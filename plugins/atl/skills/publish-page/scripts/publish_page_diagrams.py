#!/usr/bin/env python3
"""Diagram rendering and attachment upload for `publish-page`'s token branch.

Extracts ```mermaid fenced blocks from a Markdown source, renders each to a PNG (via `mmdc`),
uploads the PNGs as Confluence attachments, and prints back the media-service fileId each needs
to be embedded in the page's ADF body -- see ../SKILL.md for the full workflow (page creation,
Markdown<->ADF conversion, and the final MCP publish call are the invoking skill's prose, not
this script).

Usage:
    python3 publish_page_diagrams.py extract < design.md > diagrams.json
    python3 publish_page_diagrams.py render-attach --assets-dir <dir> --page-id <id> \
        --root <Harness Repo Path> < diagrams.json > media_ids.json

Requires `mmdc` (@mermaid-js/mermaid-cli) on PATH and `atlassian-python-api` (see
../requirements.txt) for `render-attach`; credentials are read from `.atlassian` inside the
script -- never passed as CLI args or literals.

This file is a thin entrypoint; the pipeline lives in ./page_diagrams/, split along its seams
(patterns, theme, mermaid, attachments, env, cli) so each is unit-testable -- see ../tests/.
"""
from __future__ import annotations

from page_diagrams.cli import main

if __name__ == "__main__":
    main()
