from __future__ import annotations

import copy
import json
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from atl_cli import conversion_guard as guard
from atl_cli.converter.adf_to_md import adf_to_markdown
from atl_cli.converter.md_to_adf import markdown_to_adf
from atl_cli.map_markdown import ConversionError, adf_to_md, md_to_adf
from atl_cli.page_diagrams.patterns import strip_ignored_sections


def document(*nodes):
    return {"type": "doc", "version": 1, "content": list(nodes)}


def paragraph(*nodes):
    return {"type": "paragraph", "content": list(nodes)}


def text(value, **extra):
    return {"type": "text", "text": value, **extra}


@pytest.mark.parametrize("value", [
    "literal *stars* and [x](https://example.com)", "a_b_c", "\\*literal*", "# Heading", "> quote",
    "- list", "3. ordered", '<!-- adf:toc -->', '<!-- adf:comment id="a" -->',
])
def test_literal_adf_text_round_trips_without_gaining_structure(value):
    doc = document(paragraph(text(value)))
    guard.compare_documents(doc, markdown_to_adf(adf_to_markdown(doc)))
    guard.guard_adf(doc)


@pytest.mark.parametrize("value", ["a `tick` inside code", "`leading", "trailing`", "``", " padded "])
def test_code_spans_preserve_backticks_and_spaces(value):
    doc = document(paragraph(text(value, marks=[{"type": "code"}])))
    guard.compare_documents(doc, markdown_to_adf(adf_to_markdown(doc)))


def test_code_fence_longer_than_embedded_fences():
    doc = document({"type": "codeBlock", "attrs": {"language": "python"}, "content": [text("```\n<!-- adf:toc -->\n````")]})
    guard.guard_adf(doc)
    assert adf_to_markdown(doc).startswith("`````python")


@pytest.mark.parametrize("container", [None, "blockquote", "panel", "listItem"])
def test_hard_break_survives_in_containers(container):
    node = paragraph(text("first"), {"type": "hardBreak"}, text("second"))
    if container:
        node = {"type": container, "content": [node]}
        if container == "panel":
            node["attrs"] = {"panelType": "info"}
        if container == "listItem":
            node = {"type": "bulletList", "content": [node]}
    guard.guard_adf(document(node))


def test_pipe_inside_table_cell_remains_one_cell():
    doc = document({"type": "table", "content": [{"type": "tableRow", "content": [
        {"type": "tableHeader", "content": [paragraph(text("a | b"))]},
    ]}]})
    converted = markdown_to_adf(adf_to_markdown(doc))
    guard.compare_documents(doc, converted)
    assert len(converted["content"][0]["content"][0]["content"]) == 1


@pytest.mark.parametrize("matrix", [
    [[[155], [355]], [[155], [355]], [[155], [355]]],
    [[[155], None], [None, [355]], [[160], []]],
    [[[155], {}], [None, [355]], [[160], []]],
    [[None, None], [None, None], [None, None]],
])
def test_table_widths_round_trip_without_changing_absent_or_row_specific_values(matrix):
    source = "| # | Source |\n| --- | --- |\n| one | two |\n| three | four |\n"
    doc = md_to_adf(source)
    for row, widths in zip(doc["content"][0]["content"], matrix):
        for cell, width in zip(row["content"], widths):
            cell["attrs"] = {"colspan": 1, "rowspan": 1}
            if width is not None:
                cell["attrs"]["colwidth"] = None if width == {} else width

    markdown = adf_to_md(doc, guarded=True)
    assert "colwidths=" in markdown or "cell-widths=" in markdown
    result = md_to_adf(markdown, guarded=True)
    guard.compare_documents(doc, result)


@pytest.mark.parametrize("container", ["blockquote", "panel", "nested-blockquote"])
def test_table_widths_round_trip_in_quoted_containers(container):
    table = md_to_adf("| A | B |\n| --- | --- |\n| one | two |\n")["content"][0]
    for row in table["content"]:
        for cell, width in zip(row["content"], (155, 355)):
            cell["attrs"] = {"colwidth": [width]}
    if container == "nested-blockquote":
        node = {"type": "blockquote", "content": [{"type": "blockquote", "content": [table]}]}
    elif container == "panel":
        node = {"type": "panel", "attrs": {"panelType": "note"}, "content": [table]}
    else:
        node = {"type": "blockquote", "content": [table]}
    doc = document(node)
    rendered = adf_to_md(doc, guarded=True)
    assert "colwidths=" in rendered
    guard.compare_documents(doc, md_to_adf(rendered, guarded=True))


