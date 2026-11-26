import copy
import json
import subprocess
from unittest.mock import MagicMock, patch

import pytest
from atlassian.errors import ApiError
from requests import HTTPError, Response
from requests.exceptions import ConnectionError as RequestsConnectionError

from atl_cli.converter.adf_to_md import adf_to_markdown
from atl_cli.page_diagrams.pipeline import (
    convert_markdown_to_adf,
    publish,
    resolve_title,
    strip_title_heading,
    substitute_diagram_notes,
)


def write_config(tmp_path, data: dict):
    (tmp_path / ".atlassian.json.user").write_text(json.dumps(data))


def _heading(level: int, text: str) -> dict:
    return {"type": "heading", "attrs": {"level": level}, "content": [{"type": "text", "text": text}]}


def _para(text: str) -> dict:
    return {"type": "paragraph", "content": [{"type": "text", "text": text}]}


def test_strip_title_heading_drops_leading_h1():
    adf = {"version": 1, "type": "doc", "content": [_heading(1, "Title"), _para("body")]}
    assert strip_title_heading(adf)["content"] == [_para("body")]


def test_strip_title_heading_keeps_non_leading_or_lower_headings():
    later_h1 = {"type": "doc", "content": [_para("intro"), _heading(1, "Section")]}
    leading_h2 = {"type": "doc", "content": [_heading(2, "Section"), _para("body")]}
    assert strip_title_heading(later_h1) == later_h1
    assert strip_title_heading(leading_h2) == leading_h2


def test_strip_title_heading_leaves_a_valid_body_when_only_the_title_remains():
    adf = {"type": "doc", "content": [_heading(1, "Title")]}
    assert strip_title_heading(adf)["content"] == [{"type": "paragraph", "content": []}]


def test_publish_does_not_include_the_title_heading_in_the_body(tmp_path):
    md_path = tmp_path / "doc.md"
    md_path.write_text("# My Page\n\nBody text.\n")
    write_config(tmp_path, {"cloudId": "example.atlassian.net", "email": "me@example.com", "apiToken": "secret"})
    out_path = tmp_path / "final.json"
    with patch("atl_cli.page_diagrams.pipeline.get_confluence", return_value=MagicMock()), patch(
        "atl_cli.page_diagrams.pipeline.create_page_adf", return_value={"id": "1"}
    ):
        result = publish(
            md_path=str(md_path),
            config_path=str(tmp_path / ".atlassian.json.user"),
            page_id=None,
            space_id="SPACE",
            title=None,
            assets_dir=str(tmp_path / "assets"),
            out_path=str(out_path),
        )
    assert result["title"] == "My Page"
    body = json.loads(out_path.read_text())["content"]
    assert [n["type"] for n in body] == ["paragraph"]


def test_resolve_title_from_first_heading():
    md = "intro text\n\n# The Title\n\nmore text\n"
    assert resolve_title(md, None) == "The Title"


def test_resolve_title_explicit_wins_over_heading():
    md = "# Heading Title\n"
    assert resolve_title(md, "Explicit Title") == "Explicit Title"


def test_resolve_title_no_heading_and_no_explicit_raises():
    with pytest.raises(ValueError, match="--title"):
        resolve_title("just text, no heading\n", None)


def test_convert_markdown_to_adf_converts_in_process():
    adf = convert_markdown_to_adf("Some **bold** text\n")

    assert adf["type"] == "doc"
    assert adf["content"][0]["content"][1]["marks"] == [{"type": "strong"}]


def test_convert_markdown_to_adf_reraises_naming_converter_on_rejection():
    with pytest.raises(RuntimeError, match="map-markdown-adf md-to-adf failed: error: .*adf:comment"):
        convert_markdown_to_adf('<!-- adf:comment id="a" -->unterminated\n')


def _marker_paragraph(index: int) -> dict:
    return {"type": "paragraph", "content": [{"type": "text", "text": f"\x00MEDIA:{index}\x00"}]}


def test_substitute_diagram_notes_replaces_top_level_marker():
    adf = {"content": [_marker_paragraph(0)]}
    diagrams = [{"index": 0, "code": "graph TD; A-->B;", "name": "00-title"}]
    result, replaced = substitute_diagram_notes(adf, diagrams)
    assert replaced == 1
    text = result["content"][0]["content"][0]["text"]
    assert "upload pending" in text
    assert "00-title" in text


def test_substitute_diagram_notes_replaces_marker_nested_inside_expand():
    adf = {
        "content": [
            {
                "type": "expand",
                "attrs": {"title": "Details"},
                "content": [_marker_paragraph(0)],
            }
        ]
    }
    diagrams = [{"index": 0, "code": "graph TD; A-->B;", "name": "00-nested"}]
    result, replaced = substitute_diagram_notes(adf, diagrams)
    assert replaced == 1
    nested = result["content"][0]["content"][0]
    assert nested["type"] == "paragraph"
    assert "upload pending" in nested["content"][0]["text"]


def _write_page(tmp_path, renderer=None, extension_key=None):
    md_path = tmp_path / "page.md"
    md_path.write_text("# Title\n\n```mermaid\ngraph TD; A-->B;\n```\n")
    config = {"cloudId": "example.atlassian.net", "email": "me@example.com", "apiToken": "secret"}
    if renderer:
        config["diagramRenderer"] = renderer
    if extension_key:
        config["drawioExtensionKey"] = extension_key
    write_config(tmp_path, config)
    return md_path


def _publish(md_path, tmp_path):
    return publish(
        md_path=str(md_path),
        config_path=str(tmp_path / ".atlassian.json.user"),
        page_id="123",
        space_id=None,
        title=None,
        assets_dir=str(tmp_path / "assets"),
        out_path=str(tmp_path / "final.json"),
    )


def _width_doc(markdown, widths):
    doc = strip_title_heading(convert_markdown_to_adf(markdown))
    tables = [node for node in doc["content"] if node["type"] == "table"]
    for table, matrix in zip(tables, widths):
        table["attrs"].update({"layout": "wide", "width": 960})
        for row, values in zip(table["content"], matrix):
            for cell, value in zip(row["content"], values):
                cell.setdefault("attrs", {}).pop("colwidth", None)
                if value is not None:
                    cell["attrs"]["colwidth"] = None if value == {} else value
    return doc


