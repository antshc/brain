"""Thin wrapper around the `gh` CLI for issue/milestone/label write operations.

Every method shells out to `gh` and returns either raw JSON (parsed) or nothing;
no domain mapping happens here. Repo resolution mirrors the label-creation
script's own method (`gh repo view --json nameWithOwner`) — never an unset
shell variable.
"""

import json
import subprocess


class GhCli:
    """Executes `gh` CLI commands for the ticket-tracker write operations `manage-backlog` needs."""

    def resolve_repo(self) -> str:
        """Run `gh repo view --json nameWithOwner` and return `<owner>/<repo>`."""
        result = subprocess.run(
            ["gh", "repo", "view", "--json", "nameWithOwner", "-q", ".nameWithOwner"],
            capture_output=True, text=True, check=True,
        )
        return result.stdout.strip()

    def label_names(self, repo: str) -> list[str]:
        """Run `gh label list` and return the existing label names."""
        result = subprocess.run(
            ["gh", "label", "list", "--repo", repo, "--json", "name"],
            capture_output=True, text=True, check=True,
        )
        return [item["name"] for item in json.loads(result.stdout)]

    def label_create(self, repo: str, name: str, color: str, description: str) -> None:
        """Run `gh label create` for a single label."""
        subprocess.run(
            ["gh", "label", "create", name, "--repo", repo, "--color", color, "--description", description],
            capture_output=True, text=True, check=True,
        )

    def milestones_raw(self, repo: str) -> list[dict]:
        """Run `gh api repos/<repo>/milestones` (open milestones) and return the parsed JSON list."""
        result = subprocess.run(
            ["gh", "api", f"repos/{repo}/milestones"],
            capture_output=True, text=True, check=True,
        )
        return json.loads(result.stdout)

    def milestone_create_raw(self, repo: str, title: str, description: str) -> dict:
        """Run `gh api repos/<repo>/milestones --method POST` and return the created milestone JSON."""
        result = subprocess.run(
            [
                "gh", "api", f"repos/{repo}/milestones",
                "--method", "POST",
                "--field", f"title={title}",
                "--field", f"description={description}",
            ],
            capture_output=True, text=True, check=True,
        )
        return json.loads(result.stdout)

    def issue_create(
        self,
        repo: str,
        title: str,
        *,
        body: str | None = None,
        label: str | None = None,
        milestone: str | None = None,
    ) -> str:
        """Run `gh issue create` and return the created issue's URL (as printed to stdout)."""
        cmd = ["gh", "issue", "create", "--repo", repo, "--title", title]
        if body is not None:
            cmd += ["--body", body]
        if label is not None:
            cmd += ["--label", label]
        if milestone is not None:
            cmd += ["--milestone", milestone]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return result.stdout.strip()

    def issue_edit_milestone(self, repo: str, issue_number: int, milestone_title: str) -> None:
        """Run `gh issue edit --milestone` to (re)assign an issue's milestone."""
        subprocess.run(
            ["gh", "issue", "edit", str(issue_number), "--repo", repo, "--milestone", milestone_title],
            capture_output=True, text=True, check=True,
        )

    def issue_view_raw(self, repo: str, issue_number: int, json_fields: str) -> dict:
        """Run `gh issue view --json <fields>` and return the parsed JSON object."""
        result = subprocess.run(
            ["gh", "issue", "view", str(issue_number), "--repo", repo, "--json", json_fields],
            capture_output=True, text=True, check=True,
        )
        return json.loads(result.stdout)

    def issue_list_raw(
        self,
        repo: str,
        json_fields: str,
        *,
        milestone: str | None = None,
        label: str | None = None,
        state: str | None = None,
        limit: int | None = None,
    ) -> list[dict]:
        """Run `gh issue list --json <fields>` and return the parsed JSON list."""
        cmd = ["gh", "issue", "list", "--repo", repo, "--json", json_fields]
        if milestone is not None:
            cmd += ["--milestone", milestone]
        if label is not None:
            cmd += ["--label", label]
        if state is not None:
            cmd += ["--state", state]
        if limit is not None:
            cmd += ["--limit", str(limit)]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return json.loads(result.stdout)

    def issue_comment(self, repo: str, issue_number: int, body: str) -> None:
        """Run `gh issue comment --body`."""
        subprocess.run(
            ["gh", "issue", "comment", str(issue_number), "--repo", repo, "--body", body],
            capture_output=True, text=True, check=True,
        )

    def issue_edit_labels(
        self, repo: str, issue_number: int, *, add_labels: str | None = None, remove_labels: str | None = None
    ) -> None:
        """Run `gh issue edit --add-label/--remove-label`. Either may be omitted."""
        cmd = ["gh", "issue", "edit", str(issue_number), "--repo", repo]
        if add_labels:
            cmd += ["--add-label", add_labels]
        if remove_labels:
            cmd += ["--remove-label", remove_labels]
        subprocess.run(cmd, capture_output=True, text=True, check=True)

    def issue_close(self, repo: str, issue_number: int, *, comment: str | None = None) -> None:
        """Run `gh issue close`, optionally with a closing comment."""
        cmd = ["gh", "issue", "close", str(issue_number), "--repo", repo]
        if comment:
            cmd += ["--comment", comment]
        subprocess.run(cmd, capture_output=True, text=True, check=True)
