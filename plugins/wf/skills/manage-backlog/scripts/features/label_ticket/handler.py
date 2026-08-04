"""Label Ticket use case: adds and/or removes labels on an issue."""

from ...infrastructure.gh_cli import GhCli


def label_ticket(
    issue_number: int, add_labels: str, remove_labels: str, *, gh: GhCli | None = None
) -> None:
    """Add/remove labels on `issue_number`. Either `add_labels` or `remove_labels` may be empty."""
    gh = gh or GhCli()
    repo = gh.resolve_repo()
    gh.issue_edit_labels(repo, issue_number, add_labels=add_labels or None, remove_labels=remove_labels or None)