def _snapshot(doc, version=7):
    return {"version": {"number": version}, "body": {"atlas_doc_format": {"value": json.dumps(doc)}}}


def _table_widths(table):
    return [[cell.get("attrs", {}).get("colwidth", "absent") for cell in row["content"]] for row in table["content"]]


def _table_config(tmp_path, markdown):
    path = tmp_path / "page.md"
    path.write_text(markdown)
    write_config(tmp_path, {"cloudId": "example.atlassian.net", "email": "me@example.com", "apiToken": "secret"})
    return path


def test_plain_markdown_preserves_widths_by_heading_and_uses_snapshot_version(tmp_path, capsys):
    old = (
        "# Title\n\n## East\n\n| # | Priority |\n| --- | --- |\n| old-east | A |\n\n"
        "## West\n\n| # | Priority |\n| --- | --- |\n| old-west | B |\n"
    )
    live = _width_doc(old, [
        [[[155], [355]], [[155], [355]]],
        [[[45], [600]], [[45], [600]]],
    ])
    new = (
        "# Title\n\n## West\n\n| # | Priority |\n| --- | --- |\n| new-west | B |\n\n"
        "## East\n\n| # | Priority |\n| --- | --- |\n| new-east | A |\n| extra | C |\n"
    )
    md_path = _table_config(tmp_path, new)
    confluence = MagicMock()
    confluence.get.return_value = _snapshot(live)
    with patch("atl_cli.page_diagrams.pipeline.get_confluence", return_value=confluence), patch(
        "atl_cli.page_diagrams.pipeline.get_page_version"
    ) as version, patch("atl_cli.page_diagrams.pipeline.update_page_adf") as update:
        result = _publish(md_path, tmp_path)

    version.assert_not_called()
    assert update.call_args.args[4] == 7
    final = update.call_args.args[3]
    west, east = [node for node in final["content"] if node["type"] == "table"]
    assert _table_widths(west) == [[[45], [600]], [[45], [600]]]
    assert _table_widths(east) == [[[155], [355]], [[155], [355]], [[155], [355]]]
    assert west["attrs"]["width"] == east["attrs"]["width"] == 960
    assert west["attrs"]["layout"] == east["attrs"]["layout"] == "wide"
    assert json.loads((tmp_path / "final.json").read_text()) == final
    manifest = json.loads((tmp_path / "final.manifest.json").read_text())
    assert manifest == {"title": "Title", "adf": final}
    assert all(field not in json.dumps(final) for field in ("header-hash", "rows-hash", "cell-widths", "colwidths"))
    assert "tableWidthWarnings" not in result
    assert "warning:" not in capsys.readouterr().err

    from atl_cli.verify_publish import main as verify

    argv = [
        "--page-id", "123", "--config", "unused", "--expect-anchors", "0",
        "--expected-manifest", result["manifestPath"], "--verify-dir", str(tmp_path / "verify"),
    ]
    assert verify(argv, fetch=lambda *_: new, fetch_raw=lambda *_: ("Title", final)) == 0
    changed = copy.deepcopy(final)
    next(node for node in changed["content"] if node["type"] == "table")["content"][0]["content"][0]["attrs"]["colwidth"] = [999]
    assert verify(argv, fetch=lambda *_: new, fetch_raw=lambda *_: ("Title", changed)) == 1


@pytest.mark.parametrize(("marker", "expected_width", "expected_layout", "expected_columns"), [
    ('colwidths="[[240],[320]]"', 960, "wide", [[240], [320]]),
    ('colwidths="[null,null]"', 960, "wide", ["absent", "absent"]),
    ('layout="full-width" width="700"', 700, "full-width", [[155], [355]]),
    ('layout="full-width" width="700" colwidths="[[240],[320]]"', 700, "full-width", [[240], [320]]),
])
def test_explicit_markdown_width_fields_override_live_fields(tmp_path, marker, expected_width, expected_layout, expected_columns):
    plain = "# Title\n\n| # | Priority |\n| --- | --- |\n| one | two |\n"
    live = _width_doc(plain, [[[[155], [355]], [[155], [355]]]])
    md_path = _table_config(tmp_path, plain.replace("| # | Priority |", f"<!-- adf:table {marker} -->\n\n| # | Priority |"))
    confluence = MagicMock()
    confluence.get.return_value = _snapshot(live)
    with patch("atl_cli.page_diagrams.pipeline.get_confluence", return_value=confluence), patch(
        "atl_cli.page_diagrams.pipeline.get_page_version"
    ), patch("atl_cli.page_diagrams.pipeline.update_page_adf") as update:
        _publish(md_path, tmp_path)
    table = next(node for node in update.call_args.args[3]["content"] if node["type"] == "table")
    assert table["attrs"]["width"] == expected_width
    assert table["attrs"]["layout"] == expected_layout
    assert _table_widths(table) == [expected_columns, expected_columns]


def test_create_uses_explicit_widths_without_reading_a_live_page(tmp_path):
    markdown = '# Title\n\n<!-- adf:table colwidths="[[155],[355]]" -->\n\n| A | B |\n| --- | --- |\n| one | two |\n'
    md_path = _table_config(tmp_path, markdown)
    confluence = MagicMock()
    with patch("atl_cli.page_diagrams.pipeline.get_confluence", return_value=confluence), patch(
        "atl_cli.page_diagrams.pipeline.create_page_adf", return_value={"id": "456"}
    ) as create:
        result = publish(
            md_path=str(md_path), config_path=str(tmp_path / ".atlassian.json.user"), page_id=None,
            space_id="SPACE", title=None, assets_dir=str(tmp_path / "assets"), out_path=str(tmp_path / "final.json"),
        )
    confluence.get.assert_not_called()
    assert _table_widths(create.call_args.args[3]["content"][0]) == [[[155], [355]], [[155], [355]]]
    assert "tableWidthWarnings" not in result


