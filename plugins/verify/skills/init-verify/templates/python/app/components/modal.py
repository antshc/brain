from __future__ import annotations

from playwright.sync_api import Locator, Page


class Modal:
    """A dialog found by its accessible name."""

    def __init__(self, page: Page, name: str) -> None:
        self.dialog: Locator = page.get_by_role("dialog", name=name)

    def is_open(self) -> bool:
        return self.dialog.is_visible()

    def text(self) -> str:
        return self.dialog.inner_text().strip()

    def press(self, button: str) -> None:
        self.dialog.get_by_role("button", name=button).click()
