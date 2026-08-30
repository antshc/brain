"""CLI orchestration: the diagram source -> image -> attachment-payload test seam for
`publish-page`'s token branch. Kept thin — its own logic (action dispatch, error framing) is
what's tested here; the pipeline steps it calls are tested in their own modules. Page creation,
Markdown<->ADF conversion, and the final MCP publish call are the invoking skill's job (prose,
not this script) — see ../../SKILL.md.
"""
from __future__ import annotations

import argparse
import json
import sys

from .adf import replace_markers, substitute_media
from .env import get_confluence, load_credentials
from .mermaid import extract_mermaid, render_diagrams
from .attachments import upload_diagrams
from .patterns import strip_ignored_sections
from .rest_publish import adf_body_size, create_page_adf, get_page_version, update_page_adf

DEFAULT_THRESHOLD_BYTES = 200_000


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Diagram rendering and attachment upload for publish-page.")
    sub = parser.add_subparsers(dest="action", required=True)

    sub.add_parser("extract", help="Extract mermaid fences from Markdown (stdin) into markers. Pure, offline.")

    render = sub.add_parser(
        "render-attach",
        help="Render each diagram (stdin: {\"diagrams\": [...]} from `extract`) to PNG and upload it as a "
        "Confluence attachment. Requires `mmdc` on PATH and a configured `.atlassian` token.",
    )
    render.add_argument("--assets-dir", required=True, help="Directory to write rendered .mmd/.png files into")
    render.add_argument("--page-id", required=True, help="Confluence pageId to attach the rendered images to")
    render.add_argument("--root", required=True, help="Harness Repo Path to bound the `.atlassian` search to")
    render.add_argument("--mermaid-bg", default="white", help="mmdc background color (default: white)")
    render.add_argument(
        "--out",
        help="Write {\"mediaIdsByIndex\": ...} to this file instead of stdout, keeping stdout "
        "clean of any subprocess logging leakage. Omit to keep the current stdout-print behavior.",
    )

    replace = sub.add_parser(
        "replace-markers",
        help="Replace \\x00MEDIA:<index>\\x00 marker paragraphs in an ADF document (stdin: "
        "{\"adf\": ..., \"mediaIdsByIndex\": {...}}) with their uploaded media nodes. Top-level "
        "only — legacy/back-compat. Pure, offline.",
    )
    replace.add_argument("--page-id", required=True, help="Confluence pageId the media belongs to")

    substitute = sub.add_parser(
        "substitute-media",
        help="Replace \\x00MEDIA:<index>\\x00 marker paragraphs anywhere in an ADF document, at "
        "any nesting depth (stdin: {\"adf\": ..., \"mediaIdsByIndex\": {...}}), then verify no "
        "marker remains. Pure, offline.",
    )
    substitute.add_argument("--page-id", required=True, help="Confluence pageId the media belongs to")

    publish = sub.add_parser(
        "publish-adf",
        help="Auto-detect ADF body size (stdin: {\"adf\": ...}) and either publish it directly via "
        "REST v2 (when over threshold) or signal back to use the MCP publish call (when under it).",
    )
    publish.add_argument("--page-id", help="Confluence pageId to update (update path)")
    publish.add_argument("--space-id", help="Confluence spaceId to create the page in (create path)")
    publish.add_argument("--title", help="Page title (create path, or update path when the title changed)")
    publish.add_argument("--root", help="Harness Repo Path to bound the `.atlassian` search to")
    publish.add_argument(
        "--threshold-bytes",
        type=int,
        default=DEFAULT_THRESHOLD_BYTES,
        help=f"ADF byte-size threshold above which REST publish is used instead of MCP (default: "
        f"{DEFAULT_THRESHOLD_BYTES})",
    )

    return parser


def _run_extract() -> None:
    md_text = sys.stdin.read()
    try:
        md_text = strip_ignored_sections(md_text)
    except ValueError as e:
        print(f"error: {e}", file=sys.stderr)
        raise SystemExit(1)
    processed, diagrams = extract_mermaid(md_text)
    json.dump({"processedMarkdown": processed, "diagrams": diagrams}, sys.stdout)
    sys.stdout.write("\n")


def _write_media_ids_by_index(result: dict, out_path: str | None) -> None:
    if out_path:
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(result, f)
            f.write("\n")
    else:
        json.dump(result, sys.stdout)
        sys.stdout.write("\n")


def _run_render_attach(args: argparse.Namespace) -> None:
    payload = json.loads(sys.stdin.read())
    diagrams = payload["diagrams"]

    if not diagrams:
        _write_media_ids_by_index({"mediaIdsByIndex": {}}, args.out)
        return

    try:
        render_diagrams(diagrams, args.assets_dir, background=args.mermaid_bg)
    except FileNotFoundError:
        print(
            "error: mmdc not found on PATH — install @mermaid-js/mermaid-cli "
            "(npm install -g @mermaid-js/mermaid-cli)",
            file=sys.stderr,
        )
        raise SystemExit(1)

    credentials = load_credentials(args.root)
    confluence = get_confluence(credentials)
    filename_to_file_id = upload_diagrams(confluence, args.page_id, diagrams)

    media_ids_by_index = {str(d["index"]): filename_to_file_id[d["filename"]] for d in diagrams}
    _write_media_ids_by_index({"mediaIdsByIndex": media_ids_by_index}, args.out)


def _run_replace_markers(args: argparse.Namespace) -> None:
    payload = json.loads(sys.stdin.read())
    adf, replaced = replace_markers(payload["adf"], payload["mediaIdsByIndex"], args.page_id)
    json.dump({"adf": adf, "replaced": replaced}, sys.stdout)
    sys.stdout.write("\n")


def _run_substitute_media(args: argparse.Namespace) -> None:
    payload = json.loads(sys.stdin.read())
    try:
        adf, replaced = substitute_media(payload["adf"], payload["mediaIdsByIndex"], args.page_id)
    except RuntimeError as e:
        print(f"error: {e}", file=sys.stderr)
        raise SystemExit(1)
    json.dump({"adf": adf, "replaced": replaced}, sys.stdout)
    sys.stdout.write("\n")


def _run_publish_adf(args: argparse.Namespace) -> None:
    payload = json.loads(sys.stdin.read())
    adf = payload["adf"]
    size_bytes = adf_body_size(adf)

    if size_bytes <= args.threshold_bytes:
        json.dump({"method": "mcp", "sizeBytes": size_bytes, "thresholdBytes": args.threshold_bytes}, sys.stdout)
        sys.stdout.write("\n")
        return

    credentials = load_credentials(args.root)
    confluence = get_confluence(credentials)

    if args.page_id:
        version = get_page_version(confluence, args.page_id)
        update_page_adf(confluence, args.page_id, args.title, adf, version)
        page_id = args.page_id
    else:
        if not args.space_id or not args.title:
            print("error: --space-id and --title are required to create a page", file=sys.stderr)
            raise SystemExit(1)
        result = create_page_adf(confluence, args.space_id, args.title, adf)
        page_id = result["id"]

    json.dump({"method": "rest", "pageId": page_id, "sizeBytes": size_bytes}, sys.stdout)
    sys.stdout.write("\n")


def main(argv: list[str] | None = None) -> None:
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    if args.action == "extract":
        _run_extract()
    elif args.action == "render-attach":
        _run_render_attach(args)
    elif args.action == "substitute-media":
        _run_substitute_media(args)
    elif args.action == "publish-adf":
        _run_publish_adf(args)
    else:
        _run_replace_markers(args)


if __name__ == "__main__":
    main()
