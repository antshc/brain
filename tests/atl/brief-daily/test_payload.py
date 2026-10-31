from datetime import datetime, timedelta, timezone

from conftest import issue, page

from brief_daily.payload import cutoff_from, nodes, parse_timestamp, to_date, truncated


def test_parses_the_compact_offset_jira_returns():
    assert parse_timestamp("2026-09-17T19:29:59.356+0300") == datetime(
        2026, 9, 17, 19, 29, 59, 356000, tzinfo=timezone(timedelta(hours=3))
    )


def test_parses_a_zulu_timestamp():
    assert parse_timestamp("2026-09-17T16:29:59.356Z").tzinfo == timezone.utc


def test_compares_across_differing_offsets():
    assert parse_timestamp("2026-09-17T19:00:00.000+0300") == parse_timestamp(
        "2026-09-17T16:00:00.000+0000"
    )


def test_renders_the_date_in_the_stamps_own_offset():
    assert to_date("2026-09-17T23:30:00.000+0300") == "2026-09-17"


def test_cutoff_counts_back_from_the_injected_now():
    now = datetime(2026, 9, 19, tzinfo=timezone.utc)
    assert cutoff_from(30, now=now) == datetime(2026, 8, 20, tzinfo=timezone.utc)


def test_reads_the_issues_under_data():
    assert [node["key"] for node in nodes([page([issue("PROJ-1", comments=[])])])] == ["PROJ-1"]


def test_merges_issues_across_pages():
    pages = [page([issue("PROJ-1", comments=[])]), page([issue("PROJ-2", comments=[])])]
    assert [node["key"] for node in nodes(pages)] == ["PROJ-1", "PROJ-2"]


def test_truncated_reads_page_info_on_the_last_page():
    assert truncated([page([issue("PROJ-1", comments=[])], has_next=True)]) is True
    assert truncated([page([issue("PROJ-1", comments=[])], has_next=False)]) is False


def test_truncated_is_false_for_no_pages():
    assert truncated([]) is False
