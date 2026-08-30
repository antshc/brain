#!/usr/bin/env python3
"""One-command publish pipeline for `publish-page`: extract -> convert -> create/attach ->
substitute -> publish, over the `run` subcommand (see ./page_diagrams/pipeline.py). Forces
a REST publish whenever mermaid diagrams are present, since attachment upload needs
`atlassian-python-api` regardless of body size; falls back to an MCP handback for small,
diagram-free bodies or when no `ATLASSIAN_API_TOKEN` is configured -- see ../SKILL.md for
the full workflow.

Usage:
    python3 publish_page_diagrams.py run --md-path design.md --page-id <id> \
        --root <Harness Repo Path> --out final_adf.json

Requires `mmdc` (@mermaid-js/mermaid-cli) on PATH and `atlassian-python-api` (see
../requirements.txt) whenever a REST publish is needed; credentials are read from
`.atlassian` inside the script -- never passed as CLI args or literals.

This file is a thin entrypoint; the pipeline lives in ./page_diagrams/, split along its seams
(patterns, theme, mermaid, attachments, env, adf, rest_publish, pipeline, cli) so each is
unit-testable -- see ../tests/.
"""
from __future__ import annotations

from page_diagrams.cli import main

if __name__ == "__main__":
    main()
