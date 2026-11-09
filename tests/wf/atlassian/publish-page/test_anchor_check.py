import json
import subprocess
import sys
from pathlib import Path

from atl_cli.page_diagrams import anchor_check

FETCHED = Path(__file__).resolve().parents[1] / "fetch-page" / "fixtures" / "shared-anchor.md"
FIXTURES = Path(__file__).parent / "fixtures"
ATL_PY = Path(__file__).resolve().parents[4] / "plugins" / "wf" / "skills" / "atlassian" / "scripts" / "atl.py"
SHARED_ID = "1e1cb525-8cdd-4497-8fce-7213342df598"
SINGLE_ID = "7f3a0c2e-1111-4222-8333-944455556666"


def _check(original: Path, edited: Path, capsys) -> tuple[int, dict, str]:
    code = anchor_check.main(["--original", str(original), "--md-path", str(edited)])
    captured = capsys.readouterr()
    return code, json.loads(captured.out), captured.err


def test_an_unchanged_fetch_lists_the_shared_id_with_its_block_count(capsys):
    code, report, _ = _check(FETCHED, FETCHED, capsys)

    assert code == 0
    assert report["sharedIds"] == [{"id": SHARED_ID, "blocks": 2}]
    assert report["kept"] == sorted([SHARED_ID, SINGLE_ID])
    assert report["removed"] == []
    assert report["partialCommentRemovals"] == []


def test_keeping_one_span_of_a_shared_id_fails_and_warns(capsys):
    code, report, err = _check(FETCHED, FIXTURES / "shared-anchor-new-partial.md", capsys)

    assert code == 1
    assert report["partialCommentRemovals"] == [{"id": SHARED_ID, "before": 2, "after": 1}]
    assert f"warning: comment anchor {SHARED_ID} spanned 2 blocks, now 1" in err


def test_removing_every_span_of_a_shared_id_is_an_intended_detachment(tmp_path, capsys):
    edited = FETCHED.read_text().replace(
        f'<!-- adf:comment id="{SHARED_ID}" -->Alerts older than 30 days are archived.<!-- /adf:comment -->', "Alerts are archived."
    ).replace(f'<!-- adf:comment id="{SHARED_ID}" -->Archived alerts stay searchable.<!-- /adf:comment -->', "Archives stay searchable.")
    page = tmp_path / "edited.md"
    page.write_text(edited)
    code, report, _ = _check(FETCHED, page, capsys)

    assert code == 0
    assert report["removed"] == [SHARED_ID]
    assert report["partialCommentRemovals"] == []


def test_ignored_sections_never_count_as_anchors(tmp_path, capsys):
    original = tmp_path / "page.md"
    original.write_text(
        'Body <!-- adf:comment id="a" -->x<!-- /adf:comment -->.\n\n<!-- adf:ignore:start -->\n'
        '## Comments\n\n- <!-- adf:comment id="a" -->x<!-- /adf:comment -->\n<!-- adf:ignore:end -->\n'
    )

    code, report, _ = _check(original, original, capsys)

    assert code == 0
    assert report["sharedIds"] == []


def test_runs_offline_through_atl_py_from_another_directory(tmp_path):
    result = subprocess.run(
        [sys.executable, str(ATL_PY), "publish-page", "check-anchors", "--original", str(FETCHED), "--md-path", str(FETCHED)],
        capture_output=True,
        text=True,
        cwd=tmp_path,
    )

    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["sharedIds"] == [{"id": SHARED_ID, "blocks": 2}]
