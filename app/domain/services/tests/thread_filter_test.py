#!/usr/bin/env python3
"""Tests for review classifier."""

import sys
from pathlib import Path

import pytest

# Add app/ to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

from domain.comment import Comment
from domain.review_thread import ReviewThread
from domain.thread_classification_policy import ThreadClassificationPolicy
from domain.thread_label import ThreadLabel
from domain.services.thread_filter import ThreadFilter

_policy = ThreadClassificationPolicy()
detect_label = _policy.detect_label


def classify_thread(thread: dict) -> ReviewThread | None:
    """Build a ReviewThread from a raw dict using the domain policy."""
    raw_comments = thread.get("comments", [])
    comments = [Comment(author=c["author"]["login"], body=c["body"]) for c in raw_comments]
    start = thread.get("startLine") or thread.get("line")
    end = thread.get("line")
    try:
        return ReviewThread(
            thread_id=thread["id"],
            path=thread.get("path", ""),
            lines=f"{start}-{end}",
            is_resolved=thread.get("isResolved", False),
            comments=comments,
            policy=_policy,
        )
    except ValueError:
        return None


def classify_threads(raw_threads: list) -> list[ReviewThread]:
    threads = [t for raw in raw_threads if (t := classify_thread(raw)) is not None]
    return ThreadFilter().get_actionable_threads(threads)


# ── Helpers ────────────────────────────────────────────────────────────────────

def make_thread(id, path, start_line, end_line, body, resolved=False):
    return {
        "id": id,
        "isResolved": resolved,
        "path": path,
        "startLine": start_line,
        "line": end_line,
        "comments": [{"author": {"login": "reviewer"}, "body": body}],
    }


def make_thread_multi_comments(id, path, line, *bodies):
    return {
        "id": id,
        "isResolved": False,
        "path": path,
        "startLine": line,
        "line": line,
        "comments": [{"author": {"login": "reviewer"}, "body": b} for b in bodies],
    }


# ── Tests ──────────────────────────────────────────────────────────────────────

class TestDetectLabel:
    def test_fix_bang(self):
        assert detect_label("fix!: broken null check") == ThreadLabel.FIX

    def test_suggest_bang(self):
        assert detect_label("suggest!: consider extracting") == ThreadLabel.SUGGEST_BANG

    def test_suggest(self):
        assert detect_label("suggest: could improve") == ThreadLabel.SUGGEST

    def test_nit(self):
        assert detect_label("nit: minor style") == ThreadLabel.NIT

    def test_good(self):
        assert detect_label("good: nice approach") == ThreadLabel.GOOD

    def test_unrecognized(self):
        assert detect_label("looks fine to me") is None


