#!/usr/bin/env python3
"""Lint SKILL.md descriptions for trigger overlap and broken redirects.

Checks every skill under `plugins/wf/`:
- description is at most `MAX_DESCRIPTION_CHARS` characters;
- a quoted trigger phrase is not reused, or nearly reused, by another skill;
- every `Not for ... → \\`skill\\`` redirect names an existing skill other than itself.

Skill names for redirect targets come from every tracked skill in the repository.
"""
from __future__ import annotations

import re
import subprocess
import sys
from dataclasses import dataclass
from difflib import SequenceMatcher
from pathlib import Path

import yaml

MAX_DESCRIPTION_CHARS = 300
NEAR_DUPLICATE_RATIO = 0.85
CHECKED_ROOT = Path("plugins/wf")
IGNORED_PARTS = {"_backup", "_in-progress", "templates", "kbs"}

_QUOTED = re.compile(r"""(?<!\w)(['"])(.+?)\1(?!\w)""")
_REDIRECT = re.compile(r"→\s*`([^`]+)`")


@dataclass(frozen=True)
class Skill:
    path: Path
    name: str
    description: str


def is_skill_file(path: Path) -> bool:
    return path.name == "SKILL.md" or path.name.endswith(".SKILL.template.md")


def tracked_skill_files(repo: Path) -> list[Path]:
    names = subprocess.check_output(["git", "ls-files"], cwd=repo, text=True).splitlines()
    return [
        Path(name)
        for name in names
        if is_skill_file(Path(name)) and not IGNORED_PARTS & set(Path(name).parts)
    ]


def read_skill(repo: Path, relative: Path) -> Skill | None:
    text = (repo / relative).read_text(encoding="utf-8")
    match = re.match(r"---\n(.*?)\n---\n", text, re.DOTALL)
    if match is None:
        return None
    front = yaml.safe_load(match.group(1)) or {}
    name, description = front.get("name"), front.get("description")
    if not isinstance(name, str) or not isinstance(description, str):
        return None
    return Skill(relative, name, " ".join(description.split()))


def trigger_phrases(description: str) -> list[str]:
    return [match.group(2) for match in _QUOTED.finditer(description)]


def redirect_targets(description: str) -> list[str]:
    start = description.find("Not for")
    return _REDIRECT.findall(description[start:]) if start >= 0 else []


def normalize(phrase: str) -> str:
    return " ".join(re.sub(r"[^a-z0-9]+", " ", phrase.lower()).split())


def lint(checked: list[Skill], known_names: set[str]) -> list[str]:
    errors: list[str] = []
    seen: list[tuple[str, str, str]] = []
    for skill in checked:
        if len(skill.description) > MAX_DESCRIPTION_CHARS:
            errors.append(
                f"{skill.path}: description is {len(skill.description)} chars, max {MAX_DESCRIPTION_CHARS}"
            )
        for target in redirect_targets(skill.description):
            if target == skill.name:
                errors.append(f"{skill.path}: 'Not for' redirects to itself")
            elif target not in known_names:
                errors.append(f"{skill.path}: 'Not for' target `{target}` is not a known skill")
        for phrase in trigger_phrases(skill.description):
            normalized = normalize(phrase)
            for other_name, other_phrase, other_normalized in seen:
                if other_name == skill.name:
                    continue
                if SequenceMatcher(None, normalized, other_normalized).ratio() >= NEAR_DUPLICATE_RATIO:
                    errors.append(
                        f"{skill.path}: trigger '{phrase}' duplicates '{other_phrase}' in `{other_name}`"
                    )
            seen.append((skill.name, phrase, normalized))
    return errors


def main(repo: Path = Path.cwd()) -> int:
    skills = [
        skill
        for relative in tracked_skill_files(repo)
        if (skill := read_skill(repo, relative)) is not None
    ]
    checked = [skill for skill in skills if skill.path.is_relative_to(CHECKED_ROOT)]
    errors = lint(checked, {skill.name for skill in skills})
    for error in errors:
        print(error, file=sys.stderr)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
