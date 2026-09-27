#!/usr/bin/env python3
"""Copy crew's shipped conventions without overwriting existing repository files."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

TEMPLATES = Path(__file__).resolve().parents[1] / "templates"
INSTRUCTIONS = {
    "ai": ("ai-authoring.instructions.template.md", "ai-authoring.instructions.md"),
    "dotnet": ("dotnet.instructions.template.md", "dotnet.instructions.md"),
    "py": ("python.instructions.template.md", "python.instructions.md"),
}
RULE_SKILLS = {
    "ai": "chore-ai",
    "dotnet": "chore-dotnet",
    "py": "chore-py",
}


def copy_missing(harness_repo: Path, codebase_repo: Path, stacks: list[str]) -> dict[str, list[str]]:
    created: list[str] = []
    skipped: list[str] = []
    for stack in dict.fromkeys(stacks):
        if stack not in INSTRUCTIONS:
            raise ValueError(f"Unsupported stack: {stack}")
        source, target = INSTRUCTIONS[stack]
        files = (
            (TEMPLATES / source, codebase_repo / ".github" / "instructions" / target),
            (
                TEMPLATES / f"{RULE_SKILLS[stack]}.SKILL.template.md",
                harness_repo / ".github" / "skills" / RULE_SKILLS[stack] / "SKILL.md",
            ),
        )
        for template, destination in files:
            destination.parent.mkdir(parents=True, exist_ok=True)
            if destination.exists():
                skipped.append(str(destination))
            else:
                destination.write_bytes(template.read_bytes())
                created.append(str(destination))
    for template_name, destination in (
        (
            "gotchas-memory.SKILL.template.md",
            harness_repo / ".github" / "skills" / "gotchas-memory" / "SKILL.md",
        ),
        (
            "gotchas-memory.GOTCHAS.template.md",
            harness_repo / ".github" / "skills" / "gotchas-memory" / "GOTCHAS.md",
        ),
    ):
        destination.parent.mkdir(parents=True, exist_ok=True)
        if destination.exists():
            skipped.append(str(destination))
        else:
            destination.write_bytes((TEMPLATES / template_name).read_bytes())
            created.append(str(destination))
    return {"created": created, "skipped": skipped}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--harness-repo", type=Path, required=True)
    parser.add_argument("--codebase-repo", type=Path, required=True)
    parser.add_argument("stacks", choices=tuple(INSTRUCTIONS), nargs="+")
    args = parser.parse_args()
    for path in (args.harness_repo, args.codebase_repo):
        if not path.is_dir():
            parser.error(f"Not an existing directory: {path}")
    print(json.dumps(copy_missing(args.harness_repo, args.codebase_repo, args.stacks)))


if __name__ == "__main__":
    main()
