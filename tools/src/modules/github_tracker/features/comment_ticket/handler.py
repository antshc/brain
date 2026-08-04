"""Comment On Ticket use case: adds a comment to an issue."""

from ...infrastructure.gh_cli import GhCli


def comment_ticket(issue_number: int, body: str, *, gh: GhCli | None = None) -> None:
    """Add `body` as a comment on `issue_number`."""
    gh = gh or GhCli()
    repo = gh.resolve_repo()
    gh.issue_comment(repo, issue_number, body)
