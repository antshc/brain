"""`fetch-page`: fetch a Confluence page over REST and assemble its title + Markdown body in one
pass (I/O: Confluence REST via `atlassian-python-api`; ADF->Markdown in-process through
`map_markdown`; `fetch_diagrams` caches attachments and resolves placeholders).

Content that cannot be converted never aborts the fetch: it is tagged `adf:error` in place,
listed with its raw ADF in a trailing ignored `## Conversion errors` section, and reported on
stderr; the page is still written and the exit code stays 0.

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
import sys
import os
import tempfile
from pathlib import Path
from urllib.parse import parse_qs, urlparse
import re

from requests.exceptions import RequestException

from ..config import load_credentials, require_supported_library, site_url
from ..confluence_client import error_label, get_confluence
from ..converter.adf_to_md import ConversionIssue
from ..map_markdown import (
    DOC_NODE,
    adf_to_md_tolerant,
    append_conversion_issues,
    new_issue,
    report_conversion_issues,
)
from ..conversion_guard import GuardError, lint_markdown, validate_markdown
from .comments import (
    CommentRetrievalError,
    comments_note,
    fetch_comment_threads,
    render_comments_section,
)
from .fetch_diagrams import (
    AttachmentRetrievalError,
    fetch_attachment_snapshot,
    has_attachment_reference,
    has_diagram_placeholder,
    publish_attachment_cache,
    restore_diagrams,
    restore_diagrams_failed,
    restore_diagrams_skipped,
)

_ATTACHMENT_MODES = ("auto", "skip", "required")
_COMMENT_MODES = ("auto", "skip")


class PageFetchError(Exception):
    """The REST page read failed. The message names only the exception class and HTTP status,
    plus a fixed hint for 401/403/404 — never the raw text, which may carry a signed URL or
    credential."""


def extract_title_and_body(page: dict) -> tuple[str, object]:
    """REST v2 page -> (title, ADF). `atlas_doc_format.value` arrives as a JSON string; a body
    that is not valid JSON is returned as-is and tagged as a conversion error later."""
    value = page["body"]["atlas_doc_format"]["value"]
    try:
        body = json.loads(value) if isinstance(value, str) else value
    except ValueError:
        body = value
    return page["title"], body


def parse_page_reference(reference: str) -> tuple[str, str | None]:
    """Resolve a numeric id or standard Confluence page URL without a TWG call."""
    if reference.isdigit():
        return reference, None
    parsed = urlparse(reference)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError(f"{reference!r} is not a numeric page id or Confluence page URL")
    match = re.search(r"/pages/(?:edit-v2/)?(\d+)", parsed.path)
    page_id = match.group(1) if match else next(iter(parse_qs(parsed.query).get("pageId", [])), "")
    if not page_id.isdigit():
        raise ValueError(f"could not extract a page id from {reference!r}")
    return page_id, f"{parsed.scheme}://{parsed.netloc}"


def fetch_page(confluence, page_id: str) -> tuple[str, object]:
    try:
        page = confluence.get(f"/api/v2/pages/{page_id}", params={"body-format": "atlas_doc_format"})
    except RequestException as exception:
        raise PageFetchError(error_label(exception)) from None
    return extract_title_and_body(page)


def convert_adf_to_markdown(body: object) -> tuple[str, list[ConversionIssue]]:
    return adf_to_md_tolerant(body, guarded=True)


def _with_title(markdown: str, title: str) -> str:
    # a body whose own first heading already is the title needs no second `# <title>` line
    if markdown.startswith(f"# {title}\n"):
        return markdown
    return f"# {title}\n\n{markdown}" if markdown.strip() else f"# {title}\n"


def default_assets_dir(md_path: Path) -> Path:
    # keep the `.md.assets` suffix so it sorts next to `<name>.md` alphabetically
    return md_path.with_name(f"{md_path.name}.assets")


def assemble(
    title: str,
    body: object,
    page_id: str,
    confluence,
    assets_dir: str,
    attachments: str = "auto",
    issues: list[ConversionIssue] | None = None,
) -> str:
    """Title + body Markdown. Unconvertible nodes stay as in-place `adf:error` lines and are
    added to `issues`; callers finish the file with `append_conversion_issues`."""
    markdown, found = convert_adf_to_markdown(body)
    if issues is not None:
        issues.extend(found)

    if not isinstance(body, dict) or not has_attachment_reference(body):
        return _with_title(markdown, title)

    if attachments == "skip":
        if has_diagram_placeholder(markdown):
            markdown = restore_diagrams_skipped(markdown)
        return _with_title(markdown, title)

    try:
        snapshot = fetch_attachment_snapshot(confluence, page_id, body)
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


def main(argv: list[str] | None = None, *, prog: str | None = None) -> None:
    parser = argparse.ArgumentParser(
        prog=prog,
        description="Fetch a Confluence page over REST and assemble its title + Markdown body in one pass."
    )
    parser.add_argument("page", nargs="?", help="Numeric pageId or standard Confluence page URL")
    parser.add_argument("--page-id", help="Numeric Confluence pageId to fetch")
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
    if bool(args.page) == bool(args.page_id):
        parser.error("provide exactly one page reference, either positional or --page-id")
    try:
        page_id, reference_site = parse_page_reference(args.page or args.page_id)
    except ValueError as exception:
        print(f"error: {exception}", file=sys.stderr)
        raise SystemExit(2) from None

    require_supported_library()
    credentials = load_credentials(args.config)
    if credentials is None:
        print("error: .atlassian.json.user needs cloudId, email, and apiToken to fetch a page", file=sys.stderr)
        raise SystemExit(1)
    if args.site or reference_site:
        credentials = {**credentials, "site": args.site or reference_site}

    md_path = Path(args.md_path)
    assets_dir = args.assets_dir or str(default_assets_dir(md_path))

    confluence = get_confluence(credentials)
    issues: list[ConversionIssue] = []
    try:
        title, body = fetch_page(confluence, page_id)
        markdown = assemble(title, body, page_id, confluence, assets_dir, args.attachments, issues)
        markdown = append_comments(markdown, page_id, confluence, site_url(credentials), args.comments)
    except PageFetchError as exception:
        print(f"Page fetch failed: {exception}", file=sys.stderr)
        raise SystemExit(1)
    except AttachmentRetrievalError as exception:
        print(f"Attachment retrieval failed: {exception}", file=sys.stderr)
        raise SystemExit(1)

    try:
        validate_markdown(markdown, placeholders=True, media=True)
        lint_markdown(markdown)
    except (GuardError, ValueError, NotImplementedError) as exception:
        new_issue(issues, DOC_NODE, f"Markdown validation failed: {exception}")
    atomic_write_markdown(md_path, append_conversion_issues(markdown, issues))
    report_conversion_issues(issues, str(md_path))


def atomic_write_markdown(path: Path, markdown: str) -> None:
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent, prefix=f".{path.name}.", delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(markdown)
        os.replace(temporary, path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
