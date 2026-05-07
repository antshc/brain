"""Entry point: fetch and classify review threads for a PR URL."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from domain.review_thread import ReviewThread
from features.fetch_threads import classifier
from infrastructure import gh_client
from shared.pr_url import parse_pr_url


def fetch_and_classify_threads(pr_url: str) -> list[ReviewThread]:
    """Fetch unresolved review threads and return actionable ones, sorted by priority."""
    owner, repo, number = parse_pr_url(pr_url)
    raw_threads = gh_client.fetch_review_threads(owner, repo, number)

    fix_threads: list[ReviewThread] = []
    suggest_threads: list[ReviewThread] = []

    for thread in raw_threads:
        if thread.get("isResolved"):
            continue
        classified = classifier.classify_thread(thread)
        if not classified or not classified.label.is_actionable():
            continue
        if classified.label.value == "fix!":
            fix_threads.append(classified)
        else:
            suggest_threads.append(classified)

    return fix_threads + suggest_threads
