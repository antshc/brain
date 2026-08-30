"""Mermaid extraction (pure) and PNG rendering (I/O: filesystem + `mmdc` subprocess).

`extract_mermaid`/`slugify` are pure and covered directly; `render_diagrams` is a thin
shell around `subprocess.run` and is tested by mocking that call. A missing `mmdc` binary
surfaces as `FileNotFoundError` — left uncaught here so the caller (`cli.py`) can name the
missing prerequisite instead of a generic failure.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

from .patterns import HEADING_RE, SUMMARY_RE, media_marker
from .theme import LIGHT_THEME_CSS, apply_light_theme

_MERMAID_FENCE_RE = re.compile(r"```mermaid\n(.*?)\n```", re.DOTALL)


def slugify(text: str) -> str:
    text = re.sub(r"[^\w\s-]", "", text).strip().lower()
    return re.sub(r"[\s_]+", "-", text) or "diagram"


def extract_mermaid(md_text: str) -> tuple[str, list[dict]]:
    """Replace each ```mermaid fence with a \\x00MEDIA:{i}\\x00 marker line.

    Returns (processed_markdown, diagrams) where each diagram dict has
    {"index", "code", "name"}. `name` is derived from the nearest preceding heading or,
    when the diagram sits inside a `<details><summary>` expand with no heading of its
    own, the nearest preceding `<summary>` text.
    """
    diagrams: list[dict] = []
    index = 0

    def _replace(match: re.Match) -> str:
        nonlocal index
        code = match.group(1)
        preceding = md_text[: match.start()]
        heading_text = "diagram"
        heading_pos = -1
        for hm in HEADING_RE.finditer(preceding):
            heading_text = hm.group(2)
            heading_pos = hm.start()
        for sm in SUMMARY_RE.finditer(preceding):
            if sm.start() > heading_pos:
                heading_text = sm.group(1)
        name = f"{index:02d}-{slugify(heading_text)}"
        diagrams.append({"index": index, "code": code, "name": name})
        marker = media_marker(index)
        index += 1
        return marker

    processed = _MERMAID_FENCE_RE.sub(_replace, md_text)
    return processed, diagrams


def render_diagrams(diagrams: list[dict], assets_dir: str, background: str = "white") -> None:
    assets_path = Path(assets_dir)
    assets_path.mkdir(parents=True, exist_ok=True)
    css_path = assets_path / "_light_theme.css"
    css_path.write_text(LIGHT_THEME_CSS)
    for d in diagrams:
        mmd_path = assets_path / f"{d['name']}.mmd"
        png_path = assets_path / f"{d['name']}.png"
        mmd_path.write_text(apply_light_theme(d["code"]) + "\n")
        result = subprocess.run(
            [
                "mmdc", "-i", str(mmd_path), "-o", str(png_path), "-w", "1040", "-s", "2", "-b", background,
                "--cssFile", str(css_path),
            ],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            sys.stderr.write(result.stderr)
            result.check_returncode()
        d["mmd_path"] = str(mmd_path)
        d["png_path"] = str(png_path)
        d["filename"] = f"{d['name']}.png"
