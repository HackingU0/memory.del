#!/usr/bin/env python3
"""Validate the skills and manifests: frontmatter, names, description limits and relative links."""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NAME = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
LINK = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
MAX_DESCRIPTION = 1024
MAX_SKILL_LINES = 500


def frontmatter(text):
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---\n", 4)
    if end < 0:
        return None
    fields = {}
    for line in text[4:end].splitlines():
        key, _, value = line.partition(":")
        fields[key.strip()] = value.strip()
    return fields


def check_links(path, errors):
    for target in LINK.findall(path.read_text()):
        if re.match(r"^[a-z]+:", target) or target.startswith("#"):
            continue
        if not (path.parent / target.split("#")[0]).exists():
            errors.append(f"{path.relative_to(ROOT)}: broken link {target}")


def main():
    errors = []
    skills = sorted((ROOT / "skills").glob("*/SKILL.md"))
    if not skills:
        errors.append("no skills found")
    for skill in skills:
        text = skill.read_text()
        meta = frontmatter(text)
        where = skill.relative_to(ROOT)
        if meta is None:
            errors.append(f"{where}: missing frontmatter")
            continue
        name, description = meta.get("name", ""), meta.get("description", "")
        if not NAME.match(name) or len(name) > 64:
            errors.append(f"{where}: invalid name {name!r}")
        if name != skill.parent.name:
            errors.append(f"{where}: name {name!r} does not match folder {skill.parent.name!r}")
        if not description or len(description) > MAX_DESCRIPTION or "<" in description or ">" in description:
            errors.append(f"{where}: description must be 1..{MAX_DESCRIPTION} chars without angle brackets")
        if len(text.splitlines()) > MAX_SKILL_LINES:
            errors.append(f"{where}: longer than {MAX_SKILL_LINES} lines; move detail into references/")
    for path in sorted(ROOT.glob("**/*.md")):
        if ".git" not in path.parts and "dist" not in path.parts:
            check_links(path, errors)
    for manifest in (ROOT / ".claude-plugin/plugin.json", ROOT / ".claude-plugin/marketplace.json"):
        try:
            json.loads(manifest.read_text())
        except (OSError, ValueError) as error:
            errors.append(f"{manifest.relative_to(ROOT)}: {error}")
    for error in errors:
        print(error, file=sys.stderr)
    if not errors:
        print(f"{len(skills)} skills and manifests OK")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
