"""Fetch Issues use case: fetches actionable open issues for an owner/repo."""

from ...domain.services.issue_filter import IssueFilter
from ...infrastructure.vcs_client import VCSClient


def fetch_issues(
    owner: str,
    repo: str,
    *,
    vcs: VCSClient | None = None,
) -> list[dict]:
    """Fetch and return actionable open issues as serialisable dicts.

    The returned shape:
        {
            "number": int,
            "title": str,
            "body": str,
            "url": str,
            "labels": list[str],
            "comments": [{"id": str, "body": str, "created_at": str}],
        }

    Args:
        owner: Repository owner (e.g. "octocat").
        repo:  Repository name (e.g. "hello-world").
        vcs:   VCSClient instance (defaults to VCSClient()).
    """
    vcs = vcs or VCSClient()
    issue_filter = IssueFilter()

    issues = vcs.fetch_issues(owner, repo)
    actionable = issue_filter.get_actionable_issues(issues)

    return [_issue_to_dict(i) for i in actionable]


def _issue_to_dict(issue) -> dict:
    return {
        "number": issue.number,
        "title": issue.title,
        "body": issue.body,
        "url": issue.url,
        "labels": issue.labels,
        "comments": [
            {"id": c.id, "body": c.body, "created_at": c.updated_at}
            for c in issue.comments
        ],
    }
