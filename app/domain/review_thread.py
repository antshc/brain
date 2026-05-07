from dataclasses import dataclass, field
from enum import Enum


class ThreadLabel(Enum):
    FIX = "fix!"
    SUGGEST_BANG = "suggest!"
    SUGGEST = "suggest"
    NIT = "nit"
    GOOD = "good"
    QUESTION = "question"

    def is_actionable(self) -> bool:
        return self in (ThreadLabel.FIX, ThreadLabel.SUGGEST_BANG)


@dataclass
class ReviewThread:
    thread_id: str
    label: ThreadLabel
    path: str
    lines: str
    body: str
    discussion: list[dict] = field(default_factory=list)
