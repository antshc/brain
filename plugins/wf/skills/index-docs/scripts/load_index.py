#!/usr/bin/env python3
"""Load every row of each Trigger condition table in a Markdown index as one JSON payload on stdout."""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path

HEADING = re.compile(r"^(#{1,6})\s+(.*?)\s*$")
OPTIONAL_SUFFIX = re.compile(r"\s*\*\([^)]*\)\*\s*$")
ROW_MARKER = re.compile(r"^<!--\s*rows:\s*(\d+)\s*-->$")
SEPARATOR_CELL = re.compile(r"^:?-+:?$")
LINK = re.compile(r"\[([^\]]+)\]\(([^)\s]+)\)")
TRIGGER_DEFAULT = re.compile(r"^\*\*Trigger:\*\*\s*(.*?)\s*(?:\*\*Default:\*\*\s*(.*))?$", re.DOTALL)


@dataclass(frozen=True)
class IndexRow:
    line: int
    title: str
    link: str | None
    trigger: str
    default: str | None
    cells: dict[str, str]


@dataclass
class IndexTable:
    name: str
    line: int
    headers: list[str]
    trigger_column: str
    marker_count: int | None
    rows: list[IndexRow] = field(default_factory=list)

    @property
    def row_count(self) -> int:
        return len(self.rows)


def split_cells(line: str) -> list[str]:
    text = line.strip()
    if text.startswith("|"):
        text = text[1:]
    if text.endswith("|") and not text.endswith("\\|"):
        text = text[:-1]
    return [cell.strip().replace("\\|", "|") for cell in re.split(r"(?<!\\)\|", text)]


def is_table_line(line: str) -> bool:
    return line.lstrip().startswith("|")


def is_separator(line: str) -> bool:
    cells = split_cells(line)
    return bool(cells) and all(SEPARATOR_CELL.match(cell) for cell in cells)


def section_name(heading_text: str) -> str:
    return OPTIONAL_SUFFIX.sub("", heading_text).strip()


def preceding_marker(lines: list[str], header_index: int) -> int | None:
    index = header_index - 1
    while index >= 0 and not lines[index].strip():
        index -= 1
    if index < 0:
        return None
    match = ROW_MARKER.match(lines[index].strip())
    return int(match.group(1)) if match else None


def parse_title(cell: str) -> tuple[str, str | None]:
    match = LINK.search(cell)
    if match:
        return match.group(1).strip("* "), match.group(2)
    return cell.replace("**", "").strip(), None


def parse_trigger(cell: str) -> tuple[str, str | None]:
    match = TRIGGER_DEFAULT.match(cell.strip())
    if not match:
        return cell.strip(), None
    trigger = match.group(1).strip().rstrip(".").strip()
    default = match.group(2).strip() if match.group(2) else None
    return trigger, default


def build_row(
    line_number: int, headers: list[str], cells: list[str], trigger_column: str, omit: set[str]
) -> IndexRow:
    values = dict(zip(headers, cells))
    title, link = parse_title(cells[0])
    trigger, default = parse_trigger(values[trigger_column])
    extra = {
        header: value
        for header, value in values.items()
        if header not in (headers[0], trigger_column) and header.lower() not in omit
    }
    return IndexRow(line=line_number, title=title, link=link, trigger=trigger, default=default, cells=extra)


def load_index(text: str, omit_columns: list[str] | None = None) -> tuple[list[IndexTable], list[str]]:
    omit = {column.lower() for column in omit_columns or []}
    lines = text.splitlines()
    tables: list[IndexTable] = []
    errors: list[str] = []
    heading = ""
    in_fence = False
    index = 0
    while index < len(lines):
        line = lines[index]
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            index += 1
            continue
        if in_fence:
            index += 1
            continue
        heading_match = HEADING.match(line)
        if heading_match:
            heading = section_name(heading_match.group(2))
            index += 1
            continue
        if not (is_table_line(line) and index + 1 < len(lines) and is_separator(lines[index + 1])):
            index += 1
            continue

        headers = split_cells(line)
        trigger_column = next((header for header in headers if "trigger condition" in header.lower()), None)
        body_start = index + 2
        body_end = body_start
        while body_end < len(lines) and is_table_line(lines[body_end]):
            body_end += 1
        if trigger_column is None:
            index = body_end
            continue

        table = IndexTable(
            name=heading,
            line=index + 1,
            headers=headers,
            trigger_column=trigger_column,
            marker_count=preceding_marker(lines, index),
        )
        for row_index in range(body_start, body_end):
            cells = split_cells(lines[row_index])
            if len(cells) != len(headers):
                errors.append(
                    f"{heading} line {row_index + 1}: expected {len(headers)} cells, found {len(cells)}"
                )
                continue
            table.rows.append(build_row(row_index + 1, headers, cells, trigger_column, omit))
        if table.marker_count is not None and table.marker_count != table.row_count:
            errors.append(
                f"{heading} line {table.line}: rows marker says {table.marker_count}, table has {table.row_count}"
            )
        tables.append(table)
        index = body_end
    return tables, errors


def table_payload(table: IndexTable) -> dict[str, object]:
    return {
        "name": table.name,
        "line": table.line,
        "headers": table.headers,
        "triggerColumn": table.trigger_column,
        "rowCount": table.row_count,
        "markerCount": table.marker_count,
        "rows": [asdict(row) for row in table.rows],
    }


def build_payload(source: Path, tables: list[IndexTable], errors: list[str]) -> dict[str, object]:
    return {
        "source": str(source),
        "counts": {table.name: table.row_count for table in tables},
        "totalRows": sum(table.row_count for table in tables),
        "errors": errors,
        "tables": [table_payload(table) for table in tables],
    }


def parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path, help="Markdown index file.")
    parser.add_argument(
        "--table",
        action="append",
        default=[],
        help="Emit rows only for this table name (repeatable); counts and errors still cover every table.",
    )
    parser.add_argument(
        "--omit-column",
        action="append",
        default=[],
        help="Drop this column from row cells (repeatable, case-insensitive), e.g. Summary.",
    )
    parser.add_argument("--counts-only", action="store_true", help="Omit rows; emit counts and errors.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        text = args.path.read_text(encoding="utf-8")
    except OSError as exception:
        print(f"Cannot read {args.path}: {exception}", file=sys.stderr)
        return 2

    tables, errors = load_index(text, args.omit_column)
    known = {table.name for table in tables}
    errors.extend(f"Table not found: {name}" for name in args.table if name not in known)
    payload = build_payload(args.path, tables, errors)
    if args.counts_only:
        payload["tables"] = []
    elif args.table:
        payload["tables"] = [entry for entry in payload["tables"] if entry["name"] in args.table]
    print(json.dumps(payload, ensure_ascii=False))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
