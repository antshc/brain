"""Inline mark parsing (pure): markdown spans -> ADF text nodes with marks."""
from __future__ import annotations

import re

_INLINE_RE = re.compile(
    r"`(?P<code_txt>[^`]+)`"
    r"|\[(?P<link_txt>[^\]]*)\]\((?P<link_href>[^)\s]+)\)"
    r"|\*\*(?P<strong_txt>.+?)\*\*"
    r"|~~(?P<strike_txt>.+?)~~"
    r"|\*(?P<em_txt>.+?)\*"
)


def _parse_inline_marks(text: str) -> list[dict]:
    nodes: list[dict] = []
    pos = 0
    for m in _INLINE_RE.finditer(text):
        if m.start() > pos:
            plain = text[pos : m.start()]
            if plain:
                nodes.append({"type": "text", "text": plain})
        if m.group("code_txt") is not None:
            nodes.append({"type": "text", "text": m.group("code_txt"), "marks": [{"type": "code"}]})
        elif m.group("link_txt") is not None:
            label = m.group("link_txt") or m.group("link_href")
            nodes.append(
                {"type": "text", "text": label, "marks": [{"type": "link", "attrs": {"href": m.group("link_href")}}]}
            )
        elif m.group("strong_txt") is not None:
            nodes.append({"type": "text", "text": m.group("strong_txt"), "marks": [{"type": "strong"}]})
        elif m.group("strike_txt") is not None:
            nodes.append({"type": "text", "text": m.group("strike_txt"), "marks": [{"type": "strike"}]})
        elif m.group("em_txt") is not None:
            nodes.append({"type": "text", "text": m.group("em_txt"), "marks": [{"type": "em"}]})
        pos = m.end()
    if pos < len(text):
        remainder = text[pos:]
        if remainder:
            nodes.append({"type": "text", "text": remainder})
    return nodes


def parse_inline(text: str) -> list[dict]:
    segments = re.split(r"<br\s*/?>", text)
    nodes: list[dict] = []
    for i, seg in enumerate(segments):
        if i > 0:
            nodes.append({"type": "hardBreak"})
        nodes.extend(_parse_inline_marks(seg))
    return nodes or [{"type": "text", "text": ""}]