@pytest.mark.parametrize("source", [
    '<!-- adf:table colwidths="[[155]]" -->\n> | A |\n> | --- |\n',
    '> <!-- adf:table colwidths="[[155]]" -->\n| A |\n| --- |\n',
    '> <!-- adf:table colwidths="[[155]]" -->\n\n> | A |\n> | --- |\n',
])
def test_table_marker_cannot_cross_quote_boundaries(source):
    with pytest.raises(guard.GuardError, match="table marker must precede a table"):
        guard.validate_markdown(source)


def test_widths_are_part_of_fidelity_comparison():
    original = md_to_adf("| A | B |\n| --- | --- |\n| 1 | 2 |\n")
    changed = copy.deepcopy(original)
    changed["content"][0]["content"][0]["content"][0]["attrs"] = {"colwidth": [155]}
    with pytest.raises(guard.GuardError, match="semantic content"):
        guard.compare_documents(original, changed)


def test_row_specific_widths_round_trip_with_formatted_content():
    source = (
        "| Name | Details |\n| --- | --- |\n"
        "| **one** | [link](https://example.com) \\| escaped |\n"
        "| *two* | first<br>second |\n"
    )
    doc = md_to_adf(source)
    for row, values in zip(doc["content"][0]["content"], [
        [[155], [355]], [[160], [350]], [[165], [345]],
    ]):
        for cell, value in zip(row["content"], values):
            cell["attrs"] = {"colwidth": value}
    markdown = adf_to_md(doc, guarded=True)
    guard.compare_documents(doc, md_to_adf(markdown, guarded=True))


def test_stale_width_metadata_warns_and_defaults_instead_of_moving_columns(run_cli):
    doc = md_to_adf("| # | Source |\n| --- | --- |\n| one | two |\n")
    markdown = adf_to_md(doc, guarded=True).replace("| # | Source |", "| Source | # |")
    result = run_cli("md-to-adf", markdown)
    assert result.returncode == 0
    assert "column headers changed; using default column widths" in result.stderr
    table = json.loads(result.stdout)["content"][0]
    assert [cell["attrs"]["colwidth"] for cell in table["content"][0]["content"]] == [[110], [60]]


def test_added_column_invalidates_existing_width_metadata(run_cli):
    doc = md_to_adf("| # | Source |\n| --- | --- |\n| one | two |\n")
    markdown = adf_to_md(doc, guarded=True).replace(
        "| # | Source |\n| --- | --- |\n| one | two |",
        "| # | Source | Extra |\n| --- | --- | --- |\n| one | two | three |",
    )
    result = run_cli("md-to-adf", markdown)
    assert result.returncode == 0
    assert "column headers changed; using default column widths" in result.stderr
    table = json.loads(result.stdout)["content"][0]
    assert [cell["attrs"]["colwidth"] for cell in table["content"][0]["content"]] == [[60], [110], [1230]]


def test_consistent_sparse_widths_survive_row_edits(run_cli):
    doc = md_to_adf("| A | B |\n| --- | --- |\n| one | two |\n")
    doc["content"][0]["content"][0]["content"][0]["attrs"] = {"colwidth": [155]}
    markdown = adf_to_md(doc, guarded=True).replace("| one | two |", "| changed | two |")
    result = run_cli("md-to-adf", markdown)
    assert result.returncode == 0
    assert "table rows changed; applied consistent column widths" in result.stderr
    rows = json.loads(result.stdout)["content"][0]["content"]
    assert [row["content"][0]["attrs"]["colwidth"] for row in rows] == [[155], [155]]


def test_stale_conflicting_row_specific_widths_warn_and_default(run_cli):
    doc = md_to_adf("| A | B |\n| --- | --- |\n| one | two |\n")
    doc["content"][0]["content"][0]["content"][0]["attrs"] = {"colwidth": [155]}
    doc["content"][0]["content"][1]["content"][0]["attrs"] = {"colwidth": [160]}
    markdown = adf_to_md(doc, guarded=True).replace("| one | two |", "| changed | two |")
    result = run_cli("md-to-adf", markdown)
    assert result.returncode == 0
    assert "table rows changed; using default column widths" in result.stderr
    rows = json.loads(result.stdout)["content"][0]["content"]
    assert all("colwidth" not in row["content"][0].get("attrs", {}) for row in rows)


