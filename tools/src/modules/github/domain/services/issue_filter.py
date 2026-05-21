"""Filter issues by actionability."""

from ..issue import Issue


class IssueFilter:
    """Filters Issue entities by actionability."""

    def get_actionable_issues(self, issues: list[Issue]) -> list[Issue]:
        """Return only issues where is_actionable is True."""
        return [i for i in issues if i.is_actionable]
