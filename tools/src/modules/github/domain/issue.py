from dataclasses import dataclass, field


_ACTIONABLE_LABELS = frozenset({"ready", "prd"})
_BLOCKING_LABELS = frozenset({"blocked", "hitl"})


@dataclass
class IssueComment:
    id: str
    body: str
    updated_at: str


@dataclass
class Issue:
    number: int
    title: str
    body: str
    url: str
    labels: list[str] = field(default_factory=list)
    comments: list[IssueComment] = field(default_factory=list)

    @property
    def is_actionable(self) -> bool:
        label_set = set(self.labels)
        return bool(label_set & _ACTIONABLE_LABELS) and not (label_set & _BLOCKING_LABELS)