def test_row_specific_widths_do_not_follow_reordered_rows_with_same_text_and_different_marks(run_cli):
    source = "| A |\n| --- |\n| **same** |\n| *same* |\n"
    doc = md_to_adf(source)
    doc["content"][0]["content"][1]["content"][0]["attrs"] = {"colwidth": [155]}
    doc["content"][0]["content"][2]["content"][0]["attrs"] = {"colwidth": [160]}
    markdown = adf_to_md(doc, guarded=True).replace(
        "| **same** |\n| *same* |", "| *same* |\n| **same** |"
    )
    result = run_cli("md-to-adf", markdown)
    assert result.returncode == 0
    assert "table rows changed; using default column widths" in result.stderr
    assert all("colwidth" not in row["content"][0].get("attrs", {}) for row in json.loads(result.stdout)["content"][0]["content"])


def test_row_specific_widths_do_not_guess_when_comment_removal_makes_rows_identical(run_cli):
    source = (
        '| A |\n| --- |\n| <!-- adf:comment id="c1" -->same<!-- /adf:comment --> |\n'
        '| <!-- adf:comment id="c2" -->same<!-- /adf:comment --> |\n'
    )
    doc = md_to_adf(source, guarded=True)
    doc["content"][0]["content"][1]["content"][0]["attrs"] = {"colwidth": [155]}
    doc["content"][0]["content"][2]["content"][0]["attrs"] = {"colwidth": [160]}
    markdown = adf_to_md(doc, guarded=True)
    from atl_cli.copy_page import strip_comment_anchors

    result = run_cli("md-to-adf", strip_comment_anchors(markdown))
    assert result.returncode == 0
    assert "table rows changed; using default column widths" in result.stderr
    assert all("colwidth" not in row["content"][0].get("attrs", {}) for row in json.loads(result.stdout)["content"][0]["content"])


def test_row_specific_width_identity_keeps_literal_comment_tags_in_code(run_cli):
    source = '| A |\n| --- |\n| `<!-- adf:comment id="c1" -->` |\n'
    doc = md_to_adf(source, guarded=True)
    doc["content"][0]["content"][0]["content"][0]["attrs"] = {"colwidth": [155]}
    doc["content"][0]["content"][1]["content"][0]["attrs"] = {"colwidth": [160]}
    markdown = adf_to_md(doc, guarded=True).replace('id="c1"', 'id="c2"')
    result = run_cli("md-to-adf", markdown)
    assert result.returncode == 0
    assert "table rows changed; using default column widths" in result.stderr


@pytest.mark.parametrize("marker", [
    '<!-- adf:table colwidths="not-json" -->',
    '<!-- adf:table colwidths="[true]" -->',
    '<!-- adf:table colwidths="[[-1]]" -->',
    '<!-- adf:table colwidths="[null]" cell-widths="[[null]]" -->',
    '<!-- adf:table header-hash="not-a-hash" colwidths="[null]" -->',
    '<!-- adf:table colwidths="[[155]]" colwidths="[[355]]" -->',
    '<!-- adf:table colwidths="[[155]]" COLWIDTHS="[[355]]" -->',
])
def test_invalid_width_markers_are_rejected(marker, run_cli):
    result = run_cli("md-to-adf", marker + "\n| A |\n| --- |\n")
    assert result.returncode != 0
    assert "table marker" in result.stderr
    assert result.stdout == ""


def test_mismatched_table_separator_rejected_without_stdout(run_cli):
    result = run_cli("md-to-adf", "| a | b |\n| --- |\n")
    assert result.returncode == 1
    assert "separator column count" in result.stderr
    assert result.stdout == ""


@pytest.mark.parametrize("source", [
    '<!-- adf:table width="600" -->\nparagraph',
    '<!-- adf:breakout mode="wide" -->\nparagraph',
    '<!-- adf:mystery -->', '<details>\n<summary>x</summary>\nbody',
    '<!-- adf:attachment media-id="a" -->', '<!-- adf:error id="e1" node="mention" -->', '<div>unsupported</div>', '![image](https://example.com/a.png)',
])
def test_invalid_dialect_is_rejected(source):
    with pytest.raises((guard.GuardError, ConversionError, ValueError)):
        md_to_adf(source, guarded=True)


def test_adf_error_tag_is_allowed_in_fetched_markdown_but_blocks_publishing():
    source = 'Hi <!-- adf:error id="e1" node="mention" -->⚠️ **Conversion error e1:** x\n'

    guard.validate_markdown(source, placeholders=True)
    with pytest.raises(guard.GuardError, match="line 1: unresolved conversion error"):
        guard.validate_markdown(source)
    with pytest.raises(guard.GuardError, match="malformed adf:error"):
        guard.validate_markdown('<!-- adf:error node="x" -->\n', placeholders=True)


