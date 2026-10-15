"""Discovers agent/skill documents and skill names under the repo's plugin/skill trees."""

from __future__ import annotations

import re
from pathlib import Path

from modules.repo_consistency.frontmatter import parse_frontmatter

# Scanned roots only — excludes _backup/, _in-progress/, docs/kbs and other non-plugin folders.
SCAN_ROOTS = ("plugins", "skills")


def find_skill_and_agent_files(repo_root: Path) -> list[Path]:
    """Every SKILL.md and *.agent.md file under the repo's plugin/skill trees."""
    files: list[Path] = []
    for root_name in SCAN_ROOTS:
        root = repo_root / root_name
        if not root.is_dir():
            continue
        files.extend(root.rglob("SKILL.md"))
        files.extend(root.rglob("*.agent.md"))
    return sorted(files)


def find_skill_names(repo_root: Path) -> set[str]:
    """Installed skill folder names and concrete generated-skill template names."""
    names: set[str] = set()
    for root_name in SCAN_ROOTS:
        root = repo_root / root_name
        if not root.is_dir():
            continue
        for skill_md in root.rglob("SKILL.md"):
            names.add(skill_md.parent.name)
        for template in root.rglob("*.SKILL.template.md"):
            if any(part in {"_backup", "_in-progress"} for part in template.relative_to(root).parts):
                continue
            fields = parse_frontmatter(template.read_text(encoding="utf-8"))
            name = (fields or {}).get("name", "")
            if re.fullmatch(r"[a-z][a-z0-9-]*", name):
                names.add(name)
    return names

