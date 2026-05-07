from dataclasses import InitVar, dataclass, field

from domain.comment import Comment
from domain.thread_classification_policy import ThreadClassificationPolicy
from domain.thread_label import ThreadLabel


@dataclass
class ReviewThread:
    thread_id: str
    path: str
    lines: str
    is_resolved: bool
    comments: list[Comment]
    policy: InitVar[ThreadClassificationPolicy]
    label: ThreadLabel = field(init=False)
    body: str = field(init=False)

    def __post_init__(self, policy: ThreadClassificationPolicy) -> None:
        result = policy.classify_comments(self.comments)
        if result is None:
            raise ValueError(f"Thread {self.thread_id!r} is excluded or unclassifiable")
        self.body, self.label = result

    @property
    def is_actionable(self) -> bool:
        return self.label.is_actionable()
