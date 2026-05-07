"""Classify review threads by priority."""

from domain.review_thread import ReviewThread
from domain.thread_label import ThreadLabel


class ThreadClassifier:
    """Filters and sorts ReviewThread entities by priority."""

    def classify(self, threads: list[ReviewThread]) -> list[ReviewThread]:
        """Return actionable, unresolved threads sorted fix! before suggest!."""
        fix_threads = [t for t in threads if not t.is_resolved and t.label == ThreadLabel.FIX]
        suggest_threads = [t for t in threads if not t.is_resolved and t.label == ThreadLabel.SUGGEST_BANG]
        return fix_threads + suggest_threads
