"""Discover installed Stack agents and the file patterns in their descriptions."""
from __future__ import annotations

import re
from pathlib import Path

_FRONTMATTER = re.compile(r"\A---\r?\n(.*?)\r?\n---(?:\r?\n|\Z)", re.DOTALL)
_DESCRIPTION = re.compile(r"^description:[ \t]*(.+)$", re.MULTILINE)
_GLOB = re.compile(r"`([^`]+)`")
_STACK_AGENT = re.compile(r"^codey-(.+)\.agent\.md$")


def parse_scope(agent_text: str) -> list[str]:
    """Extract backtick-quoted file patterns from the frontmatter description only."""
    frontmatter = _FRONTMATTER.match(agent_text)
    if not frontmatter:
        return []
    description = _DESCRIPTION.search(frontmatter.group(1))
    if not description:
        return []
    return _GLOB.findall(description.group(1))


def discover_stack_agents(agents_dir: Path) -> dict[str, list[str]]:
    """Map each installed Stack id (`py`, `dotnet`, `ai`, ...) to its declared glob scope.

    Scans `codey-<stack>.agent.md` files in `agents_dir`; `chorey.agent.md` is not a Stack.
    """
    stacks: dict[str, list[str]] = {}
    for agent_file in sorted(agents_dir.glob("codey-*.agent.md")):
        stack_match = _STACK_AGENT.match(agent_file.name)
        if not stack_match:
            continue
        scope = parse_scope(agent_file.read_text())
        if not scope:
            raise ValueError(f"Agent description has no file patterns: {agent_file}")
        stacks[stack_match.group(1)] = scope
    return stacks
