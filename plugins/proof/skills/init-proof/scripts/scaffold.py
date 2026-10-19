#!/usr/bin/env python3
"""Scaffold the proof kit (mole engine, app seams, verify-mole skill) into a pnpm repository.

Deterministic copy and render. Never overwrites an existing file: it is reported as skipped.

Surface markers in templates keep a section only when its expression holds for the chosen surfaces:
  TypeScript  // <surface: api>  ...  // </surface: api>      (own lines)
  Markdown    <!-- surface: web+api -->  ...  <!-- /surface: web+api -->   (own lines or inline)
Expressions: web, api, web+api (all listed chosen), web-only, api-only (exactly that surface).
Markers do not nest.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
TEMPLATES = SKILL_DIR / "templates"

KNOWN_SURFACES = ("web", "api")

# Template folder -> target folder inside the repository.
TREES = {
    "engine": "proof/engine",
    "app": "proof",
    "verify-mole": ".github/skills/verify-mole",
}
# Files that exist only when their surface is chosen.
SURFACE_FILES = {
    "proof/features/surfaces/web.ts": "web",
    "proof/features/surfaces/api.ts": "api",
}
# Template names that differ from their target, so no nested SKILL.md inside this plugin is mistaken for a skill.
RENAMES = {
    ".github/skills/verify-mole/verify-mole.SKILL.template.md": ".github/skills/verify-mole/SKILL.md",
}
# Engine files are copied byte for byte; everything else is rendered.
VERBATIM_TREES = {"engine"}

SCRIPTS = {
    "mole": "tsx proof/engine/mole.ts",
    "prove": "tsx proof/engine/prove-cli.ts",
    "test:proof": "tsx --test proof/features.test.ts",
    "typecheck:proof": "tsc -p proof/tsconfig.json",
}
DEV_DEPENDENCIES = ("tsx", "@playwright/test", "@types/node", "typescript")
GITIGNORE_LINE = "/proof/.runs/"

_EXPR = r"([a-z]+(?:\+[a-z]+)*(?:-only)?)"
_TS_BLOCK = re.compile(rf"^[ \t]*// <surface: {_EXPR}>[ \t]*\n(.*?)^[ \t]*// </surface: \1>[ \t]*\n", re.S | re.M)
_MD_BLOCK = re.compile(rf"^[ \t]*<!-- surface: {_EXPR} -->[ \t]*\n(.*?)^[ \t]*<!-- /surface: \1 -->[ \t]*\n", re.S | re.M)
_MD_INLINE = re.compile(rf"<!-- surface: {_EXPR} -->(.*?)<!-- /surface: \1 -->", re.S)
_LEFTOVER = re.compile(r"<surface:|</surface:|<!-- /?surface:|\{\{[A-Z_]+\}\}")


class ScaffoldError(Exception):
    pass


def parse_surfaces(value: str) -> list[str]:
    """`web`, `api`, `both` or a comma list -> canonical ordered list."""
    names: set[str] = set()
    for part in value.replace(" ", "").lower().split(","):
        if part == "both":
            names.update(KNOWN_SURFACES)
        elif part in KNOWN_SURFACES:
            names.add(part)
        elif part:
            raise ScaffoldError(f"Unknown surface '{part}'. Use web, api or both.")
    if not names:
        raise ScaffoldError("Choose at least one surface: web, api or both.")
    return [name for name in KNOWN_SURFACES if name in names]


def is_pnpm_repo(repo: Path) -> bool:
    package = repo / "package.json"
    if not package.is_file():
        return False
    if (repo / "pnpm-lock.yaml").is_file() or (repo / "pnpm-workspace.yaml").is_file():
        return True
    try:
        manager = json.loads(package.read_text()).get("packageManager", "")
    except json.JSONDecodeError:
        return False
    return isinstance(manager, str) and manager.startswith("pnpm@")


def _active(expression: str, surfaces: list[str]) -> bool:
    chosen = set(surfaces)
    if expression.endswith("-only"):
        only = expression[: -len("-only")]
        if only not in KNOWN_SURFACES:
            raise ScaffoldError(f"Unknown surface marker '{expression}'")
        return chosen == {only}
    parts = expression.split("+")
    for part in parts:
        if part not in KNOWN_SURFACES:
            raise ScaffoldError(f"Unknown surface marker '{expression}'")
    return all(part in chosen for part in parts)


def render(text: str, surfaces: list[str], app_name: str) -> str:
    """Drop sections whose surface is not chosen, strip the markers, fill the placeholders."""

    def block(match: re.Match[str]) -> str:
        return match.group(2) if _active(match.group(1), surfaces) else ""

    def inline(match: re.Match[str]) -> str:
        return match.group(2) if _active(match.group(1), surfaces) else ""

    text = _TS_BLOCK.sub(block, text)
    text = _MD_BLOCK.sub(block, text)
    text = _MD_INLINE.sub(inline, text)
    values = {
        "{{APP_NAME_JSON}}": json.dumps(app_name),
        "{{APP_NAME}}": app_name,
        "{{SURFACES_LIST}}": ", ".join(json.dumps(name) for name in surfaces),
        "{{SURFACES_TEXT}}": ", ".join(surfaces),
        "{{SURFACES_YAML}}": "\n".join(f"  - {name}" for name in surfaces),
    }
    for key, value in values.items():
        text = text.replace(key, value)
    leftover = _LEFTOVER.search(text)
    if leftover:
        raise ScaffoldError(f"Unresolved template marker or placeholder: {leftover.group(0)!r}")
    return text


def _copy_tree(repo: Path, surfaces: list[str], app_name: str, created: list[str], skipped: list[str]) -> None:
    for tree, target_root in TREES.items():
        source_root = TEMPLATES / tree
        for source in sorted(p for p in source_root.rglob("*") if p.is_file()):
            relative = f"{target_root}/{source.relative_to(source_root).as_posix()}"
            relative = RENAMES.get(relative, relative)
            gate = SURFACE_FILES.get(relative)
            if gate and gate not in surfaces:
                continue
            target = repo / relative
            if target.exists():
                skipped.append(relative)
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            if tree in VERBATIM_TREES:
                shutil.copyfile(source, target)
            else:
                target.write_text(render(source.read_text(), surfaces, app_name))
            created.append(relative)


def _indent_of(raw: str) -> int | str:
    match = re.search(r"^([ \t]+)\S", raw, re.M)
    if not match:
        return 2
    return match.group(1) if "\t" in match.group(1) else len(match.group(1))


def _update_package(repo: Path) -> tuple[list[str], list[str], list[str]]:
    """Add scripts that are missing. Returns (scripts added, scripts conflicting, devDependencies missing)."""
    path = repo / "package.json"
    raw = path.read_text()
    data = json.loads(raw)
    scripts = data.setdefault("scripts", {})
    added: list[str] = []
    conflicts: list[str] = []
    for name, command in SCRIPTS.items():
        if name not in scripts:
            scripts[name] = command
            added.append(name)
        elif scripts[name] != command:
            conflicts.append(name)
    if added:
        path.write_text(json.dumps(data, indent=_indent_of(raw), ensure_ascii=False) + ("\n" if raw.endswith("\n") else ""))
    declared = {**data.get("dependencies", {}), **data.get("devDependencies", {})}
    missing = [name for name in DEV_DEPENDENCIES if name not in declared]
    return added, conflicts, missing


def _pnpm(repo: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["pnpm", *args], cwd=repo, capture_output=True, text=True)


def _last_line(result: subprocess.CompletedProcess) -> str:
    lines = (result.stderr or result.stdout).strip().splitlines()
    return lines[-1] if lines else "no output"


def _install(repo: Path, packages: list[str]) -> str:
    if not packages:
        return "nothing to install"
    if shutil.which("pnpm") is None:
        return "pnpm not found on PATH"
    command = ["add", "-D", *(["-w"] if (repo / "pnpm-workspace.yaml").is_file() else []), *packages]
    result = _pnpm(repo, *command)
    output = result.stderr + result.stdout
    blocked = re.search(r"Ignored build scripts: (.+)", output)
    if result.returncode != 0 and "ERR_PNPM_IGNORED_BUILDS" in output and blocked:
        # Recent pnpm refuses install scripts until approved; tsx needs esbuild's.
        names = re.findall(r"(@?[^\s,@]+(?:/[^\s,@]+)?)@\d", blocked.group(1))
        approved = _pnpm(repo, "approve-builds", *names) if names else result
        if approved.returncode == 0:
            return f"installed (approved build scripts: {', '.join(names)})"
        return f"`pnpm {' '.join(command)}` needs build scripts approved: run `pnpm approve-builds` ({_last_line(approved)})"
    if result.returncode != 0:
        return f"`pnpm {' '.join(command)}` failed: {_last_line(result)}"
    return "installed"


def _ensure_gitignore(repo: Path) -> str:
    path = repo / ".gitignore"
    accepted = {GITIGNORE_LINE, "proof/.runs/", "/proof/.runs", "proof/.runs", "/proof/", "proof/"}
    if path.is_file():
        text = path.read_text()
        if any(line.strip() in accepted for line in text.splitlines()):
            return "present"
        path.write_text(text + ("" if text.endswith("\n") or not text else "\n") + GITIGNORE_LINE + "\n")
        return "added"
    path.write_text(GITIGNORE_LINE + "\n")
    return "created"


def scaffold(repo: Path, surfaces: list[str], app_name: str, install: bool = True) -> dict:
    repo = repo.resolve()
    if not is_pnpm_repo(repo):
        raise ScaffoldError(
            f"{repo} is not a pnpm repository (needs package.json and pnpm-lock.yaml, pnpm-workspace.yaml or packageManager: pnpm@...)."
            " Use the create-verification-skill skill for other stacks."
        )
    if not app_name.strip():
        raise ScaffoldError("The app name is empty.")
    created: list[str] = []
    skipped: list[str] = []
    _copy_tree(repo, surfaces, app_name.strip(), created, skipped)
    scripts_added, script_conflicts, missing = _update_package(repo)
    install_status = _install(repo, missing) if install else ("skipped" if missing else "nothing to install")
    return {
        "repo": str(repo),
        "surfaces": surfaces,
        "app_name": app_name.strip(),
        "created": created,
        "skipped": skipped,
        "scripts_added": scripts_added,
        "scripts_conflicting": script_conflicts,
        "dev_dependencies_missing": missing,
        "install": install_status,
        "gitignore": _ensure_gitignore(repo),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--repo", required=True, type=Path, help="Repository root (the pnpm package that gets proof/).")
    parser.add_argument("--surfaces", required=True, help="web, api, both, or a comma list.")
    parser.add_argument("--app-name", required=True, help="Name shown in receipts and the verify-mole skill.")
    parser.add_argument("--no-install", action="store_true", help="Do not run `pnpm add -D`; report the missing packages.")
    args = parser.parse_args(argv)
    try:
        result = scaffold(args.repo, parse_surfaces(args.surfaces), args.app_name, install=not args.no_install)
    except ScaffoldError as error:
        print(json.dumps({"ok": False, "error": str(error)}, indent=2), file=sys.stderr)
        return 2
    print(json.dumps({"ok": True, **result}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
