"""Inline mark parsing (pure): Markdown spans -> ADF text nodes with marks."""
from __future__ import annotations

import re

from .patterns import STATUS_PATTERN

_INLINE_RE = re.compile(
    r"`(?P<code_txt>[^`]+)`"
    r"|" + STATUS_PATTERN +
    r"|\[(?P<link_txt>[^\]]*)\]\((?P<link_href>[^)\s]+)\)"
    r"|\*\*(?P<strong_txt>.+?)\*\*"
    r"|__(?P<strong_u_txt>.+?)__"
    r"|~~(?P<strike_txt>.+?)~~"
    r"|\*(?P<em_txt>.+?)\*"
    r"|_(?P<em_u_txt>.+?)_"
)


def _marked(inner: str, mark: dict) -> list[dict]:
    """Inner spans keep their own marks; the outer mark is appended to each text node."""
    nodes = _parse_inline_marks(inner)
    for node in nodes:
        if node.get("type") == "text":
            node.setdefault("marks", []).append(mark)
    return nodes


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
        elif m.group("status_text") is not None:
            nodes.append(
                {
                    "type": "status",
                    "attrs": {
                        "text": m.group("status_text").strip(),
                        "color": (m.group("status_color") or "neutral").lower(),
                    },
                }
            )
        elif m.group("link_txt") is not None:
            href = m.group("link_href")
            link_mark = {"type": "link", "attrs": {"href": href}}
            label = m.group("link_txt")
            if label:
                nodes.extend(_marked(label, link_mark))
            else:
                nodes.append({"type": "text", "text": href, "marks": [link_mark]})
        elif m.group("strong_txt") is not None:
            nodes.extend(_marked(m.group("strong_txt"), {"type": "strong"}))
        elif m.group("strong_u_txt") is not None:
            nodes.extend(_marked(m.group("strong_u_txt"), {"type": "strong"}))
        elif m.group("strike_txt") is not None:
            nodes.extend(_marked(m.group("strike_txt"), {"type": "strike"}))
        elif m.group("em_txt") is not None:
            nodes.extend(_marked(m.group("em_txt"), {"type": "em"}))
        elif m.group("em_u_txt") is not None:
            nodes.extend(_marked(m.group("em_u_txt"), {"type": "em"}))
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
