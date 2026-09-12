import os
import struct
import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from page_diagrams.mermaid import diagram_type, extract_mermaid, render_diagrams, slugify
from page_diagrams.theme import LIGHT_THEME_CSS

_DRAWIO_XML = (
    '<mxfile><root><mxCell id="0"/>'
    '<mxCell id="1" value="Start" mermaidId="A"/>'
    '<mxCell id="2" value="Build &amp; Ship" mermaidId="B"/>'
    '<mxCell id="3" value=""/>'
    "</root></mxfile>"
)


def _png_bytes(width: int, height: int) -> bytes:
    return b"\x89PNG\r\n\x1a\n" + b"\x00\x00\x00\rIHDR" + struct.pack(">II", width, height)


def _fake_export(cmd, **kwargs):
    """Stand in for both CLIs, writing whatever the real `drawio` export would produce."""
    if cmd[0] == "drawio":
        out_path = Path(cmd[cmd.index("-o") + 1])
        if cmd[cmd.index("-f") + 1] == "png":
            out_path.write_bytes(_png_bytes(841, 571))
        else:
            out_path.write_text(_DRAWIO_XML)
    return MagicMock(returncode=0)


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


def test_extract_mermaid_two_diagrams_index_independently():
    md = "```mermaid\nA-->B\n```\n\n```mermaid\nC-->D\n```\n"
    _, diagrams = extract_mermaid(md)
    assert [d["index"] for d in diagrams] == [0, 1]


def test_extract_mermaid_names_from_diagram_id_over_heading():
    md = "# First\n\n```mermaid\n%% diagram-id: oms-system-context\nflowchart TD; A-->B;\n```\n"
    _, diagrams = extract_mermaid(md)
    assert diagrams[0]["name"] == "oms-system-context"
    assert diagrams[0]["code"] == "flowchart TD; A-->B;"


def test_extract_mermaid_diagram_id_survives_reorder():
    first = "```mermaid\n%% diagram-id: order-flow\nflowchart TD; A-->B;\n```\n"
    second = "## Other\n\n```mermaid\n%% diagram-id: order-classes\nclassDiagram\n```\n"
    _, forwards = extract_mermaid(f"# Title\n\n{first}\n{second}")
    _, backwards = extract_mermaid(f"# Retitled\n\n{second}\n{first}")
    assert {d["name"] for d in forwards} == {d["name"] for d in backwards}


def test_extract_mermaid_diagram_id_after_frontmatter():
    code = "---\nconfig:\n  c4:\n    c4ShapePadding: 20\n---\n%% diagram-id: oms-context\nC4Context"
    _, diagrams = extract_mermaid(f"```mermaid\n{code}\n```\n")
    assert diagrams[0]["name"] == "oms-context"
    assert diagrams[0]["code"].endswith("---\nC4Context")


def test_extract_mermaid_diagram_id_after_init_directive():
    code = "%%{init: {'themeVariables': {'lineColor': '#8b949e'}}}%%\n%% diagram-id: order-flow\nflowchart TD"
    _, diagrams = extract_mermaid(f"```mermaid\n{code}\n```\n")
    assert diagrams[0]["name"] == "order-flow"
    assert "diagram-id" not in diagrams[0]["code"]
    assert diagrams[0]["code"].startswith("%%{init:")


def test_extract_mermaid_rejects_duplicate_diagram_ids():
    md = (
        "```mermaid\n%% diagram-id: order-flow\nflowchart TD; A-->B;\n```\n\n"
        "```mermaid\n%% diagram-id: order-flow\nflowchart TD; C-->D;\n```\n"
    )
    with pytest.raises(ValueError, match="order-flow"):
        extract_mermaid(md)


def test_render_diagrams_keeps_diagram_id_out_of_mmd(tmp_path):
    md = "# Title\n\n```mermaid\n%% diagram-id: order-flow\ngraph TD; A-->B;\n```\n"
    _, diagrams = extract_mermaid(md)
    assets_dir = tmp_path / "assets"

    with patch("page_diagrams.mermaid.subprocess.run") as mock_run:
        mock_run.return_value.returncode = 0
        render_diagrams(diagrams, str(assets_dir))

    assert (assets_dir / "order-flow.mmd").read_text() == "graph TD; A-->B;\n"
    assert diagrams[0]["attachments"] == [
        {"path": str(assets_dir / "order-flow.png"), "filename": "order-flow.png"}
    ]


