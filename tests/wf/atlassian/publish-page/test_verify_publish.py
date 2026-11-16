"""`verify_publish.py`: post-publish read-back checks; never deletes working files."""
from __future__ import annotations

from pathlib import Path

import pytest

from atl_cli import verify_publish
from atl_cli.verify_publish import FetchFailed, check_markdown

PAGE = """# Retention

<!-- adf:comment id="a1" -->Alerts older than 90 days are archived.<!-- /adf:comment -->

- <!-- adf:comment id="b2" -->Tasks keep<!-- /adf:comment --> their retention.

<!-- adf:ignore:start -->
## Comments
<!-- adf:comment id="zz" -->ignored<!-- /adf:comment --> Old phrase in a comment.
<!-- adf:ignore:end -->
"""


def _run(tmp_path, *, expect: int, present: list[str], absent: list[str], fetch=None) -> int:
    working = tmp_path / "work"
    working.mkdir()
    (working / "page.md").write_text("edited working copy")
    present_file, absent_file = tmp_path / "present.txt", tmp_path / "absent.txt"
    present_file.write_text("\n".join(present) + "\n")
    absent_file.write_text("\n".join(absent) + "\n")

    def fake_fetch(page_id: str, config: str, md_path: Path) -> str:
        md_path.parent.mkdir(parents=True, exist_ok=True)
        md_path.write_text(PAGE)
        return PAGE

    code = verify_publish.main(
        [
            "--page-id", "1", "--config", "cfg", "--expect-anchors", str(expect),
            "--present", str(present_file), "--absent", str(absent_file),
            "--verify-dir", str(working / "verify"),
        ],
        fetch=fetch or fake_fetch,
    )
    assert (working / "page.md").read_text() == "edited working copy"
    return code


def test_pass_prints_every_check_and_exits_zero(tmp_path, capsys):
    code = _run(tmp_path, expect=2, present=["older than 90 days", "Tasks keep their retention."], absent=["30 days"])

    out = capsys.readouterr().out
    assert code == 0
    assert "PASS anchor-count (expected 2, found 2)" in out
    assert 'PASS present: "Tasks keep their retention."' in out
    assert "4/4 checks passed" in out
    assert (tmp_path / "work" / "verify" / "page.md").exists()


def test_missing_edited_phrase_fails_by_name(tmp_path, capsys):
    code = _run(tmp_path, expect=2, present=["older than 30 days"], absent=[])

    assert code == 1
    assert 'FAIL present: "older than 30 days"' in capsys.readouterr().out


def test_removed_phrase_still_present_fails_by_name(tmp_path, capsys):
    code = _run(tmp_path, expect=2, present=[], absent=["Alerts older than 90 days"])

    assert code == 1
    assert 'FAIL absent: "Alerts older than 90 days"' in capsys.readouterr().out


def test_wrong_anchor_count_fails_by_name(tmp_path, capsys):
    code = _run(tmp_path, expect=3, present=[], absent=[])

    assert code == 1
    assert "FAIL anchor-count (expected 3, found 2)" in capsys.readouterr().out


def test_refetch_failure_exits_two_and_keeps_files(tmp_path, capsys):
    def failing_fetch(page_id: str, config: str, md_path: Path) -> str:
        raise FetchFailed("Page fetch failed: HTTPError 404: check site URL and page id; wrong API base?")

    code = _run(tmp_path, expect=2, present=[], absent=[], fetch=failing_fetch)

    assert code == 2
    assert "FAIL re-fetch: Page fetch failed: HTTPError 404" in capsys.readouterr().err


def test_ignored_comments_section_is_not_counted_or_matched():
    checks = check_markdown(PAGE, 2, [], ["Old phrase in a comment."])
    assert all(check.passed for check in checks)


@pytest.mark.parametrize("phrase", ["Tasks keep their retention.", "Tasks   keep their\nretention."])
def test_phrases_match_across_comment_spans_and_whitespace(phrase):
    assert check_markdown(PAGE, 2, [phrase], [])[1].passed


def test_fetch_markdown_runs_fetch_page_in_process_and_surfaces_its_stderr(tmp_path, monkeypatch):
    def failing_fetch(argv):
        import sys

        assert argv[argv.index("--attachments") + 1] == "skip"
        assert argv[argv.index("--comments") + 1] == "skip"
        print("Page fetch failed: HTTPError 404: check site URL and page id; wrong API base?", file=sys.stderr)
        raise SystemExit(1)

    monkeypatch.setattr("atl_cli.fetch_page.assemble_page.main", failing_fetch)

    with pytest.raises(FetchFailed, match="HTTPError 404"):
        verify_publish.fetch_markdown("1", "cfg", tmp_path / "verify" / "page.md")


def test_fetch_markdown_returns_the_written_page(tmp_path, monkeypatch):
    def fetch(argv):
        Path(argv[argv.index("--md-path") + 1]).write_text("# Title\n\nBody.\n", encoding="utf-8")

    monkeypatch.setattr("atl_cli.fetch_page.assemble_page.main", fetch)

    assert verify_publish.fetch_markdown("1", "cfg", tmp_path / "verify" / "page.md") == "# Title\n\nBody.\n"


@pytest.mark.parametrize("change,expected_code", [(None, 0), ("mark", 1), ("title", 1), ("media-id", 1)])
def test_semantic_manifest_checks_raw_adf_even_when_markdown_matches(tmp_path, change, expected_code, capsys):
    import copy
    import json

    expected = {"type": "doc", "content": [
        {"type": "paragraph", "content": [{"type": "text", "text": "same words", "marks": [{"type": "strong"}]}]},
        {"type": "mediaSingle", "content": [{"type": "media", "attrs": {"id": "uploaded-id", "type": "file"}}]},
    ]}
    actual = copy.deepcopy(expected)
    title = "Title"
    if change == "mark":
        actual['content'][0]['content'][0].pop('marks')
    elif change == "title":
        title = "Changed"
    elif change == "media-id":
        actual['content'][1]['content'][0]['attrs']['id'] = 'wrong-id'
    path = tmp_path / 'manifest.json'
    path.write_text(json.dumps({"title": "Title", "adf": expected}))
    code = verify_publish.main(
        ['--page-id', '1', '--config', 'cfg', '--expect-anchors', '0', '--expected-manifest', str(path), '--verify-dir', str(tmp_path / 'verify')],
        fetch=lambda *_: '# Title\n\nsame words\n', fetch_raw=lambda *_: (title, actual),
    )
    assert code == expected_code
    assert path.exists()
    if change == 'mark':
        assert 'FAIL semantic-body' in capsys.readouterr().out
