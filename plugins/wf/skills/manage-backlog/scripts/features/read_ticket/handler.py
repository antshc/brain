"""Read Ticket use case: fetches one ticket's full details by issue number."""

from ...infrastructure.gh_cli import GhCli
from ...shared.raw_mapping import ticket_from_raw

_JSON_FIELDS = "number,title,body,labels,comments"


def read_ticket(issue_number: int, *, gh: GhCli | None = None) -> dict:
    """Return the ticket's number, title, body, labels, and comments."""
    gh = gh or GhCli()
    repo = gh.resolve_repo()
    raw = gh.issue_view_raw(repo, issue_number, _JSON_FIELDS)
    return ticket_from_raw(raw)