def test_render_diagrams_writes_mmd_and_invokes_mmdc(tmp_path):
    diagrams = [{"index": 0, "code": "graph TD; A-->B;", "name": "00-title"}]
    assets_dir = tmp_path / "assets"

    with patch("page_diagrams.mermaid.subprocess.run") as mock_run:
        mock_run.return_value.returncode = 0
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
    assert mock_run.call_args.kwargs == {"capture_output": True, "text": True}

    assert diagrams[0]["mmd_path"] == str(mmd_path)
    assert diagrams[0]["png_path"] == str(assets_dir / "00-title.png")
    assert diagrams[0]["attachments"] == [
        {"path": str(assets_dir / "00-title.png"), "filename": "00-title.png"}
    ]


def test_render_diagrams_recolors_dark_theme_hexes_in_rendered_mmd(tmp_path):
    diagrams = [{"index": 0, "code": "classDef default fill:#242424,stroke:#8b949e,color:#c9d1d9", "name": "00-title"}]
    assets_dir = tmp_path / "assets"

    with patch("page_diagrams.mermaid.subprocess.run") as mock_run:
        mock_run.return_value.returncode = 0
        render_diagrams(diagrams, str(assets_dir))

    mmd_path = assets_dir / "00-title.mmd"
    assert mmd_path.read_text() == "classDef default fill:#f6f8fa,stroke:#57606a,color:#24292f\n"
    assert diagrams[0]["filename"] == "00-title.png"


def test_render_diagrams_raises_file_not_found_when_mmdc_missing(tmp_path):
    diagrams = [{"index": 0, "code": "graph TD; A-->B;", "name": "00-title"}]
    assets_dir = tmp_path / "assets"

    with patch("page_diagrams.mermaid.subprocess.run", side_effect=FileNotFoundError):
        try:
            render_diagrams(diagrams, str(assets_dir))
        except FileNotFoundError:
            pass
        else:
            raise AssertionError("expected FileNotFoundError to propagate")


def test_render_diagrams_surfaces_stderr_and_raises_on_nonzero_exit(tmp_path, capsys):
    diagrams = [{"index": 0, "code": "graph TD; A-->B;", "name": "00-title"}]
    assets_dir = tmp_path / "assets"

    with patch("page_diagrams.mermaid.subprocess.run") as mock_run:
        mock_run.return_value.returncode = 1
        mock_run.return_value.stderr = "mmdc failed: boom\n"
        mock_run.return_value.check_returncode.side_effect = subprocess.CalledProcessError(1, ["mmdc"])
        with pytest.raises(subprocess.CalledProcessError):
            render_diagrams(diagrams, str(assets_dir))

    assert "mmdc failed: boom" in capsys.readouterr().err


def test_render_diagrams_mermaid_mode_writes_mmd_runs_mmdc_and_keeps_no_png(tmp_path):
    diagrams = [{"index": 0, "code": "graph TD; A-->B;", "name": "00-title"}]
    assets_dir = tmp_path / "assets"

    with patch("page_diagrams.mermaid.subprocess.run") as mock_run:
        mock_run.return_value.returncode = 0
        render_diagrams(diagrams, str(assets_dir), renderer="mermaid")

    mmd_path = assets_dir / "00-title.mmd"
    assert mmd_path.read_text() == "graph TD; A-->B;\n"
    assert not (assets_dir / "00-title.png").exists()
    mock_run.assert_called_once()

    assert diagrams[0]["mmd_path"] == str(mmd_path)
    assert diagrams[0]["attachments"] == []
    assert "png_path" not in diagrams[0]


def test_render_diagrams_mermaid_mode_fails_when_source_does_not_compile(tmp_path):
    diagrams = [{"index": 0, "code": "not a diagram", "name": "00-title"}]
    assets_dir = tmp_path / "assets"

    with patch("page_diagrams.mermaid.subprocess.run") as mock_run:
        mock_run.return_value.returncode = 1
        mock_run.return_value.stderr = "parse error\n"
        mock_run.return_value.check_returncode.side_effect = subprocess.CalledProcessError(1, ["mmdc"])
        with pytest.raises(subprocess.CalledProcessError):
            render_diagrams(diagrams, str(assets_dir), renderer="mermaid")


