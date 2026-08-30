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

from .adf import replace_markers
from .env import get_confluence, load_credentials
from .mermaid import extract_mermaid, render_diagrams
from .attachments import upload_diagrams


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

    replace = sub.add_parser(
        "replace-markers",
        help="Replace \\x00MEDIA:<index>\\x00 marker paragraphs in an ADF document (stdin: "
        "{\"adf\": ..., \"mediaIdsByIndex\": {...}}) with their uploaded media nodes. Pure, offline.",
    )
    replace.add_argument("--page-id", required=True, help="Confluence pageId the media belongs to")

    return parser


def _run_extract() -> None:
    md_text = sys.stdin.read()
    processed, diagrams = extract_mermaid(md_text)
    json.dump({"processedMarkdown": processed, "diagrams": diagrams}, sys.stdout)
    sys.stdout.write("\n")


def _run_render_attach(args: argparse.Namespace) -> None:
    payload = json.loads(sys.stdin.read())
    diagrams = payload["diagrams"]

    if not diagrams:
        json.dump({"mediaIdsByIndex": {}}, sys.stdout)
        sys.stdout.write("\n")
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
    json.dump({"mediaIdsByIndex": media_ids_by_index}, sys.stdout)
    sys.stdout.write("\n")


def _run_replace_markers(args: argparse.Namespace) -> None:
    payload = json.loads(sys.stdin.read())
    adf, replaced = replace_markers(payload["adf"], payload["mediaIdsByIndex"], args.page_id)
    json.dump({"adf": adf, "replaced": replaced}, sys.stdout)
    sys.stdout.write("\n")


def main(argv: list[str] | None = None) -> None:
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    if args.action == "extract":
        _run_extract()
    elif args.action == "render-attach":
        _run_render_attach(args)
    else:
        _run_replace_markers(args)


if __name__ == "__main__":
    main()
