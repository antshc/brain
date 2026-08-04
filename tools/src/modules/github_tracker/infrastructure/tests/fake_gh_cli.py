"""Test double for GhCli — returns configured data without spawning subprocesses."""

from ..gh_cli import GhCli


class FakeGhCli(GhCli):
    """In-memory GhCli substitute for use in tests.

    Usage::

        gh = FakeGhCli(repo="owner/repo", label_names_output=["hitl"])
        result = setup_labels(gh=gh)
    """

    def __init__(
        self,
        *,
        repo: str = "owner/repo",
        label_names_output: list[str] | None = None,
        milestones_raw_output: list[dict] | None = None,
        milestone_create_raw_output: dict | None = None,
        issue_create_output: str = "https://github.com/owner/repo/issues/1",
        issue_view_raw_output: dict | None = None,
        issue_list_raw_output: list[dict] | None = None,
    ) -> None:
        self._repo = repo
        self._label_names_output = label_names_output or []
        self._milestones_raw_output = milestones_raw_output or []
        self._milestone_create_raw_output = milestone_create_raw_output or {}
        self._issue_create_output = issue_create_output
        self._issue_view_raw_output = issue_view_raw_output or {}
        self._issue_list_raw_output = issue_list_raw_output or []

        self.label_create_calls: list[tuple[str, str, str, str]] = []
        self.milestone_create_calls: list[tuple[str, str, str]] = []
        self.issue_create_calls: list[dict] = []
        self.issue_edit_milestone_calls: list[tuple[str, int, str]] = []
        self.issue_comment_calls: list[tuple[str, int, str]] = []
        self.issue_edit_labels_calls: list[dict] = []
        self.issue_close_calls: list[dict] = []

    def resolve_repo(self) -> str:
        return self._repo

    def label_names(self, repo: str) -> list[str]:
        return self._label_names_output

    def label_create(self, repo: str, name: str, color: str, description: str) -> None:
        self.label_create_calls.append((repo, name, color, description))

    def milestones_raw(self, repo: str) -> list[dict]:
        return self._milestones_raw_output

    def milestone_create_raw(self, repo: str, title: str, description: str) -> dict:
        self.milestone_create_calls.append((repo, title, description))
        return self._milestone_create_raw_output or {"title": title}

    def issue_create(
        self,
        repo: str,
        title: str,
        *,
        body: str | None = None,
        label: str | None = None,
        milestone: str | None = None,
    ) -> str:
        self.issue_create_calls.append(
            {"repo": repo, "title": title, "body": body, "label": label, "milestone": milestone}
        )
        return self._issue_create_output

    def issue_edit_milestone(self, repo: str, issue_number: int, milestone_title: str) -> None:
        self.issue_edit_milestone_calls.append((repo, issue_number, milestone_title))

    def issue_view_raw(self, repo: str, issue_number: int, json_fields: str) -> dict:
        return self._issue_view_raw_output

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
        return self._issue_list_raw_output

    def issue_comment(self, repo: str, issue_number: int, body: str) -> None:
        self.issue_comment_calls.append((repo, issue_number, body))

    def issue_edit_labels(
        self, repo: str, issue_number: int, *, add_labels: str | None = None, remove_labels: str | None = None
    ) -> None:
        self.issue_edit_labels_calls.append(
            {"repo": repo, "issue_number": issue_number, "add_labels": add_labels, "remove_labels": remove_labels}
        )

    def issue_close(self, repo: str, issue_number: int, *, comment: str | None = None) -> None:
        self.issue_close_calls.append({"repo": repo, "issue_number": issue_number, "comment": comment})