def test_unmarked_update_respects_live_absent_widths_over_inferred_defaults(tmp_path):
    plain = "# Title\n\n| # | Priority |\n| --- | --- |\n| one | two |\n"
    live = _width_doc(plain, [[[None, None], [None, None]]])
    live["content"][0]["attrs"]["unrelated"] = "do not copy"
    live["content"][0]["content"][0]["content"][0]["attrs"]["background"] = "#ffffff"
    md_path = _table_config(tmp_path, plain)
    confluence = MagicMock()
    confluence.get.return_value = _snapshot(live)
    with patch("atl_cli.page_diagrams.pipeline.get_confluence", return_value=confluence), patch(
        "atl_cli.page_diagrams.pipeline.update_page_adf"
    ) as update:
        _publish(md_path, tmp_path)
    table = update.call_args.args[3]["content"][0]
    assert _table_widths(table) == [["absent", "absent"], ["absent", "absent"]]
    assert "unrelated" not in table["attrs"]
    assert "background" not in table["content"][0]["content"][0].get("attrs", {})


def test_sparse_row_specific_widths_and_explicit_null_are_preserved(tmp_path):
    plain = "# Title\n\n| # | Priority |\n| --- | --- |\n| one | two |\n"
    live = _width_doc(plain, [[[[155], {}], [None, [355]]]])
    md_path = _table_config(tmp_path, plain)
    confluence = MagicMock()
    confluence.get.return_value = _snapshot(live)
    with patch("atl_cli.page_diagrams.pipeline.get_confluence", return_value=confluence), patch(
        "atl_cli.page_diagrams.pipeline.update_page_adf"
    ) as update:
        _publish(md_path, tmp_path)
    table = next(node for node in update.call_args.args[3]["content"] if node["type"] == "table")
    assert _table_widths(table) == [[[155], None], ["absent", [355]]]


def test_sparse_consistent_widths_follow_changed_rows_and_new_rows(tmp_path, capsys):
    plain = "# Title\n\n| A | B |\n| --- | --- |\n| one | two |\n"
    live = _width_doc(plain, [[[[155], [355]], [None, None]]])
    md_path = _table_config(tmp_path, plain.replace("| one | two |", "| changed | two |\n| another | row |"))
    confluence = MagicMock()
    confluence.get.return_value = _snapshot(live)
    with patch("atl_cli.page_diagrams.pipeline.get_confluence", return_value=confluence), patch(
        "atl_cli.page_diagrams.pipeline.update_page_adf"
    ) as update:
        result = _publish(md_path, tmp_path)
    table = next(node for node in update.call_args.args[3]["content"] if node["type"] == "table")
    assert _table_widths(table) == [[[155], [355]], [[155], [355]], [[155], [355]]]
    assert "applied consistent column widths" in result["tableWidthWarnings"][0]
    assert result["tableWidthWarnings"][0] in capsys.readouterr().err


def test_tables_in_named_expands_match_by_context_not_position(tmp_path):
    def expand(name, value):
        return f"<details>\n<summary>{name}</summary>\n\n| A | B |\n| --- | --- |\n| {value} | two |\n</details>\n"

    old = "# Title\n\n" + expand("East", "one") + "\n" + expand("West", "three")
    live = strip_title_heading(convert_markdown_to_adf(old))
    for container, values in zip(live["content"], ([[155], [355]], [[45], [600]])):
        table = next(node for node in container["content"] if node["type"] == "table")
        for row in table["content"]:
            for cell, value in zip(row["content"], values):
                cell["attrs"] = {"colwidth": value}
    new = "# Title\n\n" + expand("West", "changed") + "\n" + expand("East", "edited")
    md_path = _table_config(tmp_path, new)
    confluence = MagicMock()
    confluence.get.return_value = _snapshot(live)
    with patch("atl_cli.page_diagrams.pipeline.get_confluence", return_value=confluence), patch(
        "atl_cli.page_diagrams.pipeline.update_page_adf"
    ) as update:
        _publish(md_path, tmp_path)
    west, east = update.call_args.args[3]["content"]
    assert _table_widths(west["content"][0]) == [[[45], [600]], [[45], [600]]]
    assert _table_widths(east["content"][0]) == [[[155], [355]], [[155], [355]]]


def test_plain_markdown_preserves_widths_in_a_blockquote(tmp_path):
    source = "# Title\n\n> | A | B |\n> | --- | --- |\n> | one | two |\n"
    live = strip_title_heading(convert_markdown_to_adf(source))
    for row in live["content"][0]["content"][0]["content"]:
        for cell, width in zip(row["content"], (155, 355)):
            cell["attrs"] = {"colwidth": [width]}
    md_path = _table_config(tmp_path, source.replace("one", "changed"))
    confluence = MagicMock()
    confluence.get.return_value = _snapshot(live)
    with patch("atl_cli.page_diagrams.pipeline.get_confluence", return_value=confluence), patch(
        "atl_cli.page_diagrams.pipeline.update_page_adf"
    ) as update:
        result = _publish(md_path, tmp_path)
    table = update.call_args.args[3]["content"][0]["content"][0]
    assert _table_widths(table) == [[[155], [355]], [[155], [355]]]
    assert "tableWidthWarnings" not in result


def test_conflicting_row_specific_widths_default_when_rows_change(tmp_path, capsys):
    plain = "# Title\n\n| # | Priority |\n| --- | --- |\n| one | two |\n"
    live = _width_doc(plain, [[[[155], [355]], [[160], [355]]]])
    md_path = _table_config(tmp_path, plain.replace("| one | two |", "| edited | two |"))
    confluence = MagicMock()
    confluence.get.return_value = _snapshot(live)
    with patch("atl_cli.page_diagrams.pipeline.get_confluence", return_value=confluence), patch(
        "atl_cli.page_diagrams.pipeline.update_page_adf"
    ) as update:
        result = _publish(md_path, tmp_path)
    table = next(node for node in update.call_args.args[3]["content"] if node["type"] == "table")
    assert _table_widths(table) == [[[60], [110]], [[60], [110]]]
    assert "row-specific widths" in result["tableWidthWarnings"][0]
    assert result["tableWidthWarnings"][0] in capsys.readouterr().err