def test_pragmas_and_ambient_files_cannot_disable_lint(tmp_path, monkeypatch):
    (tmp_path / '.pymarkdown').write_text('{"plugins":{"md010":{"enabled":false}}}')
    (tmp_path / 'pyproject.toml').write_text('[tool.pymarkdown.plugins.md010]\nenabled=false\n')
    monkeypatch.chdir(tmp_path)
    source = '<!-- pymarkdown disable MD010 -->\n\ntext\twith tab\n'
    with pytest.raises(guard.GuardError, match="MD010"):
        guard.lint_markdown(source)
    assert Path.cwd() == tmp_path


def test_broken_ambient_config_does_not_affect_lint(tmp_path, monkeypatch):
    (tmp_path / '.pymarkdown').write_text('invalid JSON')
    monkeypatch.chdir(tmp_path)
    guard.lint_markdown('Body fragment with no heading.\n')


def test_missing_profile_fails_closed(monkeypatch, tmp_path):
    monkeypatch.setattr(guard, '_PROFILE', tmp_path / 'missing.json')
    with pytest.raises(guard.GuardError, match="configuration missing"):
        guard.lint_markdown('# Title\n')


def test_no_source_rewrite_and_no_formatting_rules_for_confluence_dialect():
    fixture = Path(__file__).parents[1] / 'regression/fixtures/round-trip-page.md'
    original = fixture.read_bytes()
    guard.lint_markdown(original.decode())
    assert fixture.read_bytes() == original


def test_inline_card_round_trips_without_conversion_degradation():
    doc = document(paragraph({"type": "inlineCard", "attrs": {"url": "https://example.com"}}))

    assert guard.guard_adf(doc) == []


def test_inline_card_keeps_an_inline_comment_anchor():
    card = {
        "type": "inlineCard",
        "attrs": {"url": "https://example.com", "localId": "card-1"},
        "marks": [{"type": "annotation", "attrs": {"annotationType": "inlineComment", "id": "c1"}}],
    }
    doc = document(paragraph(card))

    assert guard.guard_adf(doc) == []
    assert adf_to_markdown(doc).startswith(
        '<!-- adf:comment id="c1" --><!-- adf:inline-card -->'
    )


def test_unknown_attributes_are_not_silently_dropped():
    doc = document(paragraph(text('body')))
    doc['content'][0]['attrs'] = {'unrecognized': 'must survive'}
    with pytest.raises(guard.GuardError, match="doc.content"):
        guard.guard_adf(doc)


def test_confluence_status_style_bold_is_a_default_but_other_styles_are_not():
    def status(**extra):
        return document(paragraph({"type": "status", "attrs": {"text": "Neutral", "color": "neutral", **extra}}))

    confluence = status(style="bold", localId="648ee447-17c9-4901-8ea8-e369e79194d7")
    guard.guard_adf(confluence, fetching=True)
    guard.compare_documents(confluence, markdown_to_adf(adf_to_markdown(confluence)))
    with pytest.raises(guard.GuardError, match="attrs.keys"):
        guard.compare_documents(status(style="subtle"), markdown_to_adf(adf_to_markdown(status(style="subtle"))))


@pytest.mark.parametrize("source", [
    "[`Foo.Bar`](https://example.com)", "see **[`Foo.Bar`](https://example.com)** here", "[a `b` c](https://example.com)",
    "| Form | [`Foo.Bar`](https://example.com) |",
])
def test_code_span_inside_a_link_is_rejected_with_its_line(source):
    with pytest.raises(guard.GuardError, match=r"line 2: code span inside a link"):
        guard.validate_markdown("intro\n" + source)


@pytest.mark.parametrize("source", [
    "[Foo.Bar](https://example.com) and `Foo.Bar`", "`[Foo.Bar](https://example.com)`", "`` [`Foo.Bar`](https://example.com) ``",
    "\\[`Foo.Bar`](https://example.com)",
])
def test_code_and_link_apart_or_quoted_as_code_are_accepted(source):
    guard.validate_markdown(source)


