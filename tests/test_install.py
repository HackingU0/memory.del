import importlib.util
import os
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("install", ROOT / "scripts" / "install.py")
install = importlib.util.module_from_spec(spec)
spec.loader.exec_module(install)
SKILLS = ("memory-del", "memory-del-im", "memory-del-photos", "memory-del-system")


class InstallTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        base = Path(self.tmp.name)
        self.claude, self.codex, self.dist = base / "claude", base / "codex", base / "dist"
        env = {"HOME": str(base), "CLAUDE_CONFIG_DIR": str(self.claude), "CODEX_HOME": str(self.codex)}
        patcher = mock.patch.dict(os.environ, env)
        patcher.start()
        self.addCleanup(patcher.stop)
        self.addCleanup(self.tmp.cleanup)

    def run_install(self, *extra):
        return install.main(["--hosts", "claude-code,codex,claude-desktop", "--skip-mcp", "--dist", str(self.dist), *extra])

    def test_installs_every_skill_for_every_host(self):
        self.assertEqual(install.skill_names(), list(SKILLS))
        self.assertEqual(self.run_install(), 0)
        for root in (self.claude, self.codex):
            for name in SKILLS:
                self.assertTrue((root / "skills" / name / "SKILL.md").is_file())
                self.assertTrue((root / "skills" / name / install.MARKER).is_file())
        for name in SKILLS:
            with zipfile.ZipFile(self.dist / f"{name}.zip") as bundle:
                self.assertIn(f"{name}/SKILL.md", bundle.namelist())
                self.assertFalse(any(install.MARKER in entry for entry in bundle.namelist()))

    def test_reinstall_replaces_its_own_copy(self):
        self.assertEqual(self.run_install(), 0)
        stale = self.claude / "skills" / "memory-del" / "stale.md"
        stale.write_text("old")
        self.assertEqual(self.run_install(), 0)
        self.assertFalse(stale.exists())

    def test_keeps_a_folder_it_did_not_install(self):
        foreign = self.claude / "skills" / "memory-del"
        foreign.mkdir(parents=True)
        (foreign / "SKILL.md").write_text("mine")
        self.assertEqual(self.run_install(), 1)
        self.assertEqual((foreign / "SKILL.md").read_text(), "mine")
        self.assertEqual(self.run_install("--force"), 0)
        self.assertNotEqual((foreign / "SKILL.md").read_text(), "mine")

    def test_uninstall_removes_only_installed_skills(self):
        self.assertEqual(self.run_install(), 0)
        other = self.codex / "skills" / "someone-else"
        other.mkdir(parents=True)
        self.assertEqual(install.main(["--hosts", "claude-code,codex", "--uninstall"]), 0)
        for root in (self.claude, self.codex):
            for name in SKILLS:
                self.assertFalse((root / "skills" / name).exists())
        self.assertTrue(other.is_dir())


if __name__ == "__main__":
    unittest.main()
