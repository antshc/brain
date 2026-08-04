"""Unit tests for the staged-diff-with-fallback helper.

Mapped to TEST_PLAN.md — every class docstring names the Feature,
every method name is the Scenario in snake_case.
When a test or scenario changes, update both sides to stay in sync.
"""

from modules.staged_diff.staged_diff import NO_CHANGES_MESSAGE, get_staged_diff_with_fallback


class FakeGitRunner:
    def __init__(self, diff_output: str):
        self.diff_output = diff_output
        self.calls: list[list[str]] = []

    def __call__(self, args: list[str]) -> str:
        self.calls.append(args)
        if args == ["diff", "--cached"]:
            return self.diff_output
        return ""


class TestStagedDiffWithFallback:
    """Feature: Staged Diff With Fallback"""

    def test_uncommitted_changes_stages_everything_and_returns_the_cached_diff(self):
        # Scenario: Uncommitted changes stages everything and returns the cached diff
        git = FakeGitRunner(diff_output="diff --git a/f.txt b/f.txt\n+hi\n")

        result = get_staged_diff_with_fallback(run_git=git)

        assert result == "diff --git a/f.txt b/f.txt\n+hi"
        assert git.calls == [["add", "-A"], ["diff", "--cached"]]

    def test_no_uncommitted_changes_returns_the_fallback_message(self):
        # Scenario: No uncommitted changes returns the fallback message
        git = FakeGitRunner(diff_output="")

        result = get_staged_diff_with_fallback(run_git=git)

        assert result == NO_CHANGES_MESSAGE
        assert git.calls == [["add", "-A"], ["diff", "--cached"]]
