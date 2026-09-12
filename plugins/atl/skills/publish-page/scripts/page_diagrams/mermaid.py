"""Mermaid extraction (pure) and per-renderer diagram production (I/O: filesystem + `mmdc`
and `drawio` subprocesses).

`extract_mermaid`/`slugify` are pure and covered directly; `render_diagrams` is a thin
shell around `subprocess.run` and is tested by mocking that call. A missing `mmdc` binary
surfaces as `FileNotFoundError` — left uncaught here so the caller (`cli.py`) can name the
missing prerequisite instead of a generic failure.

Every renderer writes the `.mmd` source and runs mmdc; they differ in what they keep. `png`
keeps the image and attaches it, `drawio` throws it away and attaches an editable diagram
plus its preview instead, `mermaid` throws it away and attaches nothing — the macro carries
the source, so mmdc is only a syntax gate for the latter two.
"""
from __future__ import annotations

import html
import re
import struct
import subprocess
import sys
import tempfile
from pathlib import Path

from . import renderers
from .patterns import HEADING_RE, SUMMARY_RE, media_marker
from .theme import LIGHT_THEME_CSS, apply_light_theme

_MERMAID_FENCE_RE = re.compile(r"```mermaid\n(.*?)\n```", re.DOTALL)
_MXCELL_LABEL_RE = re.compile(r'value="([^"]*)"')
_PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


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


def _run_mmdc(mmd_path: Path, png_path: Path, css_path: Path, background: str) -> None:
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


def _validate_with_mmdc(mmd_path: Path, css_path: Path, background: str) -> None:
    """Compile and discard: a diagram that will not compile must fail here rather than land
    on the page broken."""
    with tempfile.TemporaryDirectory() as tmp:
        _run_mmdc(mmd_path, Path(tmp) / "validate.png", css_path, background)


def _run_drawio(args: list[str]) -> None:
    try:
        result = subprocess.run(["drawio", *args], capture_output=True, text=True)
    except FileNotFoundError:
        raise RuntimeError(
            "drawio not found on PATH — ATLASSIAN_DIAGRAM_RENDERER=drawio needs the Draw.io Desktop "
            "CLI; install it with `python3 scripts/install_drawio.py`"
        ) from None
    if result.returncode != 0:
        sys.stderr.write(result.stderr)
        result.check_returncode()


def _png_size(png_path: Path) -> tuple[int, int]:
    """Width and height from the PNG IHDR chunk, which starts at a fixed offset."""
    header = png_path.read_bytes()[:24]
    if header[:8] != _PNG_MAGIC:
        raise RuntimeError(f"{png_path} is not a PNG; cannot measure the diagram for the macro")
    width, height = struct.unpack(">II", header[16:24])
    return width, height


def _search_text(drawio_xml: str) -> str:
    """The diagram's node labels, flattened — all the custom content body ever carries.

    Taken from the generated mxGraph model rather than the Mermaid source so it holds the
    rendered labels, not the syntax around them.
    """
    labels = (html.unescape(value).strip() for value in _MXCELL_LABEL_RE.findall(drawio_xml))
    return " ".join(dict.fromkeys(label for label in labels if label))


def _render_png(d: dict, mmd_path: Path, assets_path: Path, css_path: Path, background: str) -> None:
    png_path = assets_path / f"{d['name']}.png"
    _run_mmdc(mmd_path, png_path, css_path, background)
    d["png_path"] = str(png_path)
    d["filename"] = f"{d['name']}.png"
    d["attachments"] = [{"path": str(png_path), "filename": d["filename"]}]


def _render_drawio(d: dict, mmd_path: Path, assets_path: Path, css_path: Path, background: str) -> None:
    _validate_with_mmdc(mmd_path, css_path, background)
    drawio_path = assets_path / f"{d['name']}.drawio"
    preview_path = assets_path / f"{d['name']}.drawio.png"
    # No --mermaid-image, so the import lands as real mxCells rather than a wrapped bitmap.
    _run_drawio(["-x", "-f", "xml", "-u", "-o", str(drawio_path), str(mmd_path)])
    _run_drawio(["-x", "-f", "png", "-o", str(preview_path), str(mmd_path)])
    d["drawio_path"] = str(drawio_path)
    d["preview_path"] = str(preview_path)
    d["diagram_name"] = drawio_path.name
    d["search"] = _search_text(drawio_path.read_text())
    d["width"], d["height"] = _png_size(preview_path)
    d["attachments"] = [
        {"path": str(drawio_path), "filename": drawio_path.name},
        {"path": str(preview_path), "filename": preview_path.name},
    ]


def render_diagrams(
    diagrams: list[dict],
    assets_dir: str,
    background: str = "white",
    renderer: str = renderers.DEFAULT,
) -> None:
    """Write each diagram's `.mmd` source and produce whatever `renderer` needs from it.

    Mutates each diagram dict, adding `mmd_path` and an `attachments` list of
    `{"path", "filename"}` entries — one PNG for `png`, the editable diagram plus its
    preview for `drawio`, none for `mermaid`. `drawio` also carries the macro parameters
    the extension node needs: `diagram_name`, `search`, `width`, and `height`.
    """
    renderers.validate(renderer)

    assets_path = Path(assets_dir)
    assets_path.mkdir(parents=True, exist_ok=True)
    css_path = assets_path / "_light_theme.css"
    css_path.write_text(LIGHT_THEME_CSS)
    for d in diagrams:
        mmd_path = assets_path / f"{d['name']}.mmd"
        mmd_path.write_text(apply_light_theme(d["code"]) + "\n")
        d["mmd_path"] = str(mmd_path)
        if renderer == renderers.MERMAID:
            _validate_with_mmdc(mmd_path, css_path, background)
            d["attachments"] = []
        elif renderer == renderers.DRAWIO:
            _render_drawio(d, mmd_path, assets_path, css_path, background)
        else:
            _render_png(d, mmd_path, assets_path, css_path, background)
