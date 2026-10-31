#!/usr/bin/env python3
"""Install the memory.del skills into Claude Code, Codex and Claude Desktop.

Claude Code and Codex read skills from a folder on this machine, so the skills are copied
there. Claude Desktop takes skills as uploaded ZIP files, so those are built for the user to
upload. memory.del drives the phone through iPhone Use; for Claude Code, which iPhone Use has
no installer for, this script also registers its MCP server and copies its two skills.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / "skills"
MARKER = ".memory-del-install"
HOSTS = ("claude-code", "codex", "claude-desktop")
SERVER = "iphone_use"
UPSTREAM_SKILLS = ("iphone-use", "iphone-use-setup")
UPSTREAM_URL = "https://github.com/HackingU0/iPhone-use"


class InstallError(Exception):
    pass


def home():
    return Path(os.environ.get("HOME") or Path.home())


def skill_names():
    return sorted(path.parent.name for path in SKILLS.glob("*/SKILL.md"))


def skills_dir(host):
    if host == "claude-code":
        return Path(os.environ.get("CLAUDE_CONFIG_DIR") or home() / ".claude") / "skills"
    return Path(os.environ.get("CODEX_HOME") or home() / ".codex") / "skills"


def desktop_dir():
    return home() / "Library/Application Support/Claude"


def detect_hosts():
    found = []
    if shutil.which("claude") or (home() / ".claude").is_dir():
        found.append("claude-code")
    if shutil.which("codex") or (home() / ".codex").is_dir():
        found.append("codex")
    if desktop_dir().is_dir():
        found.append("claude-desktop")
    return found


def copy_skill(source, destination, force=False):
    """Replace a skill folder this script installed before; never one it did not."""
    if destination.exists() and not (destination / MARKER).exists() and not force:
        raise InstallError(f"{destination} exists and was not installed by memory.del. "
                           "Move it away, or pass --force to replace it.")
    if destination.exists():
        shutil.rmtree(destination)
    shutil.copytree(source, destination, ignore=shutil.ignore_patterns(MARKER, "__pycache__", ".DS_Store"))
    (destination / MARKER).write_text(json.dumps({"source": str(source)}) + "\n")


def remove_skill(destination):
    if (destination / MARKER).exists():
        shutil.rmtree(destination)
        return True
    return False


def archive(directory, path):
    """A skill as Claude Desktop's upload takes it: the skill folder itself at the top of the ZIP."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as bundle:
        for file in sorted(directory.rglob("*")):
            if file.is_file() and file.name not in (MARKER, ".DS_Store"):
                bundle.write(file, Path(directory.name) / file.relative_to(directory))
    return path


def find_upstream(explicit):
    """Locate a clone of iPhone Use: --iphone-use, $IPHONE_USE_SRC, or a sibling of this repo."""
    candidates = [explicit, os.environ.get("IPHONE_USE_SRC"),
                  ROOT.parent / "iPhone-use", ROOT.parent / "iphone-use", home() / "iPhone-use"]
    for candidate in candidates:
        if candidate and (Path(candidate).expanduser() / "claude" / "install.py").is_file():
            return Path(candidate).expanduser().resolve()
    if explicit:
        raise InstallError(f"{explicit} is not an iPhone Use clone (claude/install.py is missing).")
    return None


def desktop_entry():
    """The iphone_use entry Claude Desktop already runs, when iPhone Use was installed there."""
    config = desktop_dir() / "claude_desktop_config.json"
    try:
        entry = json.loads(config.read_text()).get("mcpServers", {}).get(SERVER)
    except (OSError, ValueError, AttributeError):
        return None
    return entry if isinstance(entry, dict) and entry.get("command") else None


def upstream_install(upstream):
    """Run iPhone Use's own Claude installer against a private config file and return its entry.

    The installer verifies that the server starts before it writes anything, so a returned
    entry is one that has been seen to answer tools/list on this machine.
    """
    config = home() / ".local/share/memory-del/iphone-use-mcp.json"
    config.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run([sys.executable, str(upstream / "claude" / "install.py"), "--config", str(config)], check=True)
    return json.loads(config.read_text())["mcpServers"][SERVER]


