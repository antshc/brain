from __future__ import annotations

from proof.kit import FlowContext


# A Page Object: the one place that knows how this page is reached and read. Flows call it; nothing else holds selectors.
class HomePage:
    def __init__(self, context: FlowContext) -> None:
        self.context = context

    def open(self) -> None:
        self.context.goto("/")

    def heading(self) -> str | None:
        locator = self.context.page.get_by_role("heading", level=1)
        return locator.first.inner_text().strip() if locator.count() else None