@pytest.mark.parametrize(("old_count", "new_count"), [(2, 1), (1, 2)])
def test_ambiguous_table_matches_warn_and_keep_defaults(tmp_path, capsys, old_count, new_count):
    table = "| # | Priority |\n| --- | --- |\n| one | two |\n"
    old = "# Title\n\n" + "\n".join([table] * old_count)
    live = _width_doc(old, [[[[155], [355]], [[155], [355]]]] * old_count)
    md_path = _table_config(tmp_path, "# Title\n\n" + "\n".join([table] * new_count))
    confluence = MagicMock()
    confluence.get.return_value = _snapshot(live)
    with patch("atl_cli.page_diagrams.pipeline.get_confluence", return_value=confluence), patch(
        "atl_cli.page_diagrams.pipeline.update_page_adf"
    ) as update:
        result = _publish(md_path, tmp_path)
    tables = [node for node in update.call_args.args[3]["content"] if node["type"] == "table"]
    assert all(_table_widths(node) == [[[60], [110]], [[60], [110]]] for node in tables)
    assert len(result["tableWidthWarnings"]) == new_count
    assert all("ambiguous" in warning for warning in result["tableWidthWarnings"])
    assert "ambiguous existing table match" in capsys.readouterr().err


def test_duplicate_column_headers_warn_instead_of_guessing(tmp_path, capsys):
    plain = "# Title\n\n| A | A |\n| --- | --- |\n| one | two |\n"
    live = _width_doc(plain, [[[[155], [355]], [[155], [355]]]])
    md_path = _table_config(tmp_path, plain)
    confluence = MagicMock()
    confluence.get.return_value = _snapshot(live)
    with patch("atl_cli.page_diagrams.pipeline.get_confluence", return_value=confluence), patch(
        "atl_cli.page_diagrams.pipeline.update_page_adf"
    ) as update:
        result = _publish(md_path, tmp_path)
    table = update.call_args.args[3]["content"][0]
    assert _table_widths(table) == [["absent", "absent"], ["absent", "absent"]]
    assert "duplicate or empty column headers" in result["tableWidthWarnings"][0]
    assert result["tableWidthWarnings"][0] in capsys.readouterr().err


def test_unmatched_and_invalid_live_widths_warn_and_keep_defaults(tmp_path, capsys):
    old = "# Title\n\n| # | Priority |\n| --- | --- |\n| one | two |\n"
    live = _width_doc(old, [[[[155], [355]], [[155], [355]]]])
    live["content"][0]["content"][0]["content"][0]["attrs"]["colwidth"] = "invalid"
    md_path = _table_config(tmp_path, old)
    confluence = MagicMock()
    confluence.get.return_value = _snapshot(live)
    with patch("atl_cli.page_diagrams.pipeline.get_confluence", return_value=confluence), patch(
        "atl_cli.page_diagrams.pipeline.update_page_adf"
    ) as update:
        result = _publish(md_path, tmp_path)
        assert "invalid existing column widths" in result["tableWidthWarnings"][0]
        assert _table_widths(update.call_args.args[3]["content"][0]) == [[[60], [110]], [[60], [110]]]

        md_path.write_text(old.replace("Priority", "Other"))
        result = _publish(md_path, tmp_path)
        assert "no compatible existing table" in result["tableWidthWarnings"][0]
    assert "no compatible existing table" in capsys.readouterr().err


@pytest.mark.parametrize("attrs", [None, {}, {"level": "1"}, {"level": True}])
def test_invalid_live_heading_cannot_cause_a_width_match(tmp_path, capsys, attrs):
    plain = "# Title\n\n# Section\n\n| A | B |\n| --- | --- |\n| one | two |\n"
    live = _width_doc(plain, [[[[155], [355]], [[155], [355]]]])
    live["content"][0]["attrs"] = attrs
    md_path = _table_config(tmp_path, plain)
    confluence = MagicMock()
    confluence.get.return_value = _snapshot(live)
    with patch("atl_cli.page_diagrams.pipeline.get_confluence", return_value=confluence), patch(
        "atl_cli.page_diagrams.pipeline.update_page_adf"
    ) as update:
        result = _publish(md_path, tmp_path)
    assert _table_widths(update.call_args.args[3]["content"][1]) == [["absent", "absent"], ["absent", "absent"]]
    assert "no compatible existing table" in result["tableWidthWarnings"][0]
    assert "no compatible existing table" in capsys.readouterr().err


def test_invalid_live_row_content_cannot_cause_a_row_specific_width_match(tmp_path, capsys):
    plain = "# Title\n\n| A | B |\n| --- | --- |\n| one | two |\n"
    live = _width_doc(plain, [[[[155], [355]], [[160], [355]]]])
    live["content"][0]["content"][1]["content"][0]["content"] = ["invalid"]
    md_path = _table_config(tmp_path, plain)
    confluence = MagicMock()
    confluence.get.return_value = _snapshot(live)
    with patch("atl_cli.page_diagrams.pipeline.get_confluence", return_value=confluence), patch(
        "atl_cli.page_diagrams.pipeline.update_page_adf"
    ) as update:
        result = _publish(md_path, tmp_path)
    table = update.call_args.args[3]["content"][0]
    assert _table_widths(table) == [["absent", "absent"], ["absent", "absent"]]
    assert "row-specific widths cannot be matched safely" in result["tableWidthWarnings"][0]
    assert result["tableWidthWarnings"][0] in capsys.readouterr().err


