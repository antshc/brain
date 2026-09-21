from datetime import datetime, timedelta, timezone

from conftest import CLOUD_ID, issue, page

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


def test_reads_the_flat_issues_list_the_live_mcp_returns():
    flat_page = {"issues": [issue("ZIC-1", comments=[])], "isLast": True}
    assert [node["key"] for node in nodes([flat_page], cloud_id=CLOUD_ID)] == ["ZIC-1"]


def test_reads_a_legacy_nested_nodes_envelope():
    nested_page = {"issues": {"nodes": [issue("ZIC-1", comments=[])]}}
    assert [node["key"] for node in nodes([nested_page], cloud_id=CLOUD_ID)] == ["ZIC-1"]


def test_synthesizes_web_url_from_cloud_id_and_key():
    flat_page = {"issues": [issue("ZIC-1", comments=[])], "isLast": True}
    assert nodes([flat_page], cloud_id=CLOUD_ID)[0]["webUrl"] == f"{CLOUD_ID}/browse/ZIC-1"


def test_keeps_an_existing_web_url_instead_of_overwriting_it():
    with_url = issue("ZIC-1", comments=[])
    with_url["webUrl"] = "https://other.atlassian.net/browse/ZIC-1"
    flat_page = {"issues": [with_url], "isLast": True}
    assert nodes([flat_page], cloud_id=CLOUD_ID)[0]["webUrl"] == "https://other.atlassian.net/browse/ZIC-1"


def test_truncated_reads_isLast_on_the_flat_shape():
    assert truncated([page([issue("ZIC-1", comments=[])], has_next=True)]) is True
    assert truncated([page([issue("ZIC-1", comments=[])], has_next=False)]) is False


def test_truncated_reads_pageInfo_on_the_legacy_nested_shape():
    nested_page = {"issues": {"nodes": [], "pageInfo": {"hasNextPage": True}}}
    assert truncated([nested_page]) is True


def test_truncated_is_false_for_no_pages():
    assert truncated([]) is False
