"""`publish-page check-anchors`: offline pre-publish comparison of a fetched page's inline-comment
anchors with the edited Markdown. A shared id (one comment over several blocks) must keep all of
its spans or lose all of them; a partial removal leaves the comment attached unpredictably.

Usage:
    atl.py publish-page check-anchors --original <fetched.md> --md-path <edited.md>

Prints `{"sharedIds", "kept", "removed", "partialCommentRemovals"}`; exits 1 when
`partialCommentRemovals` is non-empty, 2 when either file fails to convert.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from ..map_markdown import ConversionError, md_to_adf
from .comment_guard import comment_block_counts, partial_removals
from .patterns import strip_ignored_sections


def _adf(path: str) -> dict:
    return md_to_adf(strip_ignored_sections(Path(path).read_text(encoding="utf-8")))


def compare(original_adf: dict, edited_adf: dict) -> dict:
    before = comment_block_counts(original_adf)
    after = comment_block_counts(edited_adf)
    return {
        "sharedIds": [{"id": anchor_id, "blocks": count} for anchor_id, count in sorted(before.items()) if count > 1],
        "kept": sorted(anchor_id for anchor_id in before if anchor_id in after),
        "removed": sorted(anchor_id for anchor_id in before if anchor_id not in after),
        "partialCommentRemovals": partial_removals(original_adf, edited_adf),
    }


def main(argv: list[str] | None = None, *, prog: str | None = None) -> int:
    parser = argparse.ArgumentParser(prog=prog, description="Compare inline-comment anchors of a fetched page and its edit. Offline.")
    parser.add_argument("--original", required=True, help="Markdown as fetched by `fetch-page`")
    parser.add_argument("--md-path", required=True, help="Edited Markdown about to be published")
    args = parser.parse_args(argv)

    try:
        report = compare(_adf(args.original), _adf(args.md_path))
    except ConversionError as exception:
        print(f"error: {exception}", file=sys.stderr)
        return 2
    json.dump(report, sys.stdout)
    sys.stdout.write("\n")
    for partial in report["partialCommentRemovals"]:
        print(
            f"warning: comment anchor {partial['id']} spanned {partial['before']} blocks, now {partial['after']}; "
            "keep or remove every span of a shared id together",
            file=sys.stderr,
        )
    return 1 if report["partialCommentRemovals"] else 0
