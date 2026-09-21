import json

from conftest import CLOUD_ID, ME, MY_NAME, THEIR_NAME, THEM, comment, issue, mention, page

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
            "--cloud-id",
            CLOUD_ID,
            "--account-id",
            ME,
            "--display-name",
            MY_NAME,
            "--cutoff-days",
            str(cutoff_days),
        ]
    )
    return json.loads(capsys.readouterr().out)


def test_matches_a_mention_by_display_name(spill, capsys):
    path = spill(page([issue("ZIC-1", comments=[comment(RECENT, body=mention(MY_NAME))])]))
    report = run(capsys, path)
    assert [row["key"] for row in report["unanswered"]] == ["ZIC-1"]
    assert report["unanswered"][0]["mentionedBy"] == THEIR_NAME


def test_ignores_a_mention_of_somebody_else(spill, capsys):
    path = spill(page([issue("ZIC-1", comments=[comment(RECENT, body=mention(THEIR_NAME))])]))
    assert run(capsys, path)["unanswered"] == []


def test_does_not_treat_the_data_id_placeholder_as_an_account_id(spill, capsys):
    body = f'<custom data-type="mention" data-id="{ME}">@{THEIR_NAME}</custom>'
    path = spill(page([issue("ZIC-1", comments=[comment(RECENT, body=body)])]))
    assert run(capsys, path)["unanswered"] == []


def test_ignores_a_bare_account_id_in_a_comment_body(spill, capsys):
    path = spill(page([issue("ZIC-1", comments=[comment(RECENT, body=f"cc {ME}")])]))
    assert run(capsys, path)["unanswered"] == []


def test_buckets_a_reply_from_you_as_answered_by_you(spill, capsys):
    path = spill(
        page(
            [
                issue(
                    "ZIC-1",
                    comments=[
                        comment(RECENT, body=mention(MY_NAME)),
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
                    "ZIC-1",
                    comments=[
                        comment(RECENT, body=mention(MY_NAME)),
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
                    "ZIC-1",
                    comments=[
                        comment(RECENT, body=mention(MY_NAME)),
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
                    "ZIC-1",
                    comments=[
                        comment(RECENT, author=ME, name=MY_NAME),
                        comment(LATER, body=mention(MY_NAME)),
                    ],
                )
            ]
        )
    )
    assert [row["key"] for row in run(capsys, path)["unanswered"]] == ["ZIC-1"]


def test_excludes_an_issue_whose_every_mention_predates_the_cutoff(spill, capsys):
    path = spill(page([issue("ZIC-1", comments=[comment(STALE, body=mention(MY_NAME))])]))
    report = run(capsys, path, cutoff_days=30)
    assert report["cutoffExcluded"] == ["ZIC-1"]
    assert report["unanswered"] == []


def test_keeps_an_issue_with_one_mention_inside_the_window(spill, capsys):
    path = spill(
        page(
            [
                issue(
                    "ZIC-1",
                    comments=[
                        comment(STALE, body=mention(MY_NAME)),
                        comment(RECENT, body=mention(MY_NAME)),
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
                issue("ZIC-OLD", comments=[comment(RECENT, body=mention(MY_NAME))]),
                issue("ZIC-NEW", comments=[comment(LATER, body=mention(MY_NAME))]),
            ]
        )
    )
    assert [row["key"] for row in run(capsys, path)["unanswered"]] == ["ZIC-NEW", "ZIC-OLD"]


def test_merges_every_page_and_reports_truncation(spill, capsys):
    first = spill(
        page([issue("ZIC-1", comments=[comment(RECENT, body=mention(MY_NAME))])], has_next=True)
    )
    second = spill(
        page([issue("ZIC-2", comments=[comment(LATER, body=mention(MY_NAME))])], has_next=True)
    )
    report = run(capsys, first, second)
    assert {row["key"] for row in report["unanswered"]} == {"ZIC-1", "ZIC-2"}
    assert report["truncated"] is True


def test_flags_an_issue_whose_comment_thread_came_back_partial(spill, capsys):
    path = spill(
        page([issue("ZIC-1", comments=[comment(RECENT, body=mention(MY_NAME))], total=40)])
    )
    assert run(capsys, path)["partialComments"] == ["ZIC-1"]


def test_ignores_a_comment_whose_body_is_not_a_string(spill, capsys):
    path = spill(page([issue("ZIC-1", comments=[comment(RECENT, body={"type": "doc"})])]))
    assert run(capsys, path)["unanswered"] == []


def test_reports_the_browse_url_from_the_payload(spill, capsys):
    path = spill(page([issue("ZIC-1", comments=[comment(RECENT, body=mention(MY_NAME))])]))
    row = run(capsys, path)["unanswered"][0]
    assert row["url"] == "https://example.atlassian.net/browse/ZIC-1"
    assert row["status"] == "New"


def test_a_display_name_with_regex_characters_is_matched_literally(spill, capsys):
    tricky = "A. Lovelace (Dr.)"
    path = spill(page([issue("ZIC-1", comments=[comment(RECENT, body=mention(tricky))])]))
    main_mentions(
        [
            "--content",
            path,
            "--cloud-id",
            CLOUD_ID,
            "--account-id",
            ME,
            "--display-name",
            tricky,
            "--cutoff-days",
            "3650",
        ]
    )
    assert len(json.loads(capsys.readouterr().out)["unanswered"]) == 1


def test_a_mention_of_a_name_that_merely_starts_with_yours_is_ignored(spill, capsys):
    path = spill(page([issue("ZIC-1", comments=[comment(RECENT, body=mention(MY_NAME + " Jr"))])]))
    assert run(capsys, path)["unanswered"] == []


def test_ignores_an_unrelated_author_accountid_collision(spill, capsys):
    path = spill(
        page(
            [
                issue(
                    "ZIC-1",
                    comments=[
                        comment(RECENT, body=mention(MY_NAME)),
                        comment(LATER, author=THEM, name=MY_NAME),
                    ],
                )
            ]
        )
    )
    report = run(capsys, path)
    assert report["answeredByYou"] == []
    assert report["answeredByOther"][0]["answeredBy"] == MY_NAME
