import json

import pytest
from conftest import CLOUD_ID, issue, page

from brief_daily.cli import main_blocked


def blocked_issue(key, **fields):
    defaults = {
        "issuetype": {"name": "Story"},
        "priority": {"name": "P2"},
        "updated": "2026-09-17T19:29:59.356+0300",
    }
    return issue(key, comments=[], **{**defaults, **fields})


def test_maps_a_node_to_a_report_row(spill, capsys):
    path = spill(page([blocked_issue("ZIC-1", status="Blocked")]))
    main_blocked(["--content", path, "--cloud-id", CLOUD_ID])
    assert json.loads(capsys.readouterr().out) == {
        "rows": [
            {
                "key": "ZIC-1",
                "url": "https://example.atlassian.net/browse/ZIC-1",
                "summary": "A summary",
                "type": "Story",
                "status": "Blocked",
                "priority": "P2",
                "updated": "2026-09-17",
            }
        ],
        "truncated": False,
    }


def test_sorts_newest_updated_first(spill, capsys):
    path = spill(
        page(
            [
                blocked_issue("ZIC-OLD", updated="2026-08-01T10:00:00.000+0300"),
                blocked_issue("ZIC-NEW", updated="2026-09-18T10:00:00.000+0300"),
            ]
        )
    )
    main_blocked(["--content", path, "--cloud-id", CLOUD_ID])
    rows = json.loads(capsys.readouterr().out)["rows"]
    assert [row["key"] for row in rows] == ["ZIC-NEW", "ZIC-OLD"]


def test_merges_every_page_and_reports_truncation(spill, capsys):
    first = spill(page([blocked_issue("ZIC-1")], has_next=True))
    second = spill(page([blocked_issue("ZIC-2")], has_next=True))
    main_blocked(["--content", first, "--content", second, "--cloud-id", CLOUD_ID])
    report = json.loads(capsys.readouterr().out)
    assert {row["key"] for row in report["rows"]} == {"ZIC-1", "ZIC-2"}
    assert report["truncated"] is True


def test_tolerates_an_issue_without_a_priority(spill, capsys):
    path = spill(page([blocked_issue("ZIC-1", priority=None)]))
    main_blocked(["--content", path, "--cloud-id", CLOUD_ID])
    assert json.loads(capsys.readouterr().out)["rows"][0]["priority"] is None


def test_exits_naming_a_missing_content_file(tmp_path, capsys):
    with pytest.raises(SystemExit):
        main_blocked(["--content", str(tmp_path / "absent.json"), "--cloud-id", CLOUD_ID])
    assert "absent.json" in capsys.readouterr().err
