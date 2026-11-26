"""Markdown -> Atlassian Document Format entrypoint (pure)."""
from __future__ import annotations

from .blocks import parse_blocks


def markdown_to_adf(
    markdown_text: str,
    *,
    table_metadata: dict[int, frozenset[str]] | None = None,
    width_warnings: list[str] | None = None,
) -> dict:
    lines = markdown_text.splitlines()
    metadata = table_metadata if table_metadata is not None else {}
    content = parse_blocks(lines, table_metadata=metadata, width_warnings=width_warnings)
    if not content:
        content = [{"type": "paragraph", "content": [{"type": "text", "text": ""}]}]
    return {"version": 1, "type": "doc", "content": content}
