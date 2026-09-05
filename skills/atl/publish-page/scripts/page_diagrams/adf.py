"""ADF marker substitution: swap each \\x00MEDIA:<index>\\x00 marker paragraph for a
replacement node built by a caller-supplied callback — the uploaded media node here, or
(see pipeline.py's `substitute_diagram_notes`) a "not rendered" note when no token is
configured. Pure, offline — no I/O; tested directly.
"""
from __future__ import annotations

from typing import Callable

from .patterns import MEDIA_MARKER_RE


def _marker_index(node: dict) -> str | None:
    if node.get("type") != "paragraph":
        return None
    content = node.get("content") or []
    if len(content) != 1 or content[0].get("type") != "text":
        return None
    match = MEDIA_MARKER_RE.match(content[0].get("text", ""))
    return match.group(1) if match else None


def _media_node(media_id: str, page_id: str) -> dict:
    return {
        "type": "mediaSingle",
        "attrs": {"layout": "center", "width": 768, "widthType": "pixel"},
        "content": [
            {"type": "media", "attrs": {"id": media_id, "type": "file", "collection": f"contentId-{page_id}"}}
        ],
    }


def replace_markers(adf: dict, media_ids_by_index: dict, page_id: str) -> tuple[dict, int]:
    """Replace every marker paragraph in `adf["content"]` with its uploaded media node.

    Top-level only — legacy/back-compat; prefer `substitute_media` for markers nested
    inside other content (e.g. `<details><summary>` -> `expand` nodes).

    Mutates and returns the same `adf` dict, plus the number of markers replaced.
    """
    new_content = []
    replaced = 0
    for node in adf["content"]:
        index = _marker_index(node)
        if index is not None:
            new_content.append(_media_node(media_ids_by_index[index], page_id))
            replaced += 1
        else:
            new_content.append(node)
    adf["content"] = new_content
    return adf, replaced


def _substitute_in_place(nodes: list[dict], make_replacement: Callable[[str], dict]) -> int:
    replaced = 0
    for i, node in enumerate(nodes):
        index = _marker_index(node)
        if index is not None:
            nodes[i] = make_replacement(index)
            replaced += 1
        elif isinstance(node.get("content"), list):
            replaced += _substitute_in_place(node["content"], make_replacement)
    return replaced


def _verify_no_markers(nodes: list[dict]) -> None:
    for node in nodes:
        if node.get("type") == "text":
            match = MEDIA_MARKER_RE.match(node.get("text", ""))
            if match:
                raise RuntimeError(f"leftover marker after substitution: {node['text']!r}")
        if isinstance(node.get("content"), list):
            _verify_no_markers(node["content"])


def substitute_markers(adf: dict, make_replacement: Callable[[str], dict]) -> tuple[dict, int]:
    """Replace every marker paragraph anywhere in `adf`, at any nesting depth, building
    each replacement node via `make_replacement(index)`.

    Shared traversal for `substitute_media` (uploaded media nodes) and
    `pipeline.substitute_diagram_notes` ("not rendered" notes) — both walk the same
    tree shape, so both go through this one implementation instead of two.

    Recursively walks every node with a `content` list (expand/table/list/etc.), not
    just top-level `adf["content"]`. After substitution, verifies no `\\x00MEDIA:`
    marker text remains anywhere in the tree — raises `RuntimeError` naming the leftover
    marker if one does, so a partial publish never happens silently.

    Mutates and returns the same `adf` dict, plus the number of markers replaced.
    """
    replaced = _substitute_in_place(adf["content"], make_replacement)
    _verify_no_markers(adf["content"])
    return adf, replaced


def substitute_media(adf: dict, media_ids_by_index: dict, page_id: str) -> tuple[dict, int]:
    """Replace every marker paragraph anywhere in `adf` with its uploaded media node."""
    return substitute_markers(adf, lambda index: _media_node(media_ids_by_index[index], page_id))
