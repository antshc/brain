"""Close Ticket use case: closes an issue, optionally with a closing comment."""

from ...infrastructure.gh_cli import GhCli


def close_ticket(issue_number: int, comment: str, *, gh: GhCli | None = None) -> None:
    """Close `issue_number`. `comment` may be empty to close without a closing comment."""
    gh = gh or GhCli()
    repo = gh.resolve_repo()
    gh.issue_close(repo, issue_number, comment=comment or None)
