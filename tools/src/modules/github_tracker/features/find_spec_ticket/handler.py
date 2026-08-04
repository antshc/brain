"""Find Spec Ticket use case: finds the open `spec`-labeled issue for a milestone title."""

from ...infrastructure.gh_cli import GhCli
from ...shared.raw_mapping import normalize_comments

_JSON_FIELDS = "number,title,body,comments"


def find_spec_ticket(milestone_title: str, *, gh: GhCli | None = None) -> dict | None:
    """Return the matching open spec ticket's number/title/body/comments, or None if not found."""
    gh = gh or GhCli()
    repo = gh.resolve_repo()

    matches = gh.issue_list_raw(repo, _JSON_FIELDS, milestone=milestone_title, label="spec", limit=1)
    if not matches:
        return None

    raw = matches[0]
    return {
        "number": raw["number"],
        "title": raw.get("title", ""),
        "body": raw.get("body", ""),
        "comments": normalize_comments(raw.get("comments", [])),
    }
