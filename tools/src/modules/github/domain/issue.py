from dataclasses import dataclass, field
from typing import ClassVar

from .issue_comment import IssueComment


@dataclass
class Issue:
    number: int
    title: str
    body: str
    url: str
    labels: list[str] = field(default_factory=list)
    comments: list[IssueComment] = field(default_factory=list)

    _ACTIONABLE_LABELS: ClassVar[frozenset[str]] = frozenset({"ready", "prd"})
    _BLOCKING_LABELS: ClassVar[frozenset[str]] = frozenset({"blocked", "hitl"})

    @property
    def is_actionable(self) -> bool:
        normalized_labels = {label.casefold() for label in self.labels}
        return bool(normalized_labels & self._ACTIONABLE_LABELS) and not bool(normalized_labels & self._BLOCKING_LABELS)
