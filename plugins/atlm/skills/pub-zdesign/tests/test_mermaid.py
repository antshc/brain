import os
from unittest.mock import patch

from zdesign_publisher.mermaid import extract_mermaid, render_diagrams, slugify
from zdesign_publisher.theme import LIGHT_THEME_CSS


def test_slugify_basic():
    assert slugify("Hello, World!") == "hello-world"


def test_slugify_falls_back_when_empty():
    assert slugify("***") == "diagram"


def test_extract_mermaid_replaces_fence_with_marker():
    md = "# Title\n\n```mermaid\ngraph TD; A-->B;\n```\n\nmore text\n"
    processed, diagrams = extract_mermaid(md)
    assert "```mermaid" not in processed
    assert "\x00MEDIA:0\x00" in processed
    assert len(diagrams) == 1
    assert diagrams[0]["index"] == 0
    assert diagrams[0]["code"] == "graph TD; A-->B;"
    assert diagrams[0]["name"] == "00-title"


def test_extract_mermaid_names_from_nearest_preceding_heading():
    md = (
        "# First\n\n```mermaid\ngraph TD; A-->B;\n```\n\n"
        "## Second\n\n```mermaid\ngraph TD; C-->D;\n```\n"
    )
    _, diagrams = extract_mermaid(md)
    assert diagrams[0]["name"] == "00-first"
    assert diagrams[1]["name"] == "01-second"


def test_extract_mermaid_no_diagrams():
    md = "just text, no diagrams here\n"
    processed, diagrams = extract_mermaid(md)
    assert processed == md
    assert diagrams == []


def test_render_diagrams_writes_mmd_and_invokes_mmdc(tmp_path):
    diagrams = [{"index": 0, "code": "graph TD; A-->B;", "name": "00-title"}]
    assets_dir = tmp_path / "assets"

    with patch("zdesign_publisher.mermaid.subprocess.run") as mock_run:
        render_diagrams(diagrams, str(assets_dir), background="transparent")

    assert os.path.isdir(assets_dir)
    mmd_path = assets_dir / "00-title.mmd"
    assert mmd_path.read_text() == "graph TD; A-->B;\n"

    css_path = assets_dir / "_light_theme.css"
    assert css_path.read_text() == LIGHT_THEME_CSS

    mock_run.assert_called_once()
    cmd = mock_run.call_args.args[0]
    assert cmd[:2] == ["mmdc", "-i"]
    assert cmd[2] == str(mmd_path)
    assert "-b" in cmd and cmd[cmd.index("-b") + 1] == "transparent"
    assert "--cssFile" in cmd and cmd[cmd.index("--cssFile") + 1] == str(css_path)
    assert mock_run.call_args.kwargs == {"check": True}

    assert diagrams[0]["mmd_path"] == str(mmd_path)
    assert diagrams[0]["png_path"] == str(assets_dir / "00-title.png")


def test_render_diagrams_recolors_dark_theme_hexes_in_rendered_mmd(tmp_path):
    diagrams = [{"index": 0, "code": "classDef default fill:#2a2a2a,stroke:#8b949e,color:#c9d1d9", "name": "00-title"}]
    assets_dir = tmp_path / "assets"

    with patch("zdesign_publisher.mermaid.subprocess.run"):
        render_diagrams(diagrams, str(assets_dir))

    mmd_path = assets_dir / "00-title.mmd"
    assert mmd_path.read_text() == "classDef default fill:#f6f8fa,stroke:#57606a,color:#24292f\n"
    assert diagrams[0]["filename"] == "00-title.png"
