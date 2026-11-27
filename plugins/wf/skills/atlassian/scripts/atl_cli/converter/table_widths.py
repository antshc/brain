"""Reversible width metadata for the supported, unmerged table grid."""
from __future__ import annotations

import hashlib
import json
import math
import re

from .patterns import COMMENT_TAG_RE
from .syntax import syntax_lines


def _text(node: dict) -> str:
    if not isinstance(node, dict):
        raise ValueError("table or heading has invalid content")
    kind = node.get("type")
    if kind == "text":
        value = node.get("text", "")
        if not isinstance(value, str):
            raise ValueError("table or heading has invalid text")
        return value
    if kind == "hardBreak":
        return " "
    if kind in {"status", "inlineCard"}:
        attrs = node.get("attrs", {})
        value = attrs.get("text" if kind == "status" else "url", "") if isinstance(attrs, dict) else None
        if not isinstance(value, str):
            raise ValueError("table or heading has invalid inline content")
        return value
    if kind == "inlineExtension":
        attrs = node.get("attrs", {})
        if isinstance(attrs, dict) and attrs.get("extensionKey") in {"anchor", "create-from-template"}:
            return ""
        raise ValueError("table or heading has unsupported inline content")
    if kind not in {
        "paragraph", "heading", "tableCell", "tableHeader", "bulletList", "orderedList",
        "listItem", "blockquote", "panel", "expand", "codeBlock",
    }:
        raise ValueError("table or heading has unsupported content")
    children = node.get("content", [])
    if not isinstance(children, list):
        raise ValueError("table or heading has invalid content")
    separator = " " if kind in {"tableCell", "tableHeader"} else ""
    return separator.join(_text(child) for child in children)


def normalized_text(node: dict) -> str:
    return " ".join(_text(node).split()).casefold()


def flat_rows(table: dict) -> list[list[dict]]:
    rows = table.get("content", [])
    if not isinstance(rows, list) or not rows:
        raise ValueError("table has no rows")
    result = []
    for row in rows:
        if not isinstance(row, dict) or row.get("type") != "tableRow":
            raise ValueError("table has an unsupported row")
        cells = row.get("content", [])
        if not isinstance(cells, list) or not cells:
            raise ValueError("table has an empty row")
        for cell in cells:
            if not isinstance(cell, dict) or cell.get("type") not in {"tableHeader", "tableCell"}:
                raise ValueError("table has an unsupported cell")
            attrs = cell.get("attrs", {})
            if not isinstance(attrs, dict) or any(
                isinstance(attrs.get(key, 1), bool) or attrs.get(key, 1) != 1 for key in ("colspan", "rowspan")
            ):
                raise ValueError("table has merged cells")
        if result and len(cells) != len(result[0]):
            raise ValueError("table has inconsistent column counts")
        result.append(cells)
    if any(cell["type"] != "tableHeader" for cell in result[0]) or any(
        cell["type"] != "tableCell" for row in result[1:] for cell in row
    ):
        raise ValueError("table is not a header-first grid")
    return result


def header_names(rows: list[list[dict]]) -> tuple[str, ...]:
    return tuple(normalized_text(cell) for cell in rows[0])


def _digest(value: object) -> str:
    encoded = json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def header_hash(rows: list[list[dict]]) -> str:
    return _digest(header_names(rows))


def _rows_digest(rendered: list[str]) -> str:
    without_comments = []
    for row in rendered:
        _, syntax = next(syntax_lines(row))
        for match in reversed(list(COMMENT_TAG_RE.finditer(syntax))):
            row = row[:match.start()] + row[match.end():]
        without_comments.append(row)
    # Keep comment identities when otherwise-identical rows could be confused.
    return _digest(without_comments if len(set(without_comments)) == len(without_comments) else rendered)


def rows_hash(rows: list[list[dict]]) -> str:
    # The renderer also imports this module; defer the import until both are initialized.
    from .adf_to_md import render_table_cell

    return _rows_digest(["| " + " | ".join(render_table_cell(cell) for cell in row) + " |" for row in rows])


def _valid_token(value: object) -> bool:
    if value is None or value == {}:
        return True
    return isinstance(value, list) and all(
        type(number) in (int, float)
        and number >= 0
        and (not isinstance(number, float) or math.isfinite(number))
        for number in value
    )


def width_matrix(rows: list[list[dict]]) -> list[list[object]]:
    matrix = []
    for row in rows:
        values = []
        for cell in row:
            attrs = cell.get("attrs", {})
            value = attrs.get("colwidth") if "colwidth" in attrs else None
            token = {} if "colwidth" in attrs and value is None else value
            if not _valid_token(token):
                raise ValueError("table colwidth must be a numeric array or null")
            values.append(token)
        matrix.append(values)
    return matrix


