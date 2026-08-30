#!/usr/bin/env python3
"""Publish a zdesign Markdown file to Confluence as an ADF page.

Renders every ```mermaid fenced block to a PNG (via `mmdc`), uploads the PNGs as page
attachments, and embeds them as ADF `mediaSingle`/`media` nodes. Every run re-renders,
re-uploads, and updates the same Confluence page (version bump) -- see
../references/adf-mapping.md for the node mapping and the media-node id quirk.

Usage:
    python3 publish_zdesign.py --md <path/to/design.md> --page-id <confluence pageId>
                                [--env .env/.atlmcp.env] [--mermaid-bg white]

Credentials are read directly from the env file (never passed on the command line or
printed). Requires `mmdc` (@mermaid-js/mermaid-cli) on PATH and `atlassian-python-api`
(see ../requirements.txt).

This file is a thin entrypoint; the pipeline itself lives in ./zdesign_publisher/,
split along its seams (env, mermaid, attachments, inline, blocks, adf, cli) so each can
be unit tested independently -- see ../tests/.
"""
from __future__ import annotations

from zdesign_publisher.cli import main

if __name__ == "__main__":
    main()
