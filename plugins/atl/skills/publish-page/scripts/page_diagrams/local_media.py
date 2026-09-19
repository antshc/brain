"""Local image/file attachment extraction (pure) — a second, symmetrical extraction pass
alongside `mermaid.extract_mermaid`.

`/fetch-page` writes a standalone `![alt](path)` or `[name](path)` line per local attachment
it resolves (see its "Attachment cache and rendering rules"). Left alone, `map-markdown-adf`
has no upload step for these: an image's `!` becomes literal text and a plain link's `href`
is a useless local filesystem path — nothing is ever attached. This module extracts each
standalone reference into the same `\\x00MEDIA:{i}\\x00` marker `extract_mermaid` uses, so
`pipeline.py` can upload the file and substitute a real ADF media node, exactly like a
diagram.
"""
from __future__ import annotations

import re
from pathlib import Path
from urllib.parse import unquote, urlparse

from .patterns import media_marker

# Matches a whole standalone reference line, plus an optional immediately-following
# `<!-- media-size: ... -->` comment line (written by `/fetch-page` when Confluence reported
# an image's real pixel size) — mirrors `/fetch-page`'s own one-reference-per-line output
# convention. `$`/`^` (MULTILINE) match line boundaries without consuming the newline, so a
# match with no size comment leaves surrounding blank-line structure untouched, same as
# `extract_mermaid`'s fence replacement.
_REFERENCE_RE = re.compile(
    r"^(!?)\[([^\]]*)\]\(([^)]*)\)[ \t]*$"
    r"(\n[ \t]*<!--[ \t]*media-size:[ \t]*width=(\d+)[ \t]+height=(\d+)[ \t]*-->[ \t]*$)?",
    re.MULTILINE,
)

_IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".bmp")


def _is_image(filename: str) -> bool:
    return filename.lower().endswith(_IMAGE_EXTENSIONS)


def _resolve_local_path(href: str, md_dir: Path) -> Path | None:
    """`None` for anything that isn't a plain local file reference: an external URL/scheme,
    `mailto:`, an in-page `#anchor`, or a path that doesn't exist on disk as a file."""
    if not href or href.startswith("#"):
        return None
    if urlparse(href).scheme:
        return None
    resolved = (md_dir / unquote(href)).resolve()
    return resolved if resolved.is_file() else None


def extract_local_media(md_text: str, md_dir: Path, start_index: int = 0) -> tuple[str, list[dict]]:
    """Replace each standalone local image/file reference line with a `\\x00MEDIA:{i}\\x00`
    marker, `index` continuing from `start_index` so markers never collide with a prior
    `extract_mermaid` pass on the same document.

    Returns (processed_markdown, media_items); each item is
    `{"index", "path", "filename", "is_image", "width"?, "height"?}` — `width`/`height` are
    only present for an image whose reference line is immediately followed by a
    `<!-- media-size: width=W height=H -->` comment; that comment line is always consumed
    (dropped from `processed_markdown`) once matched, regardless of whether its values end up
    used, so it never survives into the ADF as a stray paragraph.

    An inline reference mixed with other prose, an external URL/`mailto:`/`#anchor`, or a
    local path that doesn't resolve to an existing file is left completely untouched.
    """
    media_items: list[dict] = []
    index = start_index

    def _replace(match: re.Match) -> str:
        nonlocal index
        href = match.group(3)
        resolved = _resolve_local_path(href, md_dir)
        if resolved is None:
            return match.group(0)

        is_image = match.group(1) == "!" and _is_image(resolved.name)
        item: dict = {
            "index": index,
            "path": str(resolved),
            "filename": resolved.name,
            "is_image": is_image,
        }
        if is_image and match.group(4) is not None:
            item["width"] = int(match.group(5))
            item["height"] = int(match.group(6))

        media_items.append(item)
        marker = media_marker(index)
        index += 1
        return marker

    processed = _REFERENCE_RE.sub(_replace, md_text)
    return processed, media_items
