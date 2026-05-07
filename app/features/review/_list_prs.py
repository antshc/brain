"""Lists open PRs authored by a user in a given repo."""

from domain.pull_request import PullRequest
from infrastructure import gh_client
from shared.pr_url import parse_pr_url


def list_prs(user: str, repo: str) -> list[PullRequest]:
    """Return open PRs authored by *user* in *repo* as PullRequest domain objects."""
    urls = gh_client.list_open_prs(user, repo)
    result = []
    for url in urls:
        owner, repo_name, number = parse_pr_url(url)
        result.append(PullRequest(owner=owner, repo=repo_name, number=number, url=url))
    return result