def test_stale_explicit_column_marker_warns_and_does_not_copy_live_columns(tmp_path, capsys):
    original = "# Title\n\n| # | Priority |\n| --- | --- |\n| one | two |\n"
    saved = _width_doc(original, [[[[155], [355]], [[155], [355]]]])
    markdown = "# Title\n\n" + adf_to_markdown(saved).replace("| # | Priority |", "| Priority | # |") + "\n"
    live = _width_doc(markdown.replace(next(line for line in markdown.splitlines() if line.startswith("<!-- adf:table")), ""),
                      [[[[333], [444]], [[333], [444]]]])
    md_path = _table_config(tmp_path, markdown)
    confluence = MagicMock()
    confluence.get.return_value = _snapshot(live)
    with patch("atl_cli.page_diagrams.pipeline.get_confluence", return_value=confluence), patch(
        "atl_cli.page_diagrams.pipeline.update_page_adf"
    ) as update:
        result = _publish(md_path, tmp_path)
    table = next(node for node in update.call_args.args[3]["content"] if node["type"] == "table")
    assert _table_widths(table) == [[[110], [60]], [[110], [60]]]
    assert "column headers changed" in result["tableWidthWarnings"][0]
    assert result["tableWidthWarnings"][0] in capsys.readouterr().err


@pytest.mark.parametrize("status", [401, 403])
def test_snapshot_auth_failure_blocks_update(tmp_path, status):
    md_path = _table_config(tmp_path, "# Title\n\n| A |\n| --- |\n| one |\n")
    response = Response()
    response.status_code = status
    confluence = MagicMock()
    confluence.get.side_effect = HTTPError("secret", response=response)
    with patch("atl_cli.page_diagrams.pipeline.get_confluence", return_value=confluence), patch(
        "atl_cli.page_diagrams.pipeline.get_page_version"
    ) as version, patch("atl_cli.page_diagrams.pipeline.update_page_adf") as update:
        with pytest.raises(RuntimeError, match=f"HTTPError {status}") as error:
            _publish(md_path, tmp_path)
    assert "secret" not in str(error.value)
    update.assert_not_called()
    version.assert_not_called()


def test_unknown_auth_api_failure_blocks_update(tmp_path):
    md_path = _table_config(tmp_path, "# Title\n\n| A |\n| --- |\n| one |\n")
    confluence = MagicMock()
    confluence.get.side_effect = ApiError(reason="secret")
    with patch("atl_cli.page_diagrams.pipeline.get_confluence", return_value=confluence), patch(
        "atl_cli.page_diagrams.pipeline.update_page_adf"
    ) as update:
        with pytest.raises(RuntimeError, match="ApiError") as error:
            _publish(md_path, tmp_path)
    assert "secret" not in str(error.value)
    update.assert_not_called()


def test_non_auth_snapshot_failure_warns_and_reads_a_fresh_version(tmp_path, capsys):
    md_path = _table_config(tmp_path, "# Title\n\n| # | Priority |\n| --- | --- |\n| one | two |\n")
    confluence = MagicMock()
    confluence.get.side_effect = RequestsConnectionError("https://example.com/?token=secret")
    with patch("atl_cli.page_diagrams.pipeline.get_confluence", return_value=confluence), patch(
        "atl_cli.page_diagrams.pipeline.get_page_version", return_value=12
    ) as version, patch("atl_cli.page_diagrams.pipeline.update_page_adf") as update:
        result = _publish(md_path, tmp_path)
    version.assert_called_once_with(confluence, "123")
    assert update.call_args.args[4] == 12
    assert "ConnectionError" in result["tableWidthWarnings"][0]
    assert "secret" not in capsys.readouterr().err


def test_non_auth_http_snapshot_failure_reports_status_and_defaults(tmp_path, capsys):
    md_path = _table_config(tmp_path, "# Title\n\n| A |\n| --- |\n| one |\n")
    response = Response()
    response.status_code = 503
    confluence = MagicMock()
    confluence.get.side_effect = HTTPError("secret", response=response)
    with patch("atl_cli.page_diagrams.pipeline.get_confluence", return_value=confluence), patch(
        "atl_cli.page_diagrams.pipeline.get_page_version", return_value=12
    ), patch("atl_cli.page_diagrams.pipeline.update_page_adf") as update:
        result = _publish(md_path, tmp_path)
    assert "HTTPError 503" in result["tableWidthWarnings"][0]
    assert update.call_args.args[4] == 12
    assert "secret" not in capsys.readouterr().err


def test_cli_exposes_width_warnings_in_json_and_stderr(tmp_path, capsys):
    from atl_cli.page_diagrams.cli import main

    md_path = _table_config(tmp_path, "# Title\n\n| A |\n| --- |\n| one |\n")
    confluence = MagicMock()
    confluence.get.side_effect = RequestsConnectionError("offline")
    with patch("atl_cli.page_diagrams.pipeline.get_confluence", return_value=confluence), patch(
        "atl_cli.page_diagrams.pipeline.get_page_version", return_value=3
    ), patch("atl_cli.page_diagrams.pipeline.update_page_adf"):
        main(["run", "--md-path", str(md_path), "--page-id", "123", "--config", str(tmp_path / ".atlassian.json.user")])
    output = capsys.readouterr()
    result = json.loads(output.out)
    assert result["tableWidthWarnings"] == [
        "cannot read existing table widths (ConnectionError); using Markdown/default widths"
    ]
    assert result["tableWidthWarnings"][0] in output.err


def test_version_read_failure_after_snapshot_failure_still_blocks_update(tmp_path):
    md_path = _table_config(tmp_path, "# Title\n\n| A |\n| --- |\n| one |\n")
    confluence = MagicMock()
    confluence.get.side_effect = RequestsConnectionError("snapshot failed")
    with patch("atl_cli.page_diagrams.pipeline.get_confluence", return_value=confluence), patch(
        "atl_cli.page_diagrams.pipeline.get_page_version", side_effect=RequestsConnectionError("version failed")
    ), patch("atl_cli.page_diagrams.pipeline.update_page_adf") as update:
        with pytest.raises(RequestsConnectionError):
            _publish(md_path, tmp_path)
    update.assert_not_called()


