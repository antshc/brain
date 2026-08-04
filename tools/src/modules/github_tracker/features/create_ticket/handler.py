"""Create Ticket use case: creates a new labeled, milestoned issue."""

from ...infrastructure.gh_cli import GhCli
from ...shared.raw_mapping import parse_issue_number


def create_ticket(
    title: str, body: str, milestone_title: str, label: str, *, gh: GhCli | None = None
) -> int:
    """Create a new ticket and return its issue number."""
    gh = gh or GhCli()
    repo = gh.resolve_repo()
    issue_url = gh.issue_create(repo, title, body=body, label=label, milestone=milestone_title)
    return parse_issue_number(issue_url)
