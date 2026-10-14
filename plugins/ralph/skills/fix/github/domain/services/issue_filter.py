from __future__ import annotations

from ..issue import Issue

class IssueFilter:
    """Filters Issue entities by actionability."""

    def get_actionable_issues(self, issues: list[Issue]) -> list[Issue]:
        """Return approved issues."""
        return [issue for issue in issues if issue.is_actionable]
