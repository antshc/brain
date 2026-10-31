import json

from conftest import ME, MY_NAME, THEIR_NAME, THEM, comment, doc, issue, mention, page, text

from brief_daily.cli import main_mentions

RECENT = "2026-09-15T09:00:00.000+0300"
LATER = "2026-09-16T09:00:00.000+0300"
STALE = "2025-01-05T09:00:00.000+0300"


def run(capsys, *paths, cutoff_days=3650):
    args = []
    for path in paths:
        args += ["--content", path]
    main_mentions(
        args
        + [
            "--account-id",
            ME,
            "--cutoff-days",
            str(cutoff_days),
        ]
    )
    return json.loads(capsys.readouterr().out)


def test_matches_a_mention_by_account_id(spill, capsys):
    path = spill(page([issue("PROJ-1", comments=[comment(RECENT, body=mention(ME, MY_NAME))])]))
    report = run(capsys, path)
    assert [row["key"] for row in report["unanswered"]] == ["PROJ-1"]
    assert report["unanswered"][0]["mentionedBy"] == THEIR_NAME


def test_ignores_a_mention_of_somebody_else(spill, capsys):
    path = spill(page([issue("PROJ-1", comments=[comment(RECENT, body=mention(THEM, THEIR_NAME))])]))
    assert run(capsys, path)["unanswered"] == []


def test_ignores_a_mention_showing_your_name_for_another_account(spill, capsys):
    path = spill(page([issue("PROJ-1", comments=[comment(RECENT, body=mention(THEM, MY_NAME))])]))
    assert run(capsys, path)["unanswered"] == []


def test_matches_a_mention_nested_inside_other_blocks(spill, capsys):
    nested = {"type": "doc", "content": [{"type": "bulletList", "content": [{"type": "listItem", "content": [mention(ME, MY_NAME)["content"][0]]}]}]}
    path = spill(page([issue("PROJ-1", comments=[comment(RECENT, body=nested)])]))
    assert [row["key"] for row in run(capsys, path)["unanswered"]] == ["PROJ-1"]


def test_ignores_a_bare_account_id_in_a_comment_body(spill, capsys):
    path = spill(page([issue("PROJ-1", comments=[comment(RECENT, body=doc(text(f"cc {ME}")))])]))
    assert run(capsys, path)["unanswered"] == []


def test_buckets_a_reply_from_you_as_answered_by_you(spill, capsys):
    path = spill(
        page(
            [
                issue(
                    "PROJ-1",
                    comments=[
                        comment(RECENT, body=mention(ME, MY_NAME)),
                        comment(LATER, author=ME, name=MY_NAME),
                    ],
                )
            ]
        )
    )
    report = run(capsys, path)
    assert report["unanswered"] == []
    assert report["answeredByYou"][0]["answeredBy"] == "you"
    assert report["answeredByYou"][0]["answeredOn"] == "2026-09-16"


def test_buckets_a_third_party_reply_separately(spill, capsys):
    path = spill(
        page(
            [
                issue(
                    "PROJ-1",
                    comments=[
                        comment(RECENT, body=mention(ME, MY_NAME)),
                        comment(LATER, author="third", name="Alan Turing"),
                    ],
                )
            ]
        )
    )
    report = run(capsys, path)
    assert report["unanswered"] == []
    assert report["answeredByOther"][0]["answeredBy"] == "Alan Turing"


def test_prefers_your_own_reply_over_a_third_party_one(spill, capsys):
    path = spill(
        page(
            [
                issue(
                    "PROJ-1",
                    comments=[
                        comment(RECENT, body=mention(ME, MY_NAME)),
                        comment(LATER, author="third", name="Alan Turing"),
                        comment("2026-09-17T09:00:00.000+0300", author=ME, name=MY_NAME),
                    ],
                )
            ]
        )
    )
    report = run(capsys, path)
    assert report["answeredByOther"] == []
    assert report["answeredByYou"][0]["answeredBy"] == "you"


def test_a_reply_before_the_mention_does_not_answer_it(spill, capsys):
    path = spill(
        page(
            [
                issue(
                    "PROJ-1",
                    comments=[
                        comment(RECENT, author=ME, name=MY_NAME),
                        comment(LATER, body=mention(ME, MY_NAME)),
                    ],
                )
            ]
        )
    )
    assert [row["key"] for row in run(capsys, path)["unanswered"]] == ["PROJ-1"]


def test_excludes_an_issue_whose_every_mention_predates_the_cutoff(spill, capsys):
    path = spill(page([issue("PROJ-1", comments=[comment(STALE, body=mention(ME, MY_NAME))])]))
    report = run(capsys, path, cutoff_days=30)
    assert report["cutoffExcluded"] == ["PROJ-1"]
    assert report["unanswered"] == []


def test_keeps_an_issue_with_one_mention_inside_the_window(spill, capsys):
    path = spill(
        page(
            [
                issue(
                    "PROJ-1",
                    comments=[
                        comment(STALE, body=mention(ME, MY_NAME)),
                        comment(RECENT, body=mention(ME, MY_NAME)),
                    ],
                )
            ]
        )
    )
    report = run(capsys, path)
    assert report["cutoffExcluded"] == []
    assert report["unanswered"][0]["mentionedOn"] == "2026-09-15"


def test_sorts_newest_mention_first(spill, capsys):
    path = spill(
        page(
            [
                issue("PROJ-OLD", comments=[comment(RECENT, body=mention(ME, MY_NAME))]),
                issue("PROJ-NEW", comments=[comment(LATER, body=mention(ME, MY_NAME))]),
            ]
        )
    )
    assert [row["key"] for row in run(capsys, path)["unanswered"]] == ["PROJ-NEW", "PROJ-OLD"]


def test_merges_every_page_and_reports_truncation(spill, capsys):
    first = spill(
        page([issue("PROJ-1", comments=[comment(RECENT, body=mention(ME, MY_NAME))])], has_next=True)
    )
    second = spill(
        page([issue("PROJ-2", comments=[comment(LATER, body=mention(ME, MY_NAME))])], has_next=True)
    )
    report = run(capsys, first, second)
    assert {row["key"] for row in report["unanswered"]} == {"PROJ-1", "PROJ-2"}
    assert report["truncated"] is True


def test_flags_an_issue_whose_comment_thread_came_back_partial(spill, capsys):
    path = spill(
        page([issue("PROJ-1", comments=[comment(RECENT, body=mention(ME, MY_NAME))], total=40)])
    )
    assert run(capsys, path)["partialComments"] == ["PROJ-1"]


def test_ignores_a_comment_whose_body_has_no_content(spill, capsys):
    path = spill(page([issue("PROJ-1", comments=[comment(RECENT, body={"type": "doc"})])]))
    assert run(capsys, path)["unanswered"] == []


def test_reports_the_browse_url_from_the_payload(spill, capsys):
    path = spill(page([issue("PROJ-1", comments=[comment(RECENT, body=mention(ME, MY_NAME))])]))
    row = run(capsys, path)["unanswered"][0]
    assert row["url"] == "https://example.atlassian.net/browse/PROJ-1"
    assert row["status"] == "New"


def test_ignores_an_unrelated_author_accountid_collision(spill, capsys):
    path = spill(
        page(
            [
                issue(
                    "PROJ-1",
                    comments=[
                        comment(RECENT, body=mention(ME, MY_NAME)),
                        comment(LATER, author=THEM, name=MY_NAME),
                    ],
                )
            ]
        )
    )
    report = run(capsys, path)
    assert report["answeredByYou"] == []
    assert report["answeredByOther"][0]["answeredBy"] == MY_NAME
