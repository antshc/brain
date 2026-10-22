from __future__ import annotations

from playwright.sync_api import Locator, Page


class Dropdown:
    """A native select or an ARIA combobox with option roles, found by its accessible name."""

    def __init__(self, page: Page, name: str) -> None:
        self.page = page
        self.control: Locator = page.get_by_role("combobox", name=name)

    def choose(self, option: str) -> None:
        if self.control.evaluate("element => element.tagName") == "SELECT":
            self.control.select_option(label=option)
        else:
            self.control.click()
            self.page.get_by_role("option", name=option).click()

    def selected(self) -> str:
        return self.control.input_value() if self.control.evaluate("element => element.tagName") == "SELECT" else self.control.inner_text().strip()