def test_cli_sanitizes_version_read_failure_after_snapshot_failure(tmp_path, capsys):
    from atl_cli.page_diagrams.cli import main

    md_path = _table_config(tmp_path, "# Title\n\n| A |\n| --- |\n| one |\n")
    confluence = MagicMock()
    confluence.get.side_effect = RequestsConnectionError("https://example.com/?token=secret")
    with patch("atl_cli.page_diagrams.pipeline.get_confluence", return_value=confluence), patch(
        "atl_cli.page_diagrams.pipeline.get_page_version",
        side_effect=RequestsConnectionError("https://example.com/?token=secret"),
    ), patch("atl_cli.page_diagrams.pipeline.update_page_adf") as update:
        with pytest.raises(SystemExit) as error:
            main(["run", "--md-path", str(md_path), "--page-id", "123", "--config", str(tmp_path / ".atlassian.json.user")])
    assert error.value.code == 1
    update.assert_not_called()
    stderr = capsys.readouterr().err
    assert "cannot read existing table widths" in stderr
    assert "Confluence request failed (ConnectionError)" in stderr
    assert "secret" not in stderr


def test_snapshot_conflict_is_reported_without_retry(tmp_path):
    plain = "# Title\n\n| A | B |\n| --- | --- |\n| one | two |\n"
    md_path = _table_config(tmp_path, plain)
    confluence = MagicMock()
    confluence.get.return_value = _snapshot(_width_doc(plain, [[[[155], [355]], [[155], [355]]]]))
    response = Response()
    response.status_code = 409
    with patch("atl_cli.page_diagrams.pipeline.get_confluence", return_value=confluence), patch(
        "atl_cli.page_diagrams.pipeline.get_page_version"
    ) as version, patch(
        "atl_cli.page_diagrams.pipeline.update_page_adf", side_effect=HTTPError("conflict", response=response)
    ) as update:
        with pytest.raises(RuntimeError, match="page changed after the table width snapshot"):
            _publish(md_path, tmp_path)
    version.assert_not_called()
    update.assert_called_once()
    assert update.call_args.args[4] == 7


def test_attachment_publish_uses_snapshot_version_and_final_width_manifest(tmp_path):
    plain = "# Title\n\n| A | B |\n| --- | --- |\n| one | two |\n"
    live = _width_doc(plain, [[[[155], [355]], [[155], [355]]]])
    (tmp_path / "screenshot.png").write_bytes(b"png-bytes")
    md_path = _table_config(tmp_path, plain + "\n![screenshot](screenshot.png)\n")
    confluence = MagicMock()
    confluence.get.return_value = _snapshot(live)
    with patch("atl_cli.page_diagrams.pipeline.get_confluence", return_value=confluence), patch(
        "atl_cli.page_diagrams.pipeline.get_page_version"
    ) as version, patch("atl_cli.page_diagrams.pipeline.upload_files", return_value={"screenshot.png": "file-1"}), patch(
        "atl_cli.page_diagrams.pipeline.update_page_adf"
    ) as update:
        result = _publish(md_path, tmp_path)
    version.assert_not_called()
    assert update.call_args.args[4] == 7
    final = update.call_args.args[3]
    table = next(node for node in final["content"] if node["type"] == "table")
    assert _table_widths(table) == [[[155], [355]], [[155], [355]]]
    assert any(node["type"] == "mediaSingle" for node in final["content"])
    assert json.loads((tmp_path / "final.manifest.json").read_text())["adf"] == final
    assert result["attachments"] == 1


def test_attachment_publish_does_not_retry_a_snapshot_conflict(tmp_path):
    plain = "# Title\n\n| A | B |\n| --- | --- |\n| one | two |\n"
    live = _width_doc(plain, [[[[155], [355]], [[155], [355]]]])
    (tmp_path / "screenshot.png").write_bytes(b"png-bytes")
    md_path = _table_config(tmp_path, plain + "\n![screenshot](screenshot.png)\n")
    confluence = MagicMock()
    confluence.get.return_value = _snapshot(live)
    response = Response()
    response.status_code = 409
    with patch("atl_cli.page_diagrams.pipeline.get_confluence", return_value=confluence), patch(
        "atl_cli.page_diagrams.pipeline.get_page_version"
    ) as version, patch(
        "atl_cli.page_diagrams.pipeline.upload_files", return_value={"screenshot.png": "file-1"}
    ) as upload, patch(
        "atl_cli.page_diagrams.pipeline.update_page_adf", side_effect=HTTPError("conflict", response=response)
    ) as update:
        with pytest.raises(RuntimeError, match="page changed after the table width snapshot"):
            _publish(md_path, tmp_path)
    upload.assert_called_once()
    update.assert_called_once()
    assert update.call_args.args[4] == 7
    version.assert_not_called()


def test_publish_png_branch_passes_the_selected_renderer_through(tmp_path):
    md_path = _write_page(tmp_path)
    base_adf = {"type": "doc", "content": [_marker_paragraph(0)]}

    def fake_render(diagrams, assets_dir, background="white", renderer="png", swimlane_drawio_enabled=False):
        for d in diagrams:
            d["filename"] = f"{d['name']}.png"

    with patch("atl_cli.page_diagrams.pipeline.convert_markdown_to_adf", return_value=base_adf), patch(
        "atl_cli.page_diagrams.pipeline.get_confluence", return_value=MagicMock()
    ), patch("atl_cli.page_diagrams.pipeline.render_diagrams", side_effect=fake_render) as mock_render, patch(
        "atl_cli.page_diagrams.pipeline.upload_diagrams", return_value={"00-title.png": "file-1"}
    ), patch("atl_cli.page_diagrams.pipeline.get_page_version", return_value=1), patch(
        "atl_cli.page_diagrams.pipeline.update_page_adf", return_value={"id": "123"}
    ), patch("atl_cli.page_diagrams.pipeline.substitute_drawio", return_value=(base_adf, 1)):
        result = _publish(md_path, tmp_path)

    assert mock_render.call_args.kwargs["renderer"] == "png"
    assert result["renderer"] == "png"


