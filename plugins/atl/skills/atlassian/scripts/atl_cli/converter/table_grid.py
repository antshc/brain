"""Table-geometry validation (pure), shared by both conversion directions.

Confirms a table's rows resolve to one consistent column count once `colspan`/`rowspan`
are applied, so a malformed table is rejected before any output is produced.
"""
from __future__ import annotations


def validate_table_grid(rows: list[list[dict]], table_label: str = "table") -> int:
    """Validate ``rows`` (each a list of cell dicts with optional `colspan`/`rowspan`,
    default 1) resolve to one consistent column count. Returns that column count.

    Raises ValueError naming ``table_label`` as the cause on mismatch.
    """
    pending: dict[int, int] = {}
    column_count: int | None = None

    for row in rows:
        col = 0
        cell_index = 0
        while cell_index < len(row) or pending.get(col, 0) > 0:
            if pending.get(col, 0) > 0:
                pending[col] -= 1
                if pending[col] == 0:
                    del pending[col]
                col += 1
                continue
            cell = row[cell_index]
            cell_index += 1
            colspan = int(cell.get("colspan", 1) or 1)
            rowspan = int(cell.get("rowspan", 1) or 1)
            if rowspan > 1:
                for c in range(col, col + colspan):
                    pending[c] = pending.get(c, 0) + (rowspan - 1)
            col += colspan

        if column_count is None:
            column_count = col
        elif col != column_count:
            raise ValueError(
                f"{table_label}: rows do not resolve to a consistent column count "
                f"({col} vs {column_count}) once column and row spans are applied"
            )

    return column_count or 0
