"""Thin wrapper around the VCS host CLI (`gh`) for GraphQL and REST operations."""

import json
import logging
import subprocess

from domain.comment import Comment
from domain.pull_request import PullRequest
from domain.review_thread import ReviewThread
from domain.thread_classification_policy import ThreadClassificationPolicy
from shared.pr_url import parse_pr_url

logger = logging.getLogger(__name__)

_REVIEW_THREADS_QUERY = """
query($owner: String!, $repo: String!, $number: Int!) {
  repository(owner: $owner, name: $repo) {
    pullRequest(number: $number) {
      reviewThreads(first: 100) {
        nodes {
          id isResolved path line startLine
          comments(first: 50) {
            nodes { author { login } body }
          }
        }
      }
    }
  }
}
"""


class VCSClient:
    """Thin wrapper around the VCS host CLI for PR and review thread operations."""

    def __init__(self) -> None:
        self._policy = ThreadClassificationPolicy()

    def list_prs(self, user: str, repo: str) -> list[PullRequest]:
        """Return open PRs authored by *user* in *repo* as PullRequest domain objects."""
        urls = self._list_open_prs(user, repo)
        result = []
        for url in urls:
            owner, repo_name, number = parse_pr_url(url)
            result.append(PullRequest(owner=owner, repo=repo_name, number=number, url=url))
        return result

    def checkout_pr(self, pr_url: str) -> None:
        """Check out a PR branch locally."""
        subprocess.run(["gh", "pr", "checkout", pr_url], check=True)

    def fetch_review_threads(self, owner: str, repo: str, number: int) -> list[ReviewThread]:
        """Fetch review threads for a PR via GraphQL.

        Returns classified ReviewThread domain entities (excluded/unclassifiable threads omitted).
        """
        data = self._graphql(_REVIEW_THREADS_QUERY, {"owner": owner, "repo": repo, "number": number})
        nodes = data["data"]["repository"]["pullRequest"]["reviewThreads"]["nodes"]
        for node in nodes:
            node["comments"] = node["comments"]["nodes"]
        return [t for node in nodes if (t := self._thread_from_raw(node)) is not None]

    def _graphql(self, query: str, variables: dict | None = None) -> dict:
        """Execute a GraphQL query via `gh api graphql` and return the parsed JSON response."""
        cmd = ["gh", "api", "graphql", "-f", f"query={query}"]
        for key, value in (variables or {}).items():
            flag = "-F" if isinstance(value, (int, float)) else "-f"
            cmd.extend([flag, f"{key}={value}"])
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return json.loads(result.stdout)

    def _list_open_prs(self, user: str, repo: str) -> list[str]:
        """List open PR URLs authored by the given user in the repo."""
        result = subprocess.run(
            [
                "gh", "pr", "list",
                "--repo", repo,
                "--author", user,
                "--state", "open",
                "--json", "url",
                "--jq", ".[].url",
            ],
            capture_output=True, text=True, check=True,
        )
        return [url.strip() for url in result.stdout.strip().splitlines() if url.strip()]

    def _thread_from_raw(self, raw: dict) -> ReviewThread | None:
        """Map a raw GitHub API thread dict to a ReviewThread domain entity."""
        comments = [Comment(author=c["author"]["login"], body=c["body"]) for c in raw.get("comments", [])]
        start = raw.get("startLine") or raw.get("line")
        end = raw.get("line")
        try:
            return ReviewThread(
                thread_id=raw["id"],
                path=raw.get("path", ""),
                lines=f"{start}-{end}",
                is_resolved=raw.get("isResolved", False),
                comments=comments,
                policy=self._policy,
            )
        except ValueError:
            logger.debug("Thread excluded or unclassifiable: %s", raw["id"])
            return None
