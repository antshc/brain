"""CLI orchestration: wires the env/mermaid/attachments/adf seams together and talks to
Confluence. Kept thin — its own logic (arg parsing, page-id resolution, verification) is
the only thing tested here; the pipeline steps it calls are tested in their own modules.
"""
from __future__ import annotations

import argparse
import json
import os
import re

from atlassian import Confluence

from .adf import build_adf_doc, wire_media_ids
from .attachments import upload_diagrams
from .env import get_confluence, load_env
from .mermaid import extract_mermaid, render_diagrams
from .patterns import strip_ignored_sections


def resolve_page_id(confluence: Confluence, page_id: str | None, space_key: str | None, title: str | None) -> str:
    if page_id:
        return page_id
    if not space_key or not title:
        raise SystemExit("Provide --page-id, or both --space-key and --title to create a new page.")
    page = confluence.create_page(space_key, title, "", representation="storage")
    return page["id"]


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Publish a zdesign Markdown file to Confluence as an ADF page.")
    parser.add_argument("--md", required=True, help="Path to the zdesign markdown file")
    parser.add_argument("--page-id", help="Confluence pageId to update")
    parser.add_argument("--space-key", help="Space key, only used when creating a new page")
    parser.add_argument("--title", help="Page title; also used when creating a new page")
    parser.add_argument("--env", default=".env/.atlmcp.env", help="Path to the Atlassian credentials env file")
    parser.add_argument("--mermaid-bg", default="white", help="mmdc background color (default: white)")
    parser.add_argument("--image-width", type=int, default=768, help="Rendered diagram width in px (default: 768)")
    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    md_path = os.path.abspath(args.md)
    if not os.path.isfile(md_path):
        raise SystemExit(f"Markdown file not found: {md_path}")

    title = args.title
    if not title:
        with open(md_path) as f:
            first_line = f.readline().strip()
        title = re.sub(r"^#+\s*", "", first_line) or os.path.splitext(os.path.basename(md_path))[0]

    env = load_env(args.env)
    confluence = get_confluence(env)
    page_id = resolve_page_id(confluence, args.page_id, args.space_key, title)

    with open(md_path) as f:
        md_text = f.read()

    md_text = strip_ignored_sections(md_text)
    processed_md, diagrams = extract_mermaid(md_text)

    md_stem = os.path.splitext(os.path.basename(md_path))[0]
    assets_dir = os.path.join(os.path.dirname(md_path), f"{md_stem}.artifacts")
    render_diagrams(diagrams, assets_dir, background=args.mermaid_bg)

    filename_to_file_id = upload_diagrams(confluence, page_id, diagrams)
    file_ids_by_index = wire_media_ids(diagrams, filename_to_file_id)

    adf_doc = build_adf_doc(processed_md, file_ids_by_index, image_width=args.image_width)
    body = json.dumps(adf_doc)

    confluence.update_page(
        page_id=page_id,
        title=title,
        body=body,
        representation="atlas_doc_format",
        always_update=True,
    )

    # Verify: re-fetch and confirm every diagram's fileId appears in the published body.
    page = confluence.get(f"/rest/api/content/{page_id}", params={"expand": "body.atlas_doc_format,version,_links"})
    published_body = page["body"]["atlas_doc_format"]["value"]
    for d in diagrams:
        file_id = filename_to_file_id[d["filename"]]
        if file_id not in published_body:
            raise RuntimeError(f"media id for {d['filename']!r} missing from published body")

    base_url = env["ACLI_SITE"]
    if not re.match(r"^https?://", base_url):
        base_url = "https://" + base_url
    webui = page.get("_links", {}).get("webui", "")
    print(f"page_id={page_id}")
    print(f"version={page['version']['number']}")
    print(f"url={base_url}{webui}")
    print(f"diagrams={[d['filename'] for d in diagrams]}")
