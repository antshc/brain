"""Thin wrapper around the VCS host CLI (`gh`) for GraphQL and REST operations."""

import logging

from ralph_tools.domain.comment import Comment
from ralph_tools.domain.pull_request import PullRequest
from ralph_tools.domain.review_thread import ReviewThread
from ralph_tools.infrastructure.gh_cli import GhCli
from ralph_tools.shared.pr_url import parse_pr_url

logger = logging.getLogger(__name__)


class VCSClient:
    """Thin wrapper around the VCS host CLI for PR and review thread operations."""

    def __init__(self, *, gh: GhCli | None = None) -> None:
        self._gh = gh or GhCli()

    def list_prs(self, user: str, repo: str) -> list[PullRequest]:
        """Return open PRs authored by *user* in *repo* as PullRequest domain objects."""
        prs = self._gh.pr_list(user, repo)
        result = []
        for url in [pr["url"] for pr in prs]:
            owner, repo_name, number = parse_pr_url(url)
            result.append(PullRequest(owner=owner, repo=repo_name, number=number, url=url))
        return result

    def checkout_pr(self, pr_url: str) -> None:
        """Check out a PR branch locally."""
        self._gh.pr_checkout(pr_url)

    def fetch_review_threads(self, owner: str, repo: str, number: int) -> list[ReviewThread]:
        """Fetch review threads for a PR via GraphQL."""
        nodes = self._gh.fetch_threads_raw(owner, repo, number)
        return [self._thread_from_raw(node) for node in nodes]

    def _thread_from_raw(self, raw: dict) -> ReviewThread:
        """Map a raw GitHub API thread dict to a ReviewThread domain entity."""
        comments = [Comment(author=c["author"]["login"], body=c["body"]) for c in raw.get("comments", [])]
        start = raw.get("startLine") or raw.get("line")
        end = raw.get("line")
        return ReviewThread(
            thread_id=raw["id"],
            path=raw.get("path", ""),
            lines=f"{start}-{end}",
            is_resolved=raw.get("isResolved", False),
            comments=comments,
        )