def test_linked_code_from_confluence_fetches_as_a_plain_link_and_cannot_be_republished(capsys):
    node = text("Foo.Bar", marks=[{"type": "code"}, {"type": "link", "attrs": {"href": "https://example.com"}}])
    doc = document(paragraph(node))

    assert guard.guard_adf(doc, fetching=True) == ["code inside link omitted"]
    assert adf_to_md(doc, guarded=True) == "[Foo.Bar](https://example.com)\n"
    assert "warning: code inside link omitted" in capsys.readouterr().err
    with pytest.raises(guard.GuardError, match="lossy conversion"):
        guard.guard_adf(doc)


def test_plain_jira_wrappers_do_not_enable_confluence_lint(monkeypatch):
    monkeypatch.setattr(guard, 'lint_markdown', MagicMock(side_effect=AssertionError('unexpected lint')))
    assert md_to_adf('body\ttab')['type'] == 'doc'
    assert adf_to_md(document(paragraph(text('body\ttab')))) == 'body\ttab\n'


def test_ignore_markers_inside_long_fence_and_code_span_are_literal():
    source = '````text\n```\n<!-- adf:ignore:start -->\nkeep\n<!-- adf:ignore:end -->\n````\n\n`<!-- adf:ignore:start -->`\n'
    assert strip_ignored_sections(source) == source


def test_round_trip_fixed_point_and_semantics_for_full_fixture():
    fixture = Path(__file__).parents[1] / 'regression/fixtures/round-trip-page.md'
    from atl_cli.page_diagrams.mermaid import extract_mermaid
    from atl_cli.page_diagrams.local_media import extract_local_media
    source = strip_ignored_sections(fixture.read_text())
    source, diagrams = extract_mermaid(source)
    source, _ = extract_local_media(source, fixture.parent, start_index=len(diagrams))
    doc = markdown_to_adf(source)
    guard.guard_adf(doc)
    canonical = adf_to_markdown(doc)
    for _ in range(3):
        next_doc = markdown_to_adf(canonical)
        guard.compare_documents(doc, next_doc)
        assert adf_to_markdown(next_doc) == canonical


def test_diagnostics_name_the_semantic_path():
    expected = document(paragraph(text('same words', marks=[{'type': 'strong'}])))
    actual = copy.deepcopy(expected)
    actual['content'][0]['content'][0].pop('marks')
    with pytest.raises(guard.GuardError, match=r'doc.content\[0\].content\[0\]'):
        guard.compare_documents(expected, actual)


@pytest.mark.parametrize('node', [
    paragraph(text(123)), paragraph(text('x', marks=[None])), paragraph(None),
])
def test_malformed_adf_exits_without_traceback_or_partial_output(run_cli, node):
    result = run_cli('adf-to-md', json.dumps(document(node)))
    assert result.returncode == 1
    assert result.stderr.startswith('error: ADF')
    assert 'Traceback' not in result.stderr
    assert result.stdout == ''


def test_indented_code_is_rejected_instead_of_losing_formatting(run_cli):
    result = run_cli('md-to-adf', '    print("hello")\n')
    assert result.returncode == 1
    assert 'indented code' in result.stderr
    assert result.stdout == ''


@pytest.mark.parametrize('info', ['c++', 'objective-c', 'sh title'])
def test_detect_skips_arbitrary_fence_info_and_conversion_reports_unsupported(run_cli, info):
    source = f'```{info}\n<!-- adf:toc -->\n```\n'
    result = run_cli('detect-adf-only', source)
    assert result.returncode == 0
    assert not json.loads(result.stdout)['adfOnly']
    result = run_cli('md-to-adf', source)
    assert result.returncode == 1
    assert 'unsupported code language' in result.stderr


def test_fence_closes_with_trailing_whitespace(run_cli):
    result = run_cli('md-to-adf', '```python\nx = 1\n```  \n')
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)['content'][0]['type'] == 'codeBlock'


def _text(value: str, *marks: str) -> dict:
    node = {"type": "text", "text": value}
    if marks:
        node["marks"] = [{"type": mark} for mark in marks]
    return node


def _paragraph(*content: dict) -> dict:
    return {"type": "paragraph", "content": list(content)}


def test_empty_block_paragraphs_and_trailing_space_do_not_fail_the_round_trip():
    card = {"type": "inlineCard", "attrs": {"url": "https://example.atlassian.net/wiki/spaces/X/pages/1"}}
    doc = {"type": "doc", "version": 1, "content": [
        _paragraph(card, _text(" ")),
        {"type": "paragraph"},
        _paragraph(_text("after")),
    ]}
    guard.check_round_trip(doc, fetching=True)


