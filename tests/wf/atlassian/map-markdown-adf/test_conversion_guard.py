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


def test_mismatched_table_separator_rejected_without_stdout(run_cli):
    result = run_cli("md-to-adf", "| a | b |\n| --- |\n")
    assert result.returncode == 1
    assert "separator column count" in result.stderr
    assert result.stdout == ""


@pytest.mark.parametrize("source", [
    '<!-- adf:table width="600" -->\nparagraph',
    '<!-- adf:breakout mode="wide" -->\nparagraph',
    '<!-- adf:mystery -->', '<details>\n<summary>x</summary>\nbody',
    '<!-- adf:attachment media-id="a" -->', '<!-- adf:lossy -->', '<div>unsupported</div>', '![image](https://example.com/a.png)',
])
def test_invalid_dialect_is_rejected(source):
    with pytest.raises((guard.GuardError, ConversionError, ValueError)):
        md_to_adf(source, guarded=True)


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


def test_known_degradation_is_reported_and_publish_rejected():
    doc = document(paragraph({"type": "inlineCard", "attrs": {"url": "https://example.com"}}))
    assert guard.guard_adf(doc, fetching=True) == ["smart card normalized to a plain link"]
    with pytest.raises(guard.GuardError, match="lossy conversion"):
        guard.guard_adf(doc)


def test_unknown_attributes_are_not_silently_dropped():
    doc = document(paragraph(text('body')))
    doc['content'][0]['attrs'] = {'unrecognized': 'must survive'}
    with pytest.raises(guard.GuardError, match="doc.content"):
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
