from dataclasses import dataclass

from domain.comment import Comment


@dataclass
class ReviewThread:
    thread_id: str
    path: str
    lines: str
    is_resolved: bool
    comments: list[Comment]

    @property
    def actionable_comment(self) -> str:
        labeled = next((c for c in reversed(self.comments) if c.get_label() is not None), None)
        return labeled.body if labeled else (self.comments[0].body if self.comments else "")

    @property
    def is_actionable(self) -> bool:
        if self.is_resolved:
            return False
        label = None
        for comment in reversed(self.comments):
            if comment.is_excluded():
                return False
            lbl = comment.get_label()
            if lbl is not None:
                label = lbl
                break
        if label is None:
            if not self.comments:
                return False
            label = self.comments[0].get_label()
        if not label:
            return False
        return label.is_actionable()