def wire_claude_code(upstream_arg, force):
    """Register iPhone Use's MCP server with Claude Code and copy its skills."""
    claude = shutil.which("claude")
    if not claude:
        print("  ! `claude` CLI not found; skipped registering the iphone_use MCP server.")
        return
    registered = subprocess.run([claude, "mcp", "get", SERVER], capture_output=True).returncode == 0
    if not registered:
        entry = desktop_entry()
        if entry is None:
            upstream = find_upstream(upstream_arg)
            if upstream is None:
                print(f"  ! iPhone Use not found. Clone {UPSTREAM_URL} next to this repo, or pass\n"
                      "    --iphone-use /path/to/iPhone-use, then run this script again.")
                return
            entry = upstream_install(upstream)
        spec = {"type": "stdio", "command": entry["command"], "args": entry.get("args", []), "env": entry.get("env", {})}
        subprocess.run([claude, "mcp", "add-json", "-s", "user", SERVER, json.dumps(spec)], check=True)
        print(f"  + registered MCP server {SERVER} for Claude Code (user scope)")
    else:
        print(f"  = MCP server {SERVER} already registered in Claude Code")
    # The Claude-worded copies of iPhone Use's skills live in the installed package.
    staged = home() / ".local/share/iphone-use-claude/skills"
    for name in UPSTREAM_SKILLS:
        source, destination = staged / name, skills_dir("claude-code") / name
        if not (source / "SKILL.md").is_file():
            print(f"  ! {source} missing; install iPhone Use for Claude first (python3 claude/install.py).")
            continue
        if destination.exists() and not (destination / MARKER).exists() and not force:
            print(f"  = {destination} already present; left as is")
            continue
        copy_skill(source, destination, force)
        print(f"  + {destination}")


def install(hosts, upstream=None, skip_mcp=False, dist=None, force=False):
    names = skill_names()
    if not names:
        raise InstallError(f"No skills found under {SKILLS}.")
    for host in hosts:
        print(f"[{host}]")
        if host in ("claude-code", "codex"):
            target = skills_dir(host)
            target.mkdir(parents=True, exist_ok=True)
            for name in names:
                copy_skill(SKILLS / name, target / name, force)
                print(f"  + {target / name}")
            if host == "claude-code" and not skip_mcp:
                wire_claude_code(upstream, force)
            if host == "codex" and not skip_mcp:
                codex = shutil.which("codex")
                listed = codex and subprocess.run([codex, "mcp", "list"], capture_output=True, text=True)
                if not listed or SERVER not in listed.stdout:
                    print(f"  ! iphone_use not seen in `codex mcp list`. Install iPhone Use for Codex:\n"
                          f"    git clone {UPSTREAM_URL} && sh iPhone-use/scripts/install.sh")
        else:
            out = Path(dist or ROOT / "dist" / "skill-uploads")
            for name in names:
                print(f"  + {archive(SKILLS / name, out / f'{name}.zip')}")
            print("  Upload each ZIP in Claude > Customize > Skills > Upload skill, switch them on,\n"
                  "  and make sure iPhone Use for Claude Desktop is installed (python3 claude/install.py\n"
                  "  in the iPhone Use clone). Quit Claude (Cmd-Q) and open it again.")
    print("\nStart a new chat (or reconnect) so the host loads the skills, then say e.g.\n"
          "  「用 memory.del 帮我清理和 ta 有关的照片」")


def uninstall(hosts):
    for host in hosts:
        if host == "claude-desktop":
            print("[claude-desktop] remove the memory-del skills in Claude > Customize > Skills.")
            continue
        target = skills_dir(host)
        for name in skill_names() + list(UPSTREAM_SKILLS):
            if remove_skill(target / name):
                print(f"[{host}] - {target / name}")
    print(f"MCP registrations are left in place. Claude Code: `claude mcp remove {SERVER} -s user`.")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--hosts", help=f"comma-separated: {', '.join(HOSTS)} (default: detect)")
    parser.add_argument("--iphone-use", help="path to an iPhone Use clone, for Claude Code MCP wiring")
    parser.add_argument("--skip-mcp", action="store_true", help="only install memory.del skills")
    parser.add_argument("--dist", help="where to write Claude Desktop ZIPs (default: dist/skill-uploads)")
    parser.add_argument("--force", action="store_true", help="replace skill folders not installed by this script")
    parser.add_argument("--uninstall", action="store_true")
    args = parser.parse_args(argv)
    hosts = [host.strip() for host in args.hosts.split(",")] if args.hosts else detect_hosts()
    unknown = [host for host in hosts if host not in HOSTS]
    if unknown:
        parser.error(f"unknown host(s): {', '.join(unknown)}")
    if not hosts:
        parser.error("no host detected; pass --hosts claude-code,codex,claude-desktop")
    try:
        if args.uninstall:
            uninstall(hosts)
        else:
            install(hosts, args.iphone_use, args.skip_mcp, args.dist, args.force)
    except (InstallError, subprocess.CalledProcessError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
