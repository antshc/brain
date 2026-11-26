"""Carry widths forward only between uniquely identifiable, compatible tables."""
from __future__ import annotations

import math
import re
from collections import Counter, defaultdict
from dataclasses import dataclass

from ..converter.table_widths import (
    apply_width_matrix,
    consistent_column_widths,
    flat_rows,
    header_names,
    normalized_text,
    rows_hash,
    width_matrix,
)


@dataclass(frozen=True)
class _Table:
    number: int
    node: dict
    rows: list[list[dict]] | None
    key: tuple | None


def _tables(doc: dict) -> list[_Table]:
    tables: list[_Table] = []

    def visit(nodes: object, scopes: tuple, headings: dict) -> None:
        if not isinstance(nodes, list):
            return
        current = headings.copy()
        for node in nodes:
            if not isinstance(node, dict):
                continue
            kind = node.get("type")
            if kind == "heading":
                attrs = node.get("attrs", {})
                if not isinstance(attrs, dict):
                    current = {1: None}
                    continue
                level = attrs.get("level")
                if type(level) is not int or not 1 <= level <= 6:
                    current = {1: None}
                    continue
                current = {key: value for key, value in current.items() if key < level}
                try:
                    current[level] = normalized_text(node)
                except ValueError:
                    current[level] = None
            elif kind == "table":
                try:
                    rows = flat_rows(node)
                    names = header_names(rows)
                    key = (scopes, tuple(sorted(current.items())), names) if None not in current.values() else None
                except ValueError:
                    rows, key = None, None
                tables.append(_Table(len(tables) + 1, node, rows, key))
            elif kind in {"expand", "panel", "blockquote", "bulletList", "orderedList", "listItem"}:
                attrs = node.get("attrs", {})
                label = attrs.get("title", attrs.get("panelType", "")) if isinstance(attrs, dict) else None
                label = " ".join(label.split()).casefold() if isinstance(label, str) else None
                scope = (tuple(sorted(current.items())), kind, label)
                visit(node.get("content", []), scopes + (scope,), {})

    visit(doc.get("content", []), (), {})
    return tables


def has_tables(doc: dict) -> bool:
    return bool(_tables(doc))


def _copy_table_attrs(target: dict, live: dict, explicit: frozenset[str], warnings: list[str], number: int) -> None:
    target_attrs = target.setdefault("attrs", {})
    source_attrs = live.get("attrs", {})
    if not isinstance(source_attrs, dict):
        warnings.append(f"table {number}: invalid existing table attributes; using Markdown/default layout and width")
        return
    for key in ("layout", "width"):
        if key in explicit:
            continue
        value = source_attrs.get(key)
        if value is None:
            target_attrs.pop(key, None)
            continue
        valid = (
            isinstance(value, str) and bool(re.fullmatch(r"[a-z-]+", value))
            if key == "layout"
            else type(value) in (int, float)
            and value >= 0
            and (not isinstance(value, float) or math.isfinite(value))
        )
        if valid:
            target_attrs[key] = value
        else:
            warnings.append(f"table {number}: invalid existing {key}; using Markdown/default {key}")


def _copy_column_widths(target: _Table, live: _Table, warnings: list[str]) -> None:
    assert target.rows is not None and live.rows is not None
    names = header_names(target.rows)
    if not all(names) or len(set(names)) != len(names):
        warnings.append(f"table {target.number}: duplicate or empty column headers; using default column widths")
        return
    try:
        matrix = width_matrix(live.rows)
        if all(row == matrix[0] for row in matrix):
            apply_width_matrix(target.rows, [matrix[0] for _ in target.rows])
            return
        try:
            same_rows = len(target.rows) == len(live.rows) and rows_hash(target.rows) == rows_hash(live.rows)
        except (ValueError, NotImplementedError, AttributeError, TypeError):
            same_rows = False
        if same_rows:
            apply_width_matrix(target.rows, matrix)
            return
        columns = consistent_column_widths(matrix)
        if columns is None:
            warnings.append(f"table {target.number}: row-specific widths cannot be matched safely; using default column widths")
            return
        apply_width_matrix(target.rows, [columns for _ in target.rows])
        warnings.append(f"table {target.number}: rows changed; applied consistent column widths")
    except ValueError:
        warnings.append(f"table {target.number}: invalid existing column widths; using default column widths")


def preserve_table_widths(target: dict, live: dict, metadata: dict[int, frozenset[str]]) -> list[str]:
    target_tables, live_tables = _tables(target), _tables(live)
    target_counts = Counter(table.key for table in target_tables if table.key is not None)
    live_by_key: dict[tuple, list[_Table]] = defaultdict(list)
    for table in live_tables:
        if table.key is not None:
            live_by_key[table.key].append(table)

    warnings = []
    for table in target_tables:
        explicit = metadata.get(id(table.node), frozenset())
        needs_columns = not ({"colwidths", "cell-widths"} & explicit)
        if not needs_columns and {"layout", "width"} <= explicit:
            continue
        matches = live_by_key.get(table.key, []) if table.key is not None else []
        if not matches:
            warnings.append(f"table {table.number}: no compatible existing table; using Markdown/default widths")
            continue
        if len(matches) != 1 or target_counts[table.key] != 1:
            warnings.append(f"table {table.number}: ambiguous existing table match; using Markdown/default widths")
            continue
        live_table = matches[0]
        _copy_table_attrs(table.node, live_table.node, explicit, warnings, table.number)
        if needs_columns:
            _copy_column_widths(table, live_table, warnings)
    return warnings