def test_publish_refuses_the_mermaid_renderer_before_touching_a_page(tmp_path):
    md_path = _write_page(tmp_path, "mermaid")

    with patch("atl_cli.page_diagrams.pipeline.get_confluence") as mock_confluence, patch(
        "atl_cli.page_diagrams.pipeline.render_diagrams"
    ) as mock_render:
        with pytest.raises(RuntimeError, match="section 7"):
            _publish(md_path, tmp_path)

    mock_confluence.assert_not_called()
    mock_render.assert_not_called()


def test_publish_rejects_an_unknown_renderer_before_touching_a_page(tmp_path):
    md_path = _write_page(tmp_path, "svg")

    with patch("atl_cli.page_diagrams.pipeline.get_confluence") as mock_confluence:
        with pytest.raises(ValueError, match="svg"):
            _publish(md_path, tmp_path)

    mock_confluence.assert_not_called()


def _fake_drawio_render(diagrams, assets_dir, background="white", renderer="png", swimlane_drawio_enabled=False):
    for d in diagrams:
        d["diagram_name"] = f"{d['name']}.drawio"
        d["search"] = "Start Done"
        d["width"], d["height"] = 841, 571
        d["renderer"] = "drawio"
        d["attachments"] = [
            {"path": f"/tmp/{d['name']}.drawio", "filename": f"{d['name']}.drawio"},
            {"path": f"/tmp/{d['name']}.drawio.png", "filename": f"{d['name']}.drawio.png"},
        ]


def test_publish_drawio_branch_registers_custom_content_and_injects_the_macro(tmp_path):
    md_path = _write_page(tmp_path, "drawio", "app-1/env-1/static/drawio")
    base_adf = {"type": "doc", "content": [_marker_paragraph(0)]}
    file_ids = {"00-title.drawio": "file-1", "00-title.drawio.png": "file-2"}

    with patch("atl_cli.page_diagrams.pipeline.convert_markdown_to_adf", return_value=base_adf), patch(
        "atl_cli.page_diagrams.pipeline.get_confluence", return_value=MagicMock()
    ), patch("atl_cli.page_diagrams.pipeline.render_diagrams", side_effect=_fake_drawio_render), patch(
        "atl_cli.page_diagrams.pipeline.upload_diagrams", return_value=file_ids
    ), patch("atl_cli.page_diagrams.pipeline.get_page_version", return_value=1), patch(
        "atl_cli.page_diagrams.pipeline.update_page_adf", return_value={"id": "123"}
    ), patch(
        "atl_cli.page_diagrams.pipeline.upsert_diagram", return_value={"id": "999", "revision": 1}
    ) as mock_upsert:
        result = _publish(md_path, tmp_path)

    mock_upsert.assert_called_once()
    assert mock_upsert.call_args.args[1:] == ("123", "00-title.drawio", "Start Done")

    node = base_adf["content"][0]
    assert node["type"] == "extension"
    assert node["attrs"]["extensionKey"] == "app-1/env-1/static/drawio"
    guest = node["attrs"]["parameters"]["guestParams"]
    assert guest["custContentId"] == "999"
    assert guest["pageId"] == "123"
    assert guest["baseUrl"] == "https://example.atlassian.net/wiki"
    assert (guest["width"], guest["height"]) == (841, 571)

    assert result["renderer"] == "drawio"
    assert result["attachments"] == 2


def test_publish_drawio_republish_reuses_the_existing_custom_content(tmp_path):
    md_path = _write_page(tmp_path, "drawio", "app-1/env-1/static/drawio")
    base_adf = {"type": "doc", "content": [_marker_paragraph(0)]}
    confluence = MagicMock()
    confluence.get.side_effect = [
        {"results": [{"id": "999", "title": "00-title.drawio", "version": {"number": 1}}]},
        {"space": {"key": "SPACE"}},
    ]

    with patch("atl_cli.page_diagrams.pipeline.convert_markdown_to_adf", return_value=base_adf), patch(
        "atl_cli.page_diagrams.pipeline.get_confluence", return_value=confluence
    ), patch("atl_cli.page_diagrams.pipeline.render_diagrams", side_effect=_fake_drawio_render), patch(
        "atl_cli.page_diagrams.pipeline.upload_diagrams", return_value={}
    ), patch("atl_cli.page_diagrams.pipeline.get_page_version", return_value=1), patch(
        "atl_cli.page_diagrams.pipeline.update_page_adf", return_value={"id": "123"}
    ):
        _publish(md_path, tmp_path)

    confluence.post.assert_not_called()
    assert confluence.put.call_args.args[0] == "/rest/api/content/999"
    guest = base_adf["content"][0]["attrs"]["parameters"]["guestParams"]
    assert guest["custContentId"] == "999"
    assert guest["revision"] == 2
    assert guest["contentVer"] == 2


def test_publish_drawio_branch_injects_a_media_node_for_a_diagram_that_fell_back_to_png(tmp_path):
    md_path = _write_page(tmp_path, "drawio", "app-1/env-1/static/drawio")
    base_adf = {"type": "doc", "content": [_marker_paragraph(0)]}

    def fell_back_to_png(diagrams, assets_dir, background="white", renderer="png", swimlane_drawio_enabled=False):
        for d in diagrams:
            d["renderer"] = "png"
            d["filename"] = f"{d['name']}.png"
            d["attachments"] = [{"path": f"/tmp/{d['name']}.png", "filename": d["filename"]}]

    with patch("atl_cli.page_diagrams.pipeline.convert_markdown_to_adf", return_value=base_adf), patch(
        "atl_cli.page_diagrams.pipeline.get_confluence", return_value=MagicMock()
    ), patch("atl_cli.page_diagrams.pipeline.render_diagrams", side_effect=fell_back_to_png), patch(
        "atl_cli.page_diagrams.pipeline.upload_diagrams", return_value={"00-title.png": "file-1"}
    ), patch("atl_cli.page_diagrams.pipeline.get_page_version", return_value=1), patch(
        "atl_cli.page_diagrams.pipeline.update_page_adf", return_value={"id": "123"}
    ), patch("atl_cli.page_diagrams.pipeline.upsert_diagram") as mock_upsert:
        _publish(md_path, tmp_path)

    mock_upsert.assert_not_called()
    node = base_adf["content"][0]
    assert node["type"] == "mediaSingle"
    assert node["content"][0]["attrs"]["id"] == "file-1"


