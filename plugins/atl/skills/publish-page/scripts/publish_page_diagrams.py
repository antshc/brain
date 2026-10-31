#!/usr/bin/env python3
"""One-command publish pipeline for `publish-page`: extract -> convert -> create/attach ->
substitute -> publish, over the `run` subcommand (see ./page_diagrams/pipeline.py). Every
publish goes over Confluence REST via `atlassian-python-api`; `apiToken` is mandatory -- see
../SKILL.md for the full workflow.

Usage:
    python3 publish_page_diagrams.py run --md-path design.md --page-id <id> \
        --config <configPath> --out final_adf.json

Requires `atlassian-python-api` (installed once by ../../init-atl/requirements.txt via
/init-atl), plus `mmdc` (@mermaid-js/mermaid-cli) on PATH when diagrams are present; credentials are read from
`.atlassian.json.user` inside the script -- never passed as CLI args or literals.

This file is a thin entrypoint; the pipeline lives in ./page_diagrams/, split along its seams
(patterns, theme, mermaid, attachments, env, adf, rest_publish, pipeline, cli) so each is
unit-testable -- see tests/atl/publish-page/ at the repo root.
"""
from __future__ import annotations

from page_diagrams.cli import main

if __name__ == "__main__":
    main()
