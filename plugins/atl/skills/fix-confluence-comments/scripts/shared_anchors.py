#!/usr/bin/env python3
"""List every `adf:comment id` that occurs on more than one block (Markdown line) of a page
body, `adf:ignore` sections excluded. Prints `<id>\t<blocks>` per shared id; nothing when none.

Usage:
    python3 shared_anchors.py <page.md>
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

_ANCHOR_RE = re.compile(r'<!--\s*adf:comment\s+id="([A-Za-z0-9-]+)"\s*-->')
_IGNORED_RE = re.compile(r"<!-- adf:ignore:start -->.*?<!-- adf:ignore:end -->", re.DOTALL)


def shared_anchor_blocks(markdown: str) -> dict[str, int]:
    blocks: dict[str, int] = {}
    for line in _IGNORED_RE.sub("", markdown).splitlines():
        for anchor_id in dict.fromkeys(_ANCHOR_RE.findall(line)):
            blocks[anchor_id] = blocks.get(anchor_id, 0) + 1
    return {anchor_id: count for anchor_id, count in blocks.items() if count > 1}


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if len(args) != 1:
        print("usage: shared_anchors.py <page.md>", file=sys.stderr)
        return 2
    for anchor_id, count in shared_anchor_blocks(Path(args[0]).read_text(encoding="utf-8")).items():
        print(f"{anchor_id}\t{count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
