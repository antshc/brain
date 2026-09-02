"""Discover installed Stack delta agents and the file-path scope each declares."""
from __future__ import annotations

import re
from pathlib import Path

_SCOPE_LINE = re.compile(r"^\*\*Scope\*\*:\s*(.+)$", re.MULTILINE)
_GLOB = re.compile(r"`([^`]+)`")
_STACK_AGENT = re.compile(r"^codey-(.+)\.agent\.md$")


def parse_scope(agent_text: str) -> list[str]:
    """Extract the backtick-quoted glob list from a Stack agent's `**Scope**:` line."""
    match = _SCOPE_LINE.search(agent_text)
    if not match:
        return []
    return _GLOB.findall(match.group(1))


def discover_stack_agents(agents_dir: Path) -> dict[str, list[str]]:
    """Map each installed Stack id (`py`, `dotnet`, `ai`, ...) to its declared glob scope.

    Scans `codey-<stack>.agent.md` files in `agents_dir`; the base `codey.agent.md` and
    `chorey.agent.md` carry no `**Scope**:` line and are never Stacks.
    """
    stacks: dict[str, list[str]] = {}
    for agent_file in sorted(agents_dir.glob("codey-*.agent.md")):
        stack_match = _STACK_AGENT.match(agent_file.name)
        if not stack_match:
            continue
        stacks[stack_match.group(1)] = parse_scope(agent_file.read_text())
    return stacks