def test_render_diagrams_drawio_mode_writes_source_diagram_and_preview(tmp_path):
    diagrams = [{"index": 0, "code": "graph TD; A-->B;", "name": "00-title"}]
    assets_dir = tmp_path / "assets"

    with patch("page_diagrams.mermaid.subprocess.run", side_effect=_fake_export) as mock_run:
        render_diagrams(diagrams, str(assets_dir), renderer="drawio")

    assert (assets_dir / "00-title.mmd").read_text() == "graph TD; A-->B;\n"
    assert (assets_dir / "00-title.drawio").exists()
    assert (assets_dir / "00-title.drawio.png").exists()
    assert not (assets_dir / "00-title.png").exists()

    binaries = [call.args[0][0] for call in mock_run.call_args_list]
    assert binaries == ["mmdc", "drawio", "drawio"]

    xml_cmd, png_cmd = mock_run.call_args_list[1].args[0], mock_run.call_args_list[2].args[0]
    assert xml_cmd == [
        "drawio", "-x", "-f", "xml", "-u",
        "-o", str(assets_dir / "00-title.drawio"), str(assets_dir / "00-title.mmd"),
    ]
    assert png_cmd == [
        "drawio", "-x", "-f", "png",
        "-o", str(assets_dir / "00-title.drawio.png"), str(assets_dir / "00-title.mmd"),
    ]

    assert diagrams[0]["attachments"] == [
        {"path": str(assets_dir / "00-title.drawio"), "filename": "00-title.drawio"},
        {"path": str(assets_dir / "00-title.drawio.png"), "filename": "00-title.drawio.png"},
    ]
    assert diagrams[0]["diagram_name"] == "00-title.drawio"
    assert diagrams[0]["renderer"] == "drawio"


def test_render_diagrams_drawio_mode_measures_the_macro_from_the_preview_png(tmp_path):
    diagrams = [{"index": 0, "code": "graph TD; A-->B;", "name": "00-title"}]

    with patch("page_diagrams.mermaid.subprocess.run", side_effect=_fake_export):
        render_diagrams(diagrams, str(tmp_path / "assets"), renderer="drawio")

    assert (diagrams[0]["width"], diagrams[0]["height"]) == (841, 571)


def test_render_diagrams_drawio_mode_takes_search_text_from_the_diagram_labels(tmp_path):
    diagrams = [{"index": 0, "code": "graph TD; A-->B;", "name": "00-title"}]

    with patch("page_diagrams.mermaid.subprocess.run", side_effect=_fake_export):
        render_diagrams(diagrams, str(tmp_path / "assets"), renderer="drawio")

    assert diagrams[0]["search"] == "Start Build & Ship"


def test_render_diagrams_drawio_mode_fails_when_source_does_not_compile(tmp_path):
    diagrams = [{"index": 0, "code": "not a diagram", "name": "00-title"}]

    with patch("page_diagrams.mermaid.subprocess.run") as mock_run:
        mock_run.return_value.returncode = 1
        mock_run.return_value.stderr = "parse error\n"
        mock_run.return_value.check_returncode.side_effect = subprocess.CalledProcessError(1, ["mmdc"])
        with pytest.raises(subprocess.CalledProcessError):
            render_diagrams(diagrams, str(tmp_path / "assets"), renderer="drawio")

    mock_run.assert_called_once()


def test_render_diagrams_drawio_mode_names_drawio_as_the_missing_prerequisite(tmp_path):
    diagrams = [{"index": 0, "code": "graph TD; A-->B;", "name": "00-title"}]

    def missing_drawio(cmd, **kwargs):
        if cmd[0] == "drawio":
            raise FileNotFoundError
        return MagicMock(returncode=0)

    with patch("page_diagrams.mermaid.subprocess.run", side_effect=missing_drawio):
        with pytest.raises(RuntimeError, match="drawio not found on PATH"):
            render_diagrams(diagrams, str(tmp_path / "assets"), renderer="drawio")


def test_render_diagrams_rejects_unknown_renderer(tmp_path):
    diagrams = [{"index": 0, "code": "graph TD; A-->B;", "name": "00-title"}]

    with pytest.raises(ValueError, match="svg"):
        render_diagrams(diagrams, str(tmp_path / "assets"), renderer="svg")


@pytest.mark.parametrize(
    "code,expected",
    [
        ("graph TD; A-->B;", "graph"),
        ("swimlane-beta\n  lane A", "swimlane-beta"),
        ("sequenceDiagram\n  A->>B: hi", "sequenceDiagram"),
        ("%%{init: {'theme':'base'}}%%\nflowchart LR\n  A-->B", "flowchart"),
        ("---\ntitle: Hello\n---\nclassDiagram\n  A <|-- B", "classDiagram"),
        ("", ""),
    ],
)
def test_diagram_type_reads_the_keyword_past_frontmatter_and_directives(code, expected):
    assert diagram_type(code) == expected


