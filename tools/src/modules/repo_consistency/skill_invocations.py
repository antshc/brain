"""Resolve skill calls; enforce full-load invocation wording throughout WF Markdown."""

import re
from pathlib import Path

from modules.repo_consistency.discovery import (
    find_skill_and_agent_files,
    find_skill_names,
    is_excluded,
)
from modules.repo_consistency.violation import Violation

# Non-WF callers retain legacy resolution during the scoped migration.
_INVOCATION = re.compile(r"\b(?:Run|Follow)\s+`/([a-zA-Z][a-zA-Z0-9-]*)`")

_CALL = re.compile(
    r"(?P<italic>\*)?(?P<verb>Load and follow|Run|Follow|Use|Load|Apply|Invoke)\s+"
    r"(?:the\s+)?`(?P<name>/?[\w{}:-]+)`(?P<kind>\s+(?:skill|tactic)\b)?",
    re.IGNORECASE,
)
_BARE_CALL = re.compile(r"\*(?:the\s+)?`(?P<name>[\w-]+)`\s+skill\b")
_CANONICAL = re.compile(r"\*Load and follow the `[a-z][a-z0-9{}-]*` skill to\s+\S")
_EXTERNAL = re.compile(r"<!-- skill-dependency: ([a-z][a-z0-9-]*); [^\n]+ -->")
_GUARD = re.compile(
    r"(?:never|do not|must not|ask the user to|tell the user to)\s+(?:\*\*)?$",
    re.IGNORECASE,
)


def _wf_violations(doc: Path, root: Path, known: set[str]) -> list[Violation]:
    text = doc.read_text(encoding="utf-8")
    declared = set(_EXTERNAL.findall(text))
    # Renderer instructions must bind both identity and purpose before emitting a call.
    dynamic = all(
        term in text.lower()
        for term in ("resolve", "name", "description", "never emit placeholders literally")
    )
    violations: list[Violation] = []
    for number, line in enumerate(text.splitlines(), 1):
        matches = [
            match for match in _CALL.finditer(line)
            if match["kind"] or (
                match["name"] in known | declared
                and not line[match.end():].startswith(" playbook")
            )
        ]
        spans = [(match.start(), match.end()) for match in matches]
        matches.extend(
            match for match in _BARE_CALL.finditer(line)
            if not any(start <= match.start() < end for start, end in spans)
        )
        ordered = sorted(matches, key=lambda item: item.start())
        for index, match in enumerate(ordered):
            name = match["name"].lstrip("/")
            if _GUARD.search(line[:match.start()]) or line.lstrip().startswith(("description:", "name:")):
                continue
            is_dynamic = name == "skill-name" or "{{" in name
            if is_dynamic:
                if not dynamic:
                    violations.append(Violation(str(doc.relative_to(root)), f"line {number}: unresolved dynamic skill call `{name}`"))
            end = ordered[index + 1].start() if index + 1 < len(ordered) else len(line)
            remainder = line[match.start():end]
            remainder = re.sub(r"\*\*[^\n]*?\*\*", "", remainder)
            closing = re.search(r"(?<!\*)\*(?!\*)", remainder[1:]) if remainder.startswith("*") else None
            if not _CANONICAL.match(remainder) or closing is None:
                violations.append(Violation(str(doc.relative_to(root)), f"line {number}: use italic Load and follow the `{name}` skill to <task>"))
            if not is_dynamic and name not in known and name not in declared:
                violations.append(Violation(str(doc.relative_to(root)), f"line {number}: unresolved skill invocation `{name}`"))
    return violations


def find_dangling_skill_invocations(repo_root: Path) -> list[Violation]:
    """Resolve legacy calls and validate the invocation contract throughout WF Markdown."""
    known_skills = find_skill_names(repo_root)
    violations: list[Violation] = []
    wf = repo_root / "plugins/wf"
    wf_docs = sorted(
        path for path in wf.rglob("*.md")
        if not is_excluded(path.relative_to(repo_root))
    ) if wf.is_dir() else []
    for doc in wf_docs:
        violations.extend(_wf_violations(doc, repo_root, known_skills))
    for doc in find_skill_and_agent_files(repo_root):
        if doc.is_relative_to(wf):
            continue
        text = doc.read_text(encoding="utf-8")
        rel = str(doc.relative_to(repo_root))
        reported: set[str] = set()
        for match in _INVOCATION.finditer(text):
            name = match.group(1)
            if name in known_skills or name in reported:
                continue
            reported.add(name)
            violations.append(Violation(rel, f"unresolved skill invocation `/{name}`"))
    return violations
