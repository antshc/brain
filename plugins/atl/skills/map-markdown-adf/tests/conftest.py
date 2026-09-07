"""Shared CLI-invocation fixtures — the only test seam per this skill's Verify section."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

_SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "map_markdown_adf.py"


def _run(direction: str, input_text: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(_SCRIPT), direction],
        input=input_text,
        capture_output=True,
        text=True,
    )


@pytest.fixture
def run_cli():
    return _run


@pytest.fixture
def md_to_adf():
    def _convert(markdown_text: str) -> dict:
        result = _run("md-to-adf", markdown_text)
        assert result.returncode == 0, result.stderr
        return json.loads(result.stdout)

    return _convert


@pytest.fixture
def adf_to_md():
    def _convert(doc: dict) -> str:
        result = _run("adf-to-md", json.dumps(doc))
        assert result.returncode == 0, result.stderr
        return result.stdout.rstrip("\n")

    return _convert
