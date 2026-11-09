"""Markdown -> Atlassian Document Format entrypoint (pure)."""
from __future__ import annotations

from .blocks import parse_blocks


def markdown_to_adf(markdown_text: str) -> dict:
    lines = markdown_text.splitlines()
    content = parse_blocks(lines)
    if not content:
        content = [{"type": "paragraph", "content": [{"type": "text", "text": ""}]}]
    return {"version": 1, "type": "doc", "content": content}