def test_publish_drawio_without_the_extension_key_fails_before_touching_a_page(tmp_path):
    md_path = _write_page(tmp_path, "drawio")

    with patch("atl_cli.page_diagrams.pipeline.get_confluence") as mock_confluence, patch(
        "atl_cli.page_diagrams.pipeline.render_diagrams"
    ) as mock_render:
        with pytest.raises(ValueError, match="drawioExtensionKey"):
            _publish(md_path, tmp_path)

    mock_confluence.assert_not_called()
    mock_render.assert_not_called()


def _write_local_media_page(tmp_path):
    (tmp_path / "screenshot.png").write_bytes(b"png-bytes")
    (tmp_path / "notes.pdf").write_bytes(b"pdf-bytes")
    md_path = tmp_path / "page.md"
    md_path.write_text(
        "# Title\n\n"
        "![screenshot.png](screenshot.png)\n"
        "<!-- media-size: width=611 height=793 -->\n\n"
        "[notes.pdf](notes.pdf)\n"
    )
    return md_path


def test_publish_uploads_local_attachments_with_no_diagrams_present(tmp_path):
    md_path = _write_local_media_page(tmp_path)
    write_config(
        tmp_path,
        {"cloudId": "example.atlassian.net", "email": "me@example.com", "apiToken": "secret"},
    )
    base_adf = {"type": "doc", "content": [_marker_paragraph(0), _marker_paragraph(1)]}
    file_ids = {"screenshot.png": "file-1", "notes.pdf": "file-2"}

    with patch("atl_cli.page_diagrams.pipeline.convert_markdown_to_adf", return_value=base_adf), patch(
        "atl_cli.page_diagrams.pipeline.get_confluence", return_value=MagicMock()
    ), patch("atl_cli.page_diagrams.pipeline.upload_files", return_value=file_ids) as mock_upload_files, patch(
        "atl_cli.page_diagrams.pipeline.get_page_version", return_value=1
    ), patch("atl_cli.page_diagrams.pipeline.update_page_adf", return_value={"id": "123"}):
        result = _publish(md_path, tmp_path)

    uploaded = mock_upload_files.call_args.args[2]
    assert {u["filename"] for u in uploaded} == {"screenshot.png", "notes.pdf"}

    image_node, file_node = base_adf["content"]
    assert image_node["type"] == "mediaSingle"
    assert image_node["content"][0]["attrs"] == {
        "id": "file-1",
        "type": "file",
        "collection": "contentId-123",
        "alt": "screenshot.png",
        "width": 611,
        "height": 793,
    }
    assert file_node["type"] == "mediaGroup"
    assert file_node["content"][0]["attrs"] == {
        "id": "file-2",
        "type": "file",
        "collection": "contentId-123",
    }

    assert result["method"] == "rest"
    assert result["diagrams"] == 0
    assert result["attachments"] == 2


def _local_media_page(tmp_path):
    (tmp_path / "pic.png").write_bytes(b"\x89PNG\r\n\x1a\n")
    md_path = tmp_path / "doc.md"
    md_path.write_text("# My Page\n\n![pic](pic.png)\n")
    write_config(tmp_path, {"cloudId": "example.atlassian.net", "email": "me@example.com", "apiToken": "secret"})
    return md_path


def _publish_local_media(tmp_path, md_path, page_id):
    return publish(
        md_path=str(md_path),
        config_path=str(tmp_path / ".atlassian.json.user"),
        page_id=page_id,
        space_id="SPACE",
        title=None,
        assets_dir=str(tmp_path / "assets"),
        out_path=str(tmp_path / "final.json"),
    )


def test_a_failure_after_create_carries_the_new_page_id(tmp_path):
    from requests.exceptions import HTTPError

    from atl_cli.page_diagrams.pipeline import CreatedPageError

    md_path = _local_media_page(tmp_path)
    with patch("atl_cli.page_diagrams.pipeline.get_confluence", return_value=MagicMock()), patch(
        "atl_cli.page_diagrams.pipeline.create_page_adf", return_value={"id": "777"}
    ), patch("atl_cli.page_diagrams.pipeline.upload_files", side_effect=HTTPError("https://x/?token=secret")):
        with pytest.raises(CreatedPageError) as excinfo:
            _publish_local_media(tmp_path, md_path, None)

    assert excinfo.value.page_id == "777"
    assert "re-run with --page-id 777" in str(excinfo.value)
    assert "secret" not in str(excinfo.value)


def test_a_failure_on_update_keeps_its_original_exception(tmp_path):
    from requests.exceptions import HTTPError

    md_path = _local_media_page(tmp_path)
    with patch("atl_cli.page_diagrams.pipeline.get_confluence", return_value=MagicMock()), patch(
        "atl_cli.page_diagrams.pipeline.upload_files", side_effect=HTTPError("boom")
    ):
        with pytest.raises(HTTPError):
            _publish_local_media(tmp_path, md_path, "42")


def test_run_prints_the_created_page_id_as_json_on_a_post_create_failure(tmp_path, capsys):
    from requests.exceptions import HTTPError

    from atl_cli.page_diagrams import cli

    md_path = _local_media_page(tmp_path)
    with patch("atl_cli.page_diagrams.pipeline.get_confluence", return_value=MagicMock()), patch(
        "atl_cli.page_diagrams.pipeline.create_page_adf", return_value={"id": "777"}
    ), patch("atl_cli.page_diagrams.pipeline.upload_files", side_effect=HTTPError("boom")):
        with pytest.raises(SystemExit):
            cli.main(["run", "--md-path", str(md_path), "--space-id", "SPACE", "--config", str(tmp_path / ".atlassian.json.user")])

    captured = capsys.readouterr()
    assert json.loads(captured.out) == {"method": "rest", "pageId": "777", "published": False}
    assert "re-run with --page-id 777" in captured.err
