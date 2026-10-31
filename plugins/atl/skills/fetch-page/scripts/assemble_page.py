"""Fetch a Confluence page over REST and assemble its title + Markdown body in one pass (I/O:
Confluence REST via `atlassian-python-api`, shells out to `/map-markdown-adf`'s CLI for
ADF->Markdown, then reuses this skill's own `fetch_diagrams` module for attachment caching and
placeholder resolution).

REST v2 `body-format=atlas_doc_format` returns the real ADF, annotation marks included, so every
`map-markdown-adf` construct and inline-comment anchor survives the round trip. Credentials
(`cloudId`/`email`/`apiToken`) are mandatory; `--site` overrides the configured site. Attachment
REST calls happen only when a pure, offline scan of the ADF finds a node that references an
attached file (see `fetch_diagrams.has_attachment_reference`).

`--attachments` controls what happens when a reference is present:
- `auto` (default): attempt retrieval; degrade to a note on any failure.
- `skip`: no attachment REST call at all; every placeholder becomes a "skipped" note.
- `required`: any retrieval/publish failure raises instead of degrading, and `main()` never
  writes `--md-path` in that case.

`--comments` controls the trailing `## Comments` section (see `comments.py`):
- `auto` (default): list the page's comment threads; any failure leaves a short note instead.
- `skip`: no comment lookup.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from comments import (  # noqa: E402
    CommentRetrievalError,
    comments_note,
    fetch_comment_threads,
    render_comments_section,
)
from env import get_confluence, load_credentials, site_url  # noqa: E402
from fetch_diagrams import (  # noqa: E402
    AttachmentRetrievalError,
    fetch_attachment_snapshot,
    has_attachment_reference,
    has_diagram_placeholder,
    publish_attachment_cache,
    restore_diagrams,
    restore_diagrams_failed,
    restore_diagrams_skipped,
)
from requests.exceptions import RequestException  # noqa: E402

_MAP_MARKDOWN_ADF = _SCRIPT_DIR.parents[1] / "map-markdown-adf" / "scripts" / "map_markdown_adf.py"

_ATTACHMENT_MODES = ("auto", "skip", "required")
_COMMENT_MODES = ("auto", "skip")


class ConversionError(Exception):
    """`/map-markdown-adf`'s CLI rejected the ADF body. The message is exactly its own sanitized
    stderr — never a raw `CalledProcessError` traceback.
    """


class PageFetchError(Exception):
    """The REST page read failed. The message names only the exception class — never the
    raw text, which may carry a signed URL or credential."""


def extract_title_and_body(page: dict) -> tuple[str, dict]:
    """REST v2 page -> (title, ADF). `atlas_doc_format.value` arrives as a JSON string."""
    value = page["body"]["atlas_doc_format"]["value"]
    body = json.loads(value) if isinstance(value, str) else value
    if not isinstance(body, dict):
        raise ConversionError(f"ADF body must be a JSON object, got {type(body).__name__}")
    return page["title"], body


def fetch_page(confluence, page_id: str) -> tuple[str, dict]:
    try:
        page = confluence.get(f"/api/v2/pages/{page_id}", params={"body-format": "atlas_doc_format"})
    except RequestException as exception:
        raise PageFetchError(type(exception).__name__) from None
    return extract_title_and_body(page)


def convert_adf_to_markdown(body: dict) -> str:
    result = subprocess.run(
        [sys.executable, str(_MAP_MARKDOWN_ADF), "adf-to-md"],
        input=json.dumps(body),
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise ConversionError(result.stderr.strip() or "unknown conversion failure")
    return result.stdout


def _with_title(markdown: str, title: str) -> str:
    # a body whose own first heading already is the title needs no second `# <title>` line
    if markdown.startswith(f"# {title}\n"):
        return markdown
    return f"# {title}\n\n{markdown}"


def default_assets_dir(md_path: Path) -> Path:
    # keep the `.md.assets` suffix so it sorts next to `<name>.md` alphabetically
    return md_path.with_name(f"{md_path.name}.assets")


def assemble(
    title: str, body: dict, page_id: str, confluence, assets_dir: str, attachments: str = "auto"
) -> str:
    markdown = convert_adf_to_markdown(body)

    if not has_attachment_reference(body):
        return _with_title(markdown, title)

    if attachments == "skip":
        if has_diagram_placeholder(markdown):
            markdown = restore_diagrams_skipped(markdown)
        return _with_title(markdown, title)

    try:
        snapshot = fetch_attachment_snapshot(confluence, page_id)
        publish_attachment_cache(snapshot, assets_dir)
    except AttachmentRetrievalError as exception:
        if attachments == "required":
            raise
        if has_diagram_placeholder(markdown):
            markdown = restore_diagrams_failed(markdown, str(exception))
        return _with_title(markdown, title)

    if has_diagram_placeholder(markdown):
        assets_dir_name = Path(assets_dir).name
        markdown = restore_diagrams(markdown, snapshot, assets_dir_name)
        if attachments == "required" and has_diagram_placeholder(markdown):
            raise AttachmentRetrievalError("unresolved attachment reference")
    return _with_title(markdown, title)


def append_comments(markdown: str, page_id: str, confluence, site: str, comments: str = "auto") -> str:
    if comments == "skip":
        return markdown
    try:
        threads = fetch_comment_threads(confluence, page_id)
        section = render_comments_section(threads, markdown, site)
    except CommentRetrievalError as exception:
        section = comments_note(f"comment retrieval failed ({exception})")
    if not section:
        return markdown
    return f"{markdown.rstrip()}\n\n{section}"


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="Fetch a Confluence page over REST and assemble its title + Markdown body in one pass."
    )
    parser.add_argument("--page-id", required=True, help="Numeric Confluence pageId to fetch")
    parser.add_argument("--config", required=True, help="`.atlassian.json.user` path (`configPath` from `/preflight-atlassian`)")
    parser.add_argument("--md-path", required=True, help="Path to write the assembled Markdown to")
    parser.add_argument(
        "--assets-dir",
        help="Directory to cache this page's attachments into (default: `<md-path name>.assets`)",
    )
    parser.add_argument(
        "--attachments",
        choices=_ATTACHMENT_MODES,
        default="auto",
        help=(
            "Attachment retrieval policy: auto (default) attempts retrieval and degrades safely "
            "on failure; skip performs no attachment REST call; required fails without writing "
            "--md-path when retrieval or cache publication fails"
        ),
    )
    parser.add_argument(
        "--comments",
        choices=_COMMENT_MODES,
        default="auto",
        help="Comment listing: auto (default) appends a `## Comments` section; skip lists none",
    )
    parser.add_argument("--site", help="Site URL overriding the configured `cloudId` (page URL on another site)")
    args = parser.parse_args(argv)

    credentials = load_credentials(args.config)
    if credentials is None:
        print("error: .atlassian.json.user needs cloudId, email, and apiToken to fetch a page", file=sys.stderr)
        raise SystemExit(1)
    if args.site:
        credentials = {**credentials, "site": args.site}

    md_path = Path(args.md_path)
    assets_dir = args.assets_dir or str(default_assets_dir(md_path))

    confluence = get_confluence(credentials)
    try:
        title, body = fetch_page(confluence, args.page_id)
        markdown = assemble(title, body, args.page_id, confluence, assets_dir, args.attachments)
        markdown = append_comments(markdown, args.page_id, confluence, site_url(credentials), args.comments)
    except PageFetchError as exception:
        print(f"Page fetch failed: {exception}", file=sys.stderr)
        raise SystemExit(1)
    except ConversionError as exception:
        print(f"ADF conversion failed: {exception}", file=sys.stderr)
        raise SystemExit(1)
    except AttachmentRetrievalError as exception:
        print(f"Attachment retrieval failed: {exception}", file=sys.stderr)
        raise SystemExit(1)

    md_path.write_text(markdown)


if __name__ == "__main__":
    main()
