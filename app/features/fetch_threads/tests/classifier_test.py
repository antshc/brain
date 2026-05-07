#!/usr/bin/env python3
"""Tests for fetch_threads classifier and handler."""

import logging
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

# Add app/ to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

from domain.review_thread import ThreadLabel
from features.fetch_threads.classifier import classify_thread, detect_label
from features.fetch_threads.handler import fetch_and_classify_threads


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


def mock_gh(threads):
    """Patch fetch_review_threads to return given threads."""
    return patch(
        "features.fetch_threads.handler.gh_client.fetch_review_threads",
        return_value=threads,
    )


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
        assert result.discussion[0]["author"] == "reviewer"

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

    def test_unrecognized_label_returns_none(self, caplog):
        thread = make_thread("TX", "src/x.ts", 1, 1, "looks fine to me")
        with caplog.at_level(logging.WARNING):
            result = classify_thread(thread)
        assert result is None
        assert "Unrecognized label" in caplog.text


class TestFetchAndClassify:
    def test_fix_label(self):
        threads = [make_thread("T1", "src/foo.ts", 10, 15, "fix!: broken null check")]
        with mock_gh(threads):
            result = fetch_and_classify_threads("https://github.com/o/r/pull/1")
        assert len(result) == 1
        assert result[0].label == ThreadLabel.FIX
        assert result[0].thread_id == "T1"
        assert result[0].path == "src/foo.ts"
        assert result[0].lines == "10-15"

    def test_suggest_bang_label(self):
        threads = [make_thread("T2", "src/bar.ts", 5, 5, "suggest!: consider extracting method")]
        with mock_gh(threads):
            result = fetch_and_classify_threads("https://github.com/o/r/pull/1")
        assert len(result) == 1
        assert result[0].label == ThreadLabel.SUGGEST_BANG
        assert result[0].thread_id == "T2"

    def test_non_actionable_excluded(self):
        threads = [
            make_thread("N1", "src/b.ts", 2, 2, "nit: minor style issue"),
            make_thread("S1", "src/c.ts", 3, 3, "suggest: could improve"),
            make_thread("G1", "src/d.ts", 4, 4, "good: nice approach"),
        ]
        with mock_gh(threads):
            result = fetch_and_classify_threads("https://github.com/o/r/pull/1")
        assert len(result) == 0

    def test_priority_ordering(self):
        threads = [
            make_thread("S1", "src/a.ts", 1, 1, "suggest!: improve naming"),
            make_thread("F1", "src/b.ts", 2, 2, "fix!: crash on null"),
        ]
        with mock_gh(threads):
            result = fetch_and_classify_threads("https://github.com/o/r/pull/1")
        assert len(result) == 2
        assert result[0].label == ThreadLabel.FIX
        assert result[1].label == ThreadLabel.SUGGEST_BANG

    def test_no_threads(self):
        with mock_gh([]):
            result = fetch_and_classify_threads("https://github.com/o/r/pull/1")
        assert len(result) == 0

    def test_resolved_excluded(self):
        threads = [make_thread("TR", "src/r.ts", 1, 1, "fix!: old issue", resolved=True)]
        with mock_gh(threads):
            result = fetch_and_classify_threads("https://github.com/o/r/pull/1")
        assert len(result) == 0

    def test_mixed_labels(self):
        threads = [
            make_thread("F1", "a.ts", 1, 1, "fix!: crash"),
            make_thread("N1", "b.ts", 2, 2, "nit: spacing"),
            make_thread("S1", "c.ts", 3, 3, "suggest!: refactor"),
        ]
        with mock_gh(threads):
            result = fetch_and_classify_threads("https://github.com/o/r/pull/1")
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
        with mock_gh(threads):
            result = fetch_and_classify_threads("https://github.com/o/r/pull/1")
        assert len(result[0].discussion) == 2

    def test_single_line_thread(self):
        threads = [make_thread("TL", "src/l.ts", 7, 7, "fix!: off by one")]
        with mock_gh(threads):
            result = fetch_and_classify_threads("https://github.com/o/r/pull/1")
        assert result[0].lines == "7-7"
