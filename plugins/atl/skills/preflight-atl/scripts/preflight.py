#!/usr/bin/env python3
"""Resolve Atlassian Preflight facts and print them as JSON.

Usage:
    python3 preflight.py --root <Harness Repo Path>

Offline only: bounded config search + parsing + the six-field shape. `mcpConnected` and
site-less instance-identifier discovery need a live MCP call — see ../SKILL.md.

This file is a thin entrypoint; the implementation lives in ./preflight_atl/, split along
its seams (config, resolve, cli) so each is unit-testable without network access — see
../tests/.
"""
from __future__ import annotations

from preflight_atl.cli import main

if __name__ == "__main__":
    main()
