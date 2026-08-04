"""Publish Spec use case: reuses or creates the capability milestone for a feature ID,
then creates the spec issue and assigns it to that milestone.
"""

from ...infrastructure.gh_cli import GhCli
from ...shared.raw_mapping import parse_issue_number


def publish_spec(feature_id: str, spec_title: str, target_branch: str, *, gh: GhCli | None = None) -> int:
    """Publish the spec issue for `feature_id`/`spec_title` and return its issue number.

    Reuses an existing milestone whose title starts with `feature_id` unchanged; only
    creates (and never renames) a milestone when none matches.
    """
    gh = gh or GhCli()
    repo = gh.resolve_repo()

    milestone_title = _find_milestone_title(gh, repo, feature_id)
    if milestone_title is None:
        description = f"**Feature ID:** `{feature_id}`\n**Target Branch:** `{target_branch}`"
        created = gh.milestone_create_raw(repo, f"{feature_id}: {spec_title}", description)
        milestone_title = created["title"]

    issue_url = gh.issue_create(repo, f"{feature_id}: {spec_title}", label="spec")
    issue_number = parse_issue_number(issue_url)
    gh.issue_edit_milestone(repo, issue_number, milestone_title)
    return issue_number


def _find_milestone_title(gh: GhCli, repo: str, feature_id: str) -> str | None:
    """Return the title of the first open milestone whose title starts with `feature_id`, if any."""
    for milestone in gh.milestones_raw(repo):
        title = milestone.get("title", "")
        if title.startswith(feature_id):
            return title
    return None
