from __future__ import annotations

from playwright.sync_api import Locator, Page


class Table:
    """A table found by its accessible name. Reads it as text: no cell selectors leave this class."""

    def __init__(self, page: Page, name: str) -> None:
        self.table: Locator = page.get_by_role("table", name=name)

    def headers(self) -> list[str]:
        return [text.strip() for text in self.table.get_by_role("columnheader").all_inner_texts()]

    def rows(self) -> list[list[str]]:
        rows = [[text.strip() for text in row.get_by_role("cell").all_inner_texts()] for row in self.table.get_by_role("row").all()]
        return [cells for cells in rows if cells]

    def row_with(self, text: str) -> Locator:
        return self.table.get_by_role("row").filter(has_text=text)
