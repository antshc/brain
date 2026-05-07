import re

from domain.comment import Comment
from domain.thread_label import ThreadLabel


class ThreadClassificationPolicy:
    """Rules for classifying a review thread from its comments."""

    _LABEL_PATTERNS: list[tuple[ThreadLabel, re.Pattern]] = [
        (ThreadLabel.FIX, re.compile(r"fix!:")),
        (ThreadLabel.SUGGEST_BANG, re.compile(r"suggest!:")),
        (ThreadLabel.SUGGEST, re.compile(r"suggest:")),
        (ThreadLabel.NIT, re.compile(r"nit:")),
        (ThreadLabel.GOOD, re.compile(r"good:")),
        (ThreadLabel.QUESTION, re.compile(r"question!:")),
    ]
    _EXCLUDED_KEYWORDS = {"fixed.", "question!:"}

    def detect_label(self, body: str) -> ThreadLabel | None:
        """Return the first matching ThreadLabel in *body*, or None."""
        for label, pattern in self._LABEL_PATTERNS:
            if pattern.search(body):
                return label
        return None

    def classify_comments(self, comments: list[Comment]) -> tuple[str, ThreadLabel] | None:
        """Scan comments in reverse to find the authoritative label.

        Returns (body, label) or None if the thread is excluded or unclassifiable.
        """
        body = None
        for comment in reversed(comments):
            text = comment.body
            if any(keyword in text.lower() for keyword in self._EXCLUDED_KEYWORDS):
                return None
            if self.detect_label(text):
                body = text
                break

        if body is None:
            body = comments[0].body if comments else ""

        label = self.detect_label(body)
        if not label:
            return None

        return body, label