def consistent_column_widths(matrix: list[list[object]]) -> list[object] | None:
    if not matrix or any(len(row) != len(matrix[0]) for row in matrix):
        return None
    columns = []
    for index in range(len(matrix[0])):
        defined = [row[index] for row in matrix if isinstance(row[index], list) and row[index]]
        if defined and any(value != defined[0] for value in defined):
            return None
        columns.append(defined[0] if defined else None)
    return columns


def width_marker_attrs(table: dict, inferred_widths: list[int] | None, rendered: str) -> dict[str, str]:
    try:
        rows = flat_rows(table)
    except ValueError:
        return {}
    if not inferred_widths and not any("colwidth" in cell.get("attrs", {}) for row in rows for cell in row):
        return {}
    matrix = width_matrix(rows)
    try:
        names = header_names(rows)
    except ValueError:
        return {}
    fields = {"header-hash": _digest(names)}
    rendered_lines = rendered.splitlines()
    if all(row == matrix[0] for row in matrix):
        fields["colwidths"] = json.dumps(matrix[0], separators=(",", ":"))
        if len(set(names)) != len(names):
            fields["rows-hash"] = _rows_digest([rendered_lines[0], *rendered_lines[2:]])
    else:
        fields["cell-widths"] = json.dumps(matrix, separators=(",", ":"))
        fields["rows-hash"] = _rows_digest([rendered_lines[0], *rendered_lines[2:]])
    return fields


def parse_width_marker(attrs: dict) -> tuple[str, list] | None:
    keys = [key for key in ("colwidths", "cell-widths") if key in attrs]
    if len(keys) > 1:
        raise ValueError("table marker cannot combine colwidths and cell-widths")
    for key in ("header-hash", "rows-hash"):
        if key in attrs and not re.fullmatch(r"[0-9a-f]{64}", attrs[key]):
            raise ValueError(f"table marker {key} must be a SHA-256 digest")
    if not keys:
        if "header-hash" in attrs or "rows-hash" in attrs:
            raise ValueError("table width hashes require colwidths or cell-widths")
        return None
    key = keys[0]
    try:
        value = json.loads(attrs[key])
    except (TypeError, json.JSONDecodeError):
        raise ValueError(f"table marker {key} must contain a JSON array") from None
    if not isinstance(value, list):
        raise ValueError(f"table marker {key} must contain a JSON array")
    rows = [value] if key == "colwidths" else value
    if any(not isinstance(row, list) or any(not _valid_token(token) for token in row) for row in rows):
        raise ValueError(f"table marker {key} contains an invalid column width")
    return key, value


def apply_width_matrix(rows: list[list[dict]], matrix: list[list[object]]) -> None:
    if len(rows) != len(matrix) or any(len(row) != len(values) for row, values in zip(rows, matrix)):
        raise ValueError("table width matrix does not match the table dimensions")
    if any(not _valid_token(value) for values in matrix for value in values):
        raise ValueError("table width matrix contains an invalid column width")
    for row, values in zip(rows, matrix):
        for cell, value in zip(row, values):
            attrs = cell.setdefault("attrs", {})
            if value is None:
                attrs.pop("colwidth", None)
            elif value == {}:
                attrs["colwidth"] = None
            elif isinstance(value, list):
                attrs["colwidth"] = value.copy()
            else:
                raise ValueError("table width matrix contains an invalid column width")
            if not attrs:
                cell.pop("attrs")


def apply_width_marker(table: dict, attrs: dict) -> str | None:
    parsed = parse_width_marker(attrs)
    if parsed is None:
        return None
    rows = flat_rows(table)
    key, values = parsed
    if "header-hash" in attrs and attrs["header-hash"] != header_hash(rows):
        return "column headers changed; using default column widths"
    if "rows-hash" in attrs and attrs["rows-hash"] != rows_hash(rows):
        names = header_names(rows)
        if key == "cell-widths" and "header-hash" in attrs and all(names) and len(set(names)) == len(names):
            columns = consistent_column_widths(values)
            if columns is not None and len(columns) == len(names):
                apply_width_matrix(rows, [columns for _ in rows])
                return "table rows changed; applied consistent column widths"
        return "table rows changed; using default column widths"
    matrix = [values for _ in rows] if key == "colwidths" else values
    if len(matrix) != len(rows) or any(len(values) != len(row) for values, row in zip(matrix, rows)):
        return "table dimensions changed; using default column widths"
    apply_width_matrix(rows, matrix)
    return None
