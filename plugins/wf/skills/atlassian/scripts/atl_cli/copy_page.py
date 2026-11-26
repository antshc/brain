"""Copy one Confluence page body and attachments to another page, then verify it."""
from __future__ import annotations

import argparse
import io
import json
import re
import sys
from contextlib import redirect_stdout
from pathlib import Path

from .config import load_credentials, require_supported_library, site_url
from .confluence_client import get_confluence
from .conversion_guard import lint_markdown, validate_markdown
from .fetch_page.assemble_page import (
    ConversionIssue,
    assemble,
    atomic_write_markdown,
    fetch_page,
    parse_page_reference,
)
from .fetch_page.fetch_diagrams import AttachmentRetrievalError
from .page_diagrams.pipeline import publish
from .verify_publish import main as verify_publish

_INLINE_COMMENT_TAG_RE = re.compile(r'<!--\s*/?adf:comment(?:\s+id="[^"]*")?\s*-->')
_ANCHOR_RE = re.compile(r'<!--\s*adf:comment\s+id="[^"]+"\s*-->')


def strip_comment_anchors(markdown: str) -> str:
    """Clone body text without source-page comment identities."""
    return _INLINE_COMMENT_TAG_RE.sub("", markdown)


def _target_title(confluence, page_id: str) -> str:
    page = confluence.get(f"/api/v2/pages/{page_id}")
    title = page.get("title")
    if not isinstance(title, str) or not title:
        raise ValueError(f"target page {page_id} has no title")
    return title


def copy_page(
    *,
    source: str,
    target: str,
    config_path: str,
    work_dir: str,
    title: str | None = None,
) -> dict:
    source_id, source_site = parse_page_reference(source)
    target_id, target_site = parse_page_reference(target)
    if source_id == target_id:
        raise ValueError("source and target page must differ")

    require_supported_library()
    credentials = load_credentials(config_path)
    if credentials is None:
        raise ValueError(".atlassian.json.user needs cloudId, email, and apiToken to copy a page")

    configured_site = site_url(credentials).rstrip("/")
    if source_site and source_site.rstrip("/") != configured_site:
        raise ValueError("source page must belong to the configured Atlassian site")
    if target_site and target_site.rstrip("/") != configured_site:
        raise ValueError("target page must belong to the configured Atlassian site")

    work_path = Path(work_dir)
    source_markdown = work_path / "source.md"
    clone_markdown = work_path / "clone.md"
    assets_dir = work_path / "source.md.assets"
    verify_dir = work_path / "verify"
    publish_dir = work_path / "publish"
    work_path.mkdir(parents=True, exist_ok=True)

    confluence = get_confluence(credentials)
    source_title, source_body = fetch_page(confluence, source_id)
    issues: list[ConversionIssue] = []
    markdown = assemble(
        source_title,
        source_body,
        source_id,
        confluence,
        str(assets_dir),
        attachments="required",
        issues=issues,
    )
    if issues:
        reasons = "; ".join(issue.reason for issue in issues)
        raise ValueError(f"source conversion is not lossless: {reasons}")
    validate_markdown(markdown, placeholders=True, media=True)
    lint_markdown(markdown)
    atomic_write_markdown(source_markdown, markdown)

    clone = strip_comment_anchors(markdown)
    atomic_write_markdown(clone_markdown, clone)
    resolved_title = title or _target_title(confluence, target_id)
    output_path = publish_dir / "final-adf.json"
    publish_dir.mkdir(parents=True, exist_ok=True)
    result = publish(
        md_path=str(clone_markdown),
        config_path=config_path,
        page_id=target_id,
        space_id=None,
        title=resolved_title,
        assets_dir=str(publish_dir),
        out_path=str(output_path),
        preserve_existing_table_widths=False,
    )

    verification_output = io.StringIO()
    with redirect_stdout(verification_output):
        verification_code = verify_publish(
            [
                "--page-id",
                target_id,
                "--config",
                config_path,
                "--expect-anchors",
                str(len(_ANCHOR_RE.findall(clone))),
                "--expected-manifest",
                result["manifestPath"],
                "--verify-dir",
                str(verify_dir),
            ]
        )
    if verification_code:
        raise RuntimeError(
            f"publish verification failed with exit {verification_code}: "
            f"{verification_output.getvalue().strip()}"
        )
    return {
        **result,
        "sourcePageId": source_id,
        "targetPageId": target_id,
        "commentPolicy": "clone",
        "verified": True,
        "verification": verification_output.getvalue().strip().splitlines(),
        "workDir": str(work_path),
        "url": f"{configured_site}/wiki/pages/{target_id}",
    }


def main(argv: list[str] | None = None, *, prog: str | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog=prog,
        description="Clone a page body and required attachments to another page, then verify.",
    )
    parser.add_argument("source")
    parser.add_argument("--to-page", required=True)
    parser.add_argument("--title", help="Target title; defaults to its current title")
    parser.add_argument(
        "--comment-policy",
        choices=("clone",),
        default="clone",
        help="clone strips source-page inline comment identities",
    )
    parser.add_argument("--work-dir", help="Persistent work/verification directory")
    parser.add_argument("--config", required=True)
    args = parser.parse_args(argv)

    try:
        source_id, _ = parse_page_reference(args.source)
        target_id, _ = parse_page_reference(args.to_page)
        work_dir = args.work_dir or str(Path.cwd() / "tmp" / f"atl-copy-{source_id}-to-{target_id}")
        result = copy_page(
            source=args.source,
            target=args.to_page,
            config_path=args.config,
            work_dir=work_dir,
            title=args.title,
        )
    except (AttachmentRetrievalError, RuntimeError, ValueError, OSError) as exception:
        print(f"error: {exception}", file=sys.stderr)
        return 1
    json.dump(result, sys.stdout)
    sys.stdout.write("\n")
    return 0
