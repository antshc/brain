"""Inline mark parsing (pure): Markdown spans -> ADF text nodes with marks."""
from __future__ import annotations

import re

from .patterns import (
    COMMENT_CLOSE_RE,
    COMMENT_OPEN_RE,
    COMMENT_TAG_RE,
    EMOJI_STATUS_COLORS,
    EMOJI_STATUS_PATTERN,
    STATUS_PATTERN,
)

# Emphasis bodies skip backslash escapes (`(?:\\.|.)`) so an escaped delimiter such as `\*` never closes a span.
_INLINE_RE = re.compile(
    r"(?P<escape>\\[!\"#$%&'()*+,\-./:;<=>?@\[\]\\^_`{|}~])"
    r"|(?P<hard_break><br\s*/?>| {2,}\n|\\\n)"
    r"|(?P<code_delim>`+)(?P<code_txt>.+?)(?P=code_delim)(?!`)"
    r"|" + STATUS_PATTERN +
    r"|" + EMOJI_STATUS_PATTERN +
    r"|\[(?P<link_txt>(?:\\.|[^\]])*)\]\((?P<link_href>(?:\\.|[^()\s]|\([^()]*\))+)\)"
    r"|\*\*(?P<strong_txt>(?:\\.|.)+?)\*\*"
    r"|__(?P<strong_u_txt>(?:\\.|.)+?)__"
    r"|~~(?P<strike_txt>(?:\\.|.)+?)~~"
    r"|\*(?P<em_txt>(?:\\.|.)+?)\*"
    r"|_(?P<em_u_txt>(?:\\.|.)+?)_"
)


def _marked(inner: str, mark: dict) -> list[dict]:
    """Inner spans keep their own marks; the outer mark is appended to each text node."""
    nodes = _parse_inline_marks(inner)
    for node in nodes:
        if node.get("type") == "text":
            node.setdefault("marks", []).append(mark)
    return nodes


def _annotation_mark(comment_id: str) -> dict:
    return {"type": "annotation", "attrs": {"annotationType": "inlineComment", "id": comment_id}}


def _append_plain(nodes: list[dict], plain: str) -> None:
    if COMMENT_CLOSE_RE.search(plain):
        raise ValueError("stray <!-- /adf:comment --> with no matching <!-- adf:comment id=... --> before it")
    if plain:
        nodes.append({"type": "text", "text": plain})


def _comment_close_span(text: str, start: int, comment_id: str) -> tuple[int, int]:
    """Position of the close tag balancing the open tag that ended at `start` (pairs may nest)."""
    depth = 1
    for tag in COMMENT_TAG_RE.finditer(text, start):
        if tag.group("comment_id") is not None:
            depth += 1
            continue
        depth -= 1
        if depth == 0:
            return tag.start(), tag.end()
    raise ValueError(f'unterminated <!-- adf:comment id="{comment_id}" --> (no matching <!-- /adf:comment -->)')


def _parse_inline_marks(text: str) -> list[dict]:
    nodes: list[dict] = []
    pos = 0
    while pos < len(text):
        m = _INLINE_RE.search(text, pos)
        comment = COMMENT_OPEN_RE.search(text, pos)
        # The leftmost construct wins, so a code span swallows a literal tag and a comment pair
        # may wrap other marks (and vice versa).
        if comment is not None and (m is None or comment.start() < m.start()):
            _append_plain(nodes, text[pos : comment.start()])
            comment_id = comment.group("comment_id")
            close_start, close_end = _comment_close_span(text, comment.end(), comment_id)
            nodes.extend(_marked(text[comment.end() : close_start], _annotation_mark(comment_id)))
            pos = close_end
            continue
        if m is None:
            break
        _append_plain(nodes, text[pos : m.start()])
        if m.group("escape") is not None:
            nodes.append({"type": "text", "text": m.group("escape")[1:]})
        elif m.group("hard_break") is not None:
            nodes.append({"type": "hardBreak"})
        elif m.group("code_txt") is not None:
            nodes.append({"type": "text", "text": _code_text(m.group("code_txt")), "marks": [{"type": "code"}]})
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
        elif m.group("emoji_status_text") is not None:
            nodes.append(
                {
                    "type": "status",
                    "attrs": {
                        "text": m.group("emoji_status_text").strip(),
                        "color": EMOJI_STATUS_COLORS[m.group("status_emoji")],
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
    _append_plain(nodes, text[pos:])
    return nodes


def _code_text(text: str) -> str:
    text = text.replace("\n", " ")
    if text.startswith(" ") and text.endswith(" ") and text.strip():
        return text[1:-1]
    return text


def parse_inline(text: str) -> list[dict]:
    return _parse_inline_marks(text) or [{"type": "text", "text": ""}]