def test_render_diagrams_drawio_mode_skips_drawio_for_an_unsupported_diagram_type(tmp_path, capsys):
    diagrams = [{"index": 0, "code": "swimlane-beta\n  lane A", "name": "00-title"}]
    assets_dir = tmp_path / "assets"

    with patch("page_diagrams.mermaid.subprocess.run", side_effect=_fake_export) as mock_run:
        render_diagrams(diagrams, str(assets_dir), renderer="drawio")

    assert [call.args[0][0] for call in mock_run.call_args_list] == ["mmdc", "mmdc"]
    assert diagrams[0]["renderer"] == "png"
    assert diagrams[0]["attachments"] == [
        {"path": str(assets_dir / "00-title.png"), "filename": "00-title.png"}
    ]
    assert "swimlane-beta" in capsys.readouterr().err


_SWIMLANE_CODE = (
    "swimlane-beta TB\n"
    "  subgraph a [A]\n"
    "    start([Start])\n"
    "    stepA[Do it]\n"
    "  end\n"
    "  start --> stepA\n"
)


def test_render_diagrams_drawio_mode_uses_the_native_swimlane_converter_when_enabled(tmp_path):
    diagrams = [{"index": 0, "code": _SWIMLANE_CODE, "name": "00-title"}]
    assets_dir = tmp_path / "assets"

    with patch("page_diagrams.mermaid.subprocess.run", side_effect=_fake_export) as mock_run:
        render_diagrams(diagrams, str(assets_dir), renderer="drawio", swimlane_drawio_enabled=True)

    assert diagrams[0]["renderer"] == "drawio"
    drawio_xml = (assets_dir / "00-title.drawio").read_text()
    assert 'style="swimlane;html=1;startSize=20;"' in drawio_xml
    assert "shape=mxgraph.flowchart.start_1" in drawio_xml
    # No XML import call — only mmdc (validation) and drawio (preview PNG export).
    assert [call.args[0][0] for call in mock_run.call_args_list] == ["mmdc", "drawio"]


def test_render_diagrams_drawio_mode_falls_back_to_png_when_native_conversion_fails(tmp_path, capsys):
    unsupported_code = "swimlane-beta LR\n  subgraph a [A]\n    start([Start])\n  end\n"
    diagrams = [{"index": 0, "code": unsupported_code, "name": "00-title"}]
    assets_dir = tmp_path / "assets"

    with patch("page_diagrams.mermaid.subprocess.run", side_effect=_fake_export):
        render_diagrams(diagrams, str(assets_dir), renderer="drawio", swimlane_drawio_enabled=True)

    assert diagrams[0]["renderer"] == "png"
    assert "swimlane-to-drawio conversion failed" in capsys.readouterr().err


def test_render_diagrams_drawio_mode_keeps_png_fallback_for_swimlane_when_toggle_is_off(tmp_path):
    diagrams = [{"index": 0, "code": _SWIMLANE_CODE, "name": "00-title"}]
    assets_dir = tmp_path / "assets"

    with patch("page_diagrams.mermaid.subprocess.run", side_effect=_fake_export):
        render_diagrams(diagrams, str(assets_dir), renderer="drawio")

    assert diagrams[0]["renderer"] == "png"


def test_render_diagrams_drawio_mode_falls_back_to_png_when_the_import_produces_no_cells(tmp_path):
    diagrams = [{"index": 0, "code": "graph TD; A-->B;", "name": "00-title"}]
    assets_dir = tmp_path / "assets"

    def empty_import(cmd, **kwargs):
        if cmd[0] == "drawio" and cmd[cmd.index("-f") + 1] == "xml":
            Path(cmd[cmd.index("-o") + 1]).write_text("<mxfile><root></root></mxfile>")
            return MagicMock(returncode=0)
        return _fake_export(cmd, **kwargs)

    with patch("page_diagrams.mermaid.subprocess.run", side_effect=empty_import):
        render_diagrams(diagrams, str(assets_dir), renderer="drawio")

    assert diagrams[0]["renderer"] == "png"
    assert diagrams[0]["filename"] == "00-title.png"


def test_render_diagrams_drawio_mode_falls_back_to_png_when_the_import_fails(tmp_path):
    diagrams = [{"index": 0, "code": "graph TD; A-->B;", "name": "00-title"}]

    def failing_import(cmd, **kwargs):
        if cmd[0] == "drawio":
            return MagicMock(
                returncode=1,
                stderr="import failed\n",
                check_returncode=MagicMock(
                    side_effect=subprocess.CalledProcessError(1, ["drawio"])
                ),
            )
        return MagicMock(returncode=0)

    with patch("page_diagrams.mermaid.subprocess.run", side_effect=failing_import):
        render_diagrams(diagrams, str(tmp_path / "assets"), renderer="drawio")

    assert diagrams[0]["renderer"] == "png"
