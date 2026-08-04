"""List Tickets use case: lists tickets matching a state and label."""

from ...infrastructure.gh_cli import GhCli
from ...shared.raw_mapping import ticket_from_raw

_JSON_FIELDS = "number,title,body,labels,comments"


def list_tickets(state: str, label: str, *, gh: GhCli | None = None) -> list[dict]:
    """Return every matching ticket's number, title, body, labels, and comments."""
    gh = gh or GhCli()
    repo = gh.resolve_repo()
    raw_tickets = gh.issue_list_raw(repo, _JSON_FIELDS, label=label, state=state)
    return [ticket_from_raw(raw) for raw in raw_tickets]