def test_adjacent_bold_italic_spans_with_a_literal_asterisk_round_trip():
    doc = {"type": "doc", "version": 1, "content": [_paragraph(
        _text("Add "), _text("*", "strong", "em"), _text(" - new version ", "em"), _text("1.2.14", "strong", "em"),
    )]}
    guard.check_round_trip(doc, fetching=True)


def test_paragraph_after_a_code_block_in_a_list_item_round_trips():
    item = {"type": "listItem", "content": [
        _paragraph(_text("Run")),
        {"type": "codeBlock", "content": [_text("echo a")]},
        _paragraph(_text("then wait")),
    ]}
    doc = {"type": "doc", "version": 1, "content": [{"type": "orderedList", "content": [item]}]}
    guard.check_round_trip(doc)


def test_strong_text_around_code_renders_as_one_canonical_span():
    doc = {"type": "doc", "version": 1, "content": [_paragraph(
        _text("Use "), _text("the ", "strong"), _text("atl", "strong", "code"), _text(" command", "strong"), _text(" now"),
    )]}

    assert adf_to_markdown(doc) == "Use **the `atl` command** now"
    guard.check_round_trip(doc, fetching=True)


@pytest.mark.parametrize("markdown", [
    "**bold `code` bold** and `**x**` and **`c`**",
    "*it `c` it* and ~~gone `c`~~",
    "**a `c` b *i* `d`** tail",
    "[**link** plain](https://example.com/x) and **[linked bold](https://example.com/y) `c`**",
])
def test_nested_inline_marks_reach_a_stable_semantic_round_trip(markdown):
    doc = markdown_to_adf(markdown)

    guard.check_round_trip(doc)
    assert adf_to_markdown(markdown_to_adf(adf_to_markdown(doc))) == adf_to_markdown(doc)
    guard.compare_documents(doc, markdown_to_adf(adf_to_markdown(doc)))


def test_server_mark_order_and_text_splits_are_semantically_equal():
    split = {"type": "doc", "version": 1, "content": [_paragraph(
        _text("bold ", "strong"), _text("code", "code", "strong"), _text(" bold", "strong"),
    )]}
    server = {"type": "doc", "version": 1, "content": [_paragraph(
        _text("bold ", "strong"), _text("code", "strong", "code"), _text(" bold", "strong"),
    )]}

    guard.compare_documents(split, server, transport=True)


@pytest.mark.parametrize("sent, returned", [("text", "plaintext"), ("plaintext", "text"), ("shell", "bash")])
def test_code_block_language_aliases_are_semantically_equal(sent, returned):
    def block(language: str) -> dict:
        return {"type": "doc", "version": 1, "content": [
            {"type": "codeBlock", "attrs": {"language": language}, "content": [_text("x")]},
        ]}

    guard.compare_documents(block(sent), block(returned), transport=True)


def test_unknown_code_block_language_stays_observable():
    def block(language: str) -> dict:
        return {"type": "doc", "version": 1, "content": [
            {"type": "codeBlock", "attrs": {"language": language}, "content": [_text("x")]},
        ]}

    with pytest.raises(guard.GuardError, match=r"doc\.content\[0\]\.attrs\.language"):
        guard.compare_documents(block("cobol"), block("plaintext"), transport=True)


def test_server_drops_formatting_marks_that_the_schema_excludes_beside_code():
    sent = {"type": "doc", "version": 1, "content": [_paragraph(
        _text("atl", "code", "strong"), _text("c", "code", "em"), _text("s", "code", "strike", "link"),
    )]}
    sent["content"][0]["content"][2]["marks"][2] = {"type": "link", "attrs": {"href": "https://example.com"}}
    returned = {"type": "doc", "version": 1, "content": [_paragraph(
        _text("atl", "code"), _text("c", "code"), _text("s", "code", "link"),
    )]}
    returned["content"][0]["content"][2]["marks"][1] = {"type": "link", "attrs": {"href": "https://example.com"}}

    guard.compare_documents(sent, returned, transport=True)
    with pytest.raises(guard.GuardError, match="semantic content"):
        guard.compare_documents(sent, returned)


def test_server_alias_does_not_hide_a_lost_strong_mark_without_code():
    sent = {"type": "doc", "version": 1, "content": [_paragraph(_text("bold", "strong"))]}
    returned = {"type": "doc", "version": 1, "content": [_paragraph(_text("bold"))]}

    with pytest.raises(guard.GuardError, match=r"doc\.content\[0\]\.content\[0\]"):
        guard.compare_documents(sent, returned, transport=True)
