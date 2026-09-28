from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "select_tickets.py"


def select(tmp_path, pages, kind):
    snapshot = tmp_path / "issues.json"
    snapshot.write_text(json.dumps(pages), encoding="utf-8")
    result = subprocess.run(
        [sys.executable, str(SCRIPT), str(snapshot), "--kind", kind],
        check=True, capture_output=True, text=True,
    )
    return json.loads(result.stdout)


def issue(number, *labels, state="open", **extra):
    return {"number": number, "state": state,
            "labels": [{"name": label} for label in labels], **extra}


def test_implementation_excludes_tests_and_review_gates_across_pages(tmp_path):
    pages = [[issue(5), issue(2, "tests"), issue(3, "hitl")],
             [issue(4, "spec"), issue(1, "bug"), issue(6, "TESTS")]]
    assert [item["number"] for item in select(tmp_path, pages, "implementation")] == [1, 5]


def test_tests_require_label_and_exclude_both_review_gates(tmp_path):
    pages = [[issue(1), issue(2, "tests"), issue(3, "tests", "HITL")],
             [issue(4, "tests", "spec"), issue(5, "Tests")]]
    assert [item["number"] for item in select(tmp_path, pages, "tests")] == [2, 5]


def test_closed_issues_and_pull_requests_are_never_tasks(tmp_path):
    pages = [[issue(1, state="closed"), issue(2, pull_request={}),
              issue(3, "tests", state="closed"), issue(4, "tests", pull_request={})]]
    assert select(tmp_path, pages, "implementation") == []
    assert select(tmp_path, pages, "tests") == []


def test_removing_hitl_releases_test_ticket_and_preserves_body(tmp_path):
    ticket = issue(1, "tests", "hitl", body="## Blocked by\n- Blocked by #8")
    assert select(tmp_path, [[ticket]], "tests") == []
    ticket["labels"].pop()
    assert select(tmp_path, [[ticket]], "tests") == [ticket]


def test_invalid_snapshot_fails_instead_of_reporting_empty_queue(tmp_path):
    snapshot = tmp_path / "issues.json"
    snapshot.write_text('{"message": "API failure"}', encoding="utf-8")
    result = subprocess.run(
        [sys.executable, str(SCRIPT), str(snapshot), "--kind", "tests"],
        capture_output=True, text=True,
    )
    assert result.returncode != 0
    assert result.stdout == ""


def test_empty_paginated_snapshot_is_valid(tmp_path):
    assert select(tmp_path, [[]], "tests") == []