class TestClassifyThread:
    def test_fix_thread(self):
        thread = make_thread("T1", "src/foo.ts", 10, 15, "fix!: broken null check")
        result = classify_thread(thread)
        assert result.label == ThreadLabel.FIX
        assert result.thread_id == "T1"
        assert result.path == "src/foo.ts"
        assert result.lines == "10-15"
        assert result.body == "fix!: broken null check"
        assert result.comments[0].author == "reviewer"

    def test_excluded_when_fixed(self):
        thread = make_thread_multi_comments(
            "T1", "src/foo.ts", 10, "fix!: issue", "Fixed."
        )
        assert classify_thread(thread) is None

    def test_excluded_when_question(self):
        thread = make_thread_multi_comments(
            "T1", "src/foo.ts", 10, "question!: why is this needed?"
        )
        assert classify_thread(thread) is None

    def test_label_in_later_comment(self):
        thread = make_thread_multi_comments(
            "T3", "src/foo.ts", 20, "LGTM overall", "fix!: but this part is wrong"
        )
        result = classify_thread(thread)
        assert result.label == ThreadLabel.FIX
        assert result.body == "fix!: but this part is wrong"

    def test_fix_after_question_returns_last_fix(self):
        """fix!: → question!: → fix!: — last fix wins, thread is NOT excluded."""
        thread = make_thread_multi_comments(
            "TFQ", "src/foo.ts", 10,
            "fix!: Expl",
            "question!: Clarification?",
            "fix!: new fix",
        )
        result = classify_thread(thread)
        assert result is not None
        assert result.label == ThreadLabel.FIX
        assert result.body == "fix!: new fix"

    def test_fix_then_question_excludes(self):
        """fix!: → question!: — question is last signal, thread excluded."""
        thread = make_thread_multi_comments(
            "TFQ2", "src/foo.ts", 10,
            "fix!: Expl",
            "question!: Clarification?",
        )
        assert classify_thread(thread) is None

    def test_fix_after_fixed_returns_last_fix(self):
        """fix!: → Fixed. → fix!: — last fix wins, thread is NOT excluded."""
        thread = make_thread_multi_comments(
            "TFF", "src/foo.ts", 10,
            "fix!: old issue",
            "Fixed.",
            "fix!: actually not fixed",
        )
        result = classify_thread(thread)
        assert result is not None
        assert result.label == ThreadLabel.FIX
        assert result.body == "fix!: actually not fixed"

    def test_unrecognized_label_returns_none(self):
        thread = make_thread("TX", "src/x.ts", 1, 1, "looks fine to me")
        assert classify_thread(thread) is None


class TestFetchAndClassify:
    def test_fix_label(self):
        threads = [make_thread("T1", "src/foo.ts", 10, 15, "fix!: broken null check")]
        result = classify_threads(threads)
        assert len(result) == 1
        assert result[0].label == ThreadLabel.FIX
        assert result[0].thread_id == "T1"
        assert result[0].path == "src/foo.ts"
        assert result[0].lines == "10-15"

    def test_suggest_bang_label(self):
        threads = [make_thread("T2", "src/bar.ts", 5, 5, "suggest!: consider extracting method")]
        result = classify_threads(threads)
        assert len(result) == 1
        assert result[0].label == ThreadLabel.SUGGEST_BANG
        assert result[0].thread_id == "T2"

    def test_non_actionable_excluded(self):
        threads = [
            make_thread("N1", "src/b.ts", 2, 2, "nit: minor style issue"),
            make_thread("S1", "src/c.ts", 3, 3, "suggest: could improve"),
            make_thread("G1", "src/d.ts", 4, 4, "good: nice approach"),
        ]
        result = classify_threads(threads)
        assert len(result) == 0

    def test_priority_ordering(self):
        threads = [
            make_thread("S1", "src/a.ts", 1, 1, "suggest!: improve naming"),
            make_thread("F1", "src/b.ts", 2, 2, "fix!: crash on null"),
        ]
        result = classify_threads(threads)
        assert len(result) == 2
        assert result[0].label == ThreadLabel.FIX
        assert result[1].label == ThreadLabel.SUGGEST_BANG

    def test_no_threads(self):
        result = classify_threads([])
        assert len(result) == 0

    def test_resolved_excluded(self):
        threads = [make_thread("TR", "src/r.ts", 1, 1, "fix!: old issue", resolved=True)]
        result = classify_threads(threads)
        assert len(result) == 0

    def test_mixed_labels(self):
        threads = [
            make_thread("F1", "a.ts", 1, 1, "fix!: crash"),
            make_thread("N1", "b.ts", 2, 2, "nit: spacing"),
            make_thread("S1", "c.ts", 3, 3, "suggest!: refactor"),
        ]
        result = classify_threads(threads)
        assert len(result) == 2
        assert result[0].label == ThreadLabel.FIX
        assert result[1].label == ThreadLabel.SUGGEST_BANG

    def test_discussion_includes_all_comments(self):
        threads = [
            make_thread_multi_comments(
                "TD", "src/d.ts", 5,
                "fix!: needs error handling",
                "Author: agreed, will fix",
            )
        ]
        result = classify_threads(threads)
        assert len(result[0].comments) == 2
