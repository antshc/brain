"""Block-level Markdown -> ADF parsing (pure): headings, lists, tables, quotes, code, and
`<details>` expands.
"""
from __future__ import annotations

import re

from .inline import parse_inline
from .patterns import (
    DETAILS_CLOSE_RE,
    DETAILS_OPEN_RE,
    HEADING_RE,
    PANEL_MARKER_RE,
    SUMMARY_RE,
    TOC_COMMENT_RE,
    breakout_marker_mark,
    table_marker_attrs,
)
from .table_grid import validate_table_grid

CODE_LANG_ALLOWLIST = {
    "text",
    "plaintext",
    "powershell",
    "go",
    "json",
    "xml",
    "yaml",
    "bash",
    "sh",
    "shell",
    "python",
    "javascript",
    "typescript",
    "java",
    "csharp",
    "sql",
    "html",
    "css",
    "diff",
    "none",
}

_BULLET_RE = re.compile(r"^(\s*)[-*+]\s+(.*)")
_ORDERED_RE = re.compile(r"^(\s*)\d+\.\s+(.*)")
_ORDERED_NUMBER_RE = re.compile(r"^\s*(\d+)\.")
_RULE_RE = re.compile(r"^(-{3,}|\*{3,}|_{3,})\s*$")
# Leading whitespace is allowed so a table indented under a list item is still a table.
_TABLE_ROW_RE = re.compile(r"^(\s*)\|(.*)\|\s*$")
_TABLE_SEP_RE = re.compile(r"^\s*\|[\s:|-]+\|\s*$")
_FENCE_OPEN_RE = re.compile(r"^```(\w*)\s*$")

# Column widths (px) for headers this skill recognizes by name, stripped of markdown marks
# (e.g. "**#**" -> "#"). Only applied when a table has at least one of these headers, so
# generic tables are left to Confluence's auto-sizing.
_NARROW_COLWIDTHS = {"#": 60, "no": 60, "priority": 110, "source": 110}
_WIDE_COLUMN_NAMES = {"details", "description"}
_TABLE_WIDTH_BUDGET_PX = 1400


def split_table_row(row: str) -> list[str]:
    row = row.strip()
    if row.startswith("|"):
        row = row[1:]
    if row.endswith("|"):
        row = row[:-1]
    # Split on unescaped pipes.
    cells = re.split(r"(?<!\\)\|", row)
    return [c.strip().replace("\\|", "|") for c in cells]


def build_toc_extension() -> dict:
    """A Confluence-native table of contents macro node, for the `<!-- adf:toc -->` marker."""
    return {
        "type": "extension",
        "attrs": {
            "layout": "default",
            "extensionType": "com.atlassian.confluence.macro.core",
            "extensionKey": "toc",
            "parameters": {"macroParams": {}},
        },
    }


def parse_blocks(lines: list[str]) -> list[dict]:
    """Parse a list of Markdown lines into ADF block nodes."""
    blocks: list[dict] = []
    i = 0
    n = len(lines)
    pending_table_attrs: dict | None = None
    pending_breakout: dict | None = None
    while i < n:
        line = lines[i]

        if not line.strip():
            i += 1
            continue

        if TOC_COMMENT_RE.match(line):
            toc = {"type": "expand", "attrs": {"title": "Table of Contents"}, "content": [build_toc_extension()]}
            if pending_breakout:
                toc["marks"] = [pending_breakout]
            blocks.append(toc)
            pending_table_attrs = pending_breakout = None
            i += 1
            continue

        marker_table_attrs = table_marker_attrs(line)
        if marker_table_attrs is not None:
            pending_table_attrs = marker_table_attrs
            i += 1
            continue

        marker_breakout = breakout_marker_mark(line)
        if marker_breakout is not None:
            pending_breakout = marker_breakout
            i += 1
            continue

        # A marker (if any) only applies to the very next construct; drop it otherwise.
        apply_table_attrs = pending_table_attrs
        pending_table_attrs = None
        apply_breakout = pending_breakout
        pending_breakout = None

        heading_m = HEADING_RE.match(line)
        if heading_m:
            level = len(heading_m.group(1))
            heading_text = heading_m.group(2)
            blocks.append({"type": "heading", "attrs": {"level": level}, "content": parse_inline(heading_text)})
            i += 1
            continue

        if _RULE_RE.match(line):
            blocks.append({"type": "rule"})
            i += 1
            continue

        fence_m = _FENCE_OPEN_RE.match(line)
        if fence_m:
            lang = fence_m.group(1).lower()
            code_lines = []
            i += 1
            while i < n and not lines[i].startswith("```"):
                code_lines.append(lines[i])
                i += 1
            i += 1  # skip closing fence
            attrs = {}
            if lang in CODE_LANG_ALLOWLIST:
                attrs["language"] = lang
            node = {"type": "codeBlock", "content": [{"type": "text", "text": "\n".join(code_lines)}]}
            if attrs:
                node["attrs"] = attrs
            if apply_breakout:
                node["marks"] = [apply_breakout]
            blocks.append(node)
            continue

        if line.startswith(">"):
            quote_lines = []
            while i < n and lines[i].startswith(">"):
                quote_lines.append(re.sub(r"^>\s?", "", lines[i]))
                i += 1
            panel_m = quote_lines and PANEL_MARKER_RE.match(quote_lines[0])
            if panel_m:
                panel_type = panel_m.group(1).lower()
                blocks.append(
                    {
                        "type": "panel",
                        "attrs": {"panelType": panel_type},
                        "content": paragraphs_from_lines(quote_lines[1:]),
                    }
                )
            else:
                blocks.append({"type": "blockquote", "content": paragraphs_from_lines(quote_lines)})
            continue

        if DETAILS_OPEN_RE.match(line):
            i += 1
            title = ""
            if i < n:
                sm = SUMMARY_RE.match(lines[i])
                if sm:
                    title = sm.group(1).strip()
                    i += 1
            inner_lines = []
            depth = 1
            while i < n and depth > 0:
                if DETAILS_OPEN_RE.match(lines[i]):
                    depth += 1
                elif DETAILS_CLOSE_RE.match(lines[i]):
                    depth -= 1
                    if depth == 0:
                        i += 1
                        break
                inner_lines.append(lines[i])
                i += 1
            content = parse_blocks(inner_lines)
            if not content:
                content = [{"type": "paragraph", "content": [{"type": "text", "text": ""}]}]
            expand = {"type": "expand", "attrs": {"title": title}, "content": content}
            if apply_breakout:
                expand["marks"] = [apply_breakout]
            blocks.append(expand)
            continue

        if _table_start(lines, i) is not None:
            table, i = _parse_table(lines, i, apply_table_attrs or {"layout": "default"})
            blocks.append(table)
            continue

        if _BULLET_RE.match(line) or _ORDERED_RE.match(line):
            # ADF forbids a table inside a listItem: tables nested anywhere in the list are
            # collected and emitted as siblings right after the whole list.
            deferred_tables: list[dict] = []
            list_block, i = parse_list(lines, i, deferred_tables)
            if list_block["type"] == "orderedList":
                start = int(_ORDERED_NUMBER_RE.match(line).group(1))
                if start != 1:
                    list_block["attrs"] = {"order": start}
            blocks.append(list_block)
            blocks.extend(deferred_tables)
            continue

        # Paragraph: consume consecutive plain lines until a blank line or block start.
        para_lines = []
        while i < n and lines[i].strip() and not _is_block_start(lines[i], lines, i):
            para_lines.append(lines[i])
            i += 1
        if not para_lines:
            # A block-start marker no branch above claimed (e.g. a stray `</details>`) is literal text.
            para_lines.append(lines[i])
            i += 1
        text = " ".join(l.strip() for l in para_lines)
        blocks.append({"type": "paragraph", "content": parse_inline(text)})

    return blocks


def _is_block_start(line: str, lines: list[str], i: int) -> bool:
    if HEADING_RE.match(line):
        return True
    if _RULE_RE.match(line):
        return True
    if _FENCE_OPEN_RE.match(line):
        return True
    if line.startswith(">"):
        return True
    if DETAILS_OPEN_RE.match(line) or DETAILS_CLOSE_RE.match(line) or SUMMARY_RE.match(line):
        return True
    if TOC_COMMENT_RE.match(line) or table_marker_attrs(line) is not None or breakout_marker_mark(line) is not None:
        return True
    if _table_start(lines, i) is not None:
        return True
    if _BULLET_RE.match(line) or _ORDERED_RE.match(line):
        return True
    return False


def _table_start(lines: list[str], i: int) -> int | None:
    """Indent of a table starting at `lines[i]` (header row + separator), optionally preceded by
    a table marker line (`adf:wide-table` / `adf:table`); None when no table starts there."""
    if table_marker_attrs(lines[i]) is not None:
        i += 1
    if i + 1 >= len(lines):
        return None
    row_m = _TABLE_ROW_RE.match(lines[i])
    if not row_m or not _TABLE_SEP_RE.match(lines[i + 1]):
        return None
    return len(row_m.group(1))


def _parse_table(lines: list[str], i: int, table_attrs: dict) -> tuple[dict, int]:
    header_cells = split_table_row(lines[i])
    i += 2
    rows = []
    while i < len(lines) and _TABLE_ROW_RE.match(lines[i]):
        rows.append(split_table_row(lines[i]))
        i += 1
    table = build_table(header_cells, rows, layout=table_attrs.get("layout", "default"))
    if "width" in table_attrs:
        table["attrs"]["width"] = table_attrs["width"]
    return table, i


def paragraphs_from_lines(lines: list[str]) -> list[dict]:
    paras: list[dict] = []
    buf: list[str] = []
    for line in lines:
        if not line.strip():
            if buf:
                paras.append({"type": "paragraph", "content": parse_inline(" ".join(buf))})
                buf = []
        else:
            buf.append(line.strip())
    if buf:
        paras.append({"type": "paragraph", "content": parse_inline(" ".join(buf))})
    if not paras:
        paras = [{"type": "paragraph", "content": [{"type": "text", "text": ""}]}]
    return paras


def _match_list_marker(line: str):
    """Match `line` against both list-marker patterns, ordered first.

    Returns `(is_ordered, match)`, or `(None, None)` when neither matches.
    """
    m = _ORDERED_RE.match(line)
    if m:
        return True, m
    m = _BULLET_RE.match(line)
    if m:
        return False, m
    return None, None


def parse_list(lines: list[str], i: int, deferred_tables: list[dict]) -> tuple[dict, int]:
    """Parse a list at `lines[i]`. Tables indented under its items are appended to
    `deferred_tables` (ADF has no table-in-listItem) instead of ending the list."""
    n = len(lines)
    is_ordered, first_m = _match_list_marker(lines[i])
    base_indent = len(first_m.group(1))
    list_type = "orderedList" if is_ordered else "bulletList"
    items: list[dict] = []

    def nested_table_indent(j: int) -> int | None:
        indent = _table_start(lines, j)
        return indent if indent is not None and indent > base_indent else None

    while i < n:
        line = lines[i]
        if not line.strip():
            # A single blank line inside a tight list doesn't necessarily end it;
            # stop when the following line isn't this same list (different marker
            # type at the same level ends it, so a new list can start after it).
            if i + 1 < n and nested_table_indent(i + 1) is not None:
                i += 1
                continue
            nxt_ordered, nxt_m = _match_list_marker(lines[i + 1]) if i + 1 < n else (None, None)
            if nxt_m is None:
                break
            if len(nxt_m.group(1)) <= base_indent and nxt_ordered != is_ordered:
                break
            i += 1
            continue

        if nested_table_indent(i) is not None:
            marker = table_marker_attrs(line)
            table, i = _parse_table(lines, i + 1 if marker is not None else i, marker or {"layout": "default"})
            deferred_tables.append(table)
            continue

        line_ordered, m = _match_list_marker(line)
        if not m or len(m.group(1)) < base_indent:
            break
        indent = len(m.group(1))
        if indent == base_indent and line_ordered != is_ordered:
            # A different marker type at the same level starts a new list.
            break
        if indent > base_indent:
            # Nested list belongs to the previous item.
            nested_block, i = parse_list(lines, i, deferred_tables)
            if items:
                items[-1]["content"].append(nested_block)
            continue

        item_text = m.group(2)
        i += 1
        item_content: list[dict] = []

        # Fold soft-wrapped continuation lines into the item's paragraph; a deeper-indented
        # list nests under it instead.
        while i < n and lines[i].strip():
            _, sub_m = _match_list_marker(lines[i])
            if sub_m and len(sub_m.group(1)) > indent:
                if not item_content:
                    item_content.append({"type": "paragraph", "content": parse_inline(item_text)})
                nested_block, i = parse_list(lines, i, deferred_tables)
                item_content.append(nested_block)
                continue
            if sub_m or item_content or _is_block_start(lines[i], lines, i):
                break  # keep list-item parsing simple: one paragraph + optional nested list only
            item_text = f"{item_text} {lines[i].strip()}"
            i += 1

        if not item_content:
            item_content.append({"type": "paragraph", "content": parse_inline(item_text)})

        items.append({"type": "listItem", "content": item_content})

    return {"type": list_type, "content": items}, i


def _strip_md_marks(text: str) -> str:
    return re.sub(r"\*+", "", text).strip().lower()


def compute_colwidths(header_cells: list[str]) -> list[int] | None:
    keys = [_strip_md_marks(h) for h in header_cells]
    if not any(k in _NARROW_COLWIDTHS for k in keys):
        return None

    widths: list[int] = [0] * len(keys)
    remaining_idxs = []
    fixed_total = 0
    for idx, k in enumerate(keys):
        if k in _NARROW_COLWIDTHS:
            widths[idx] = _NARROW_COLWIDTHS[k]
            fixed_total += widths[idx]
        else:
            remaining_idxs.append(idx)

    remaining_budget = max(_TABLE_WIDTH_BUDGET_PX - fixed_total, 200)
    wide_idxs = [idx for idx in remaining_idxs if keys[idx] in _WIDE_COLUMN_NAMES]
    plain_idxs = [idx for idx in remaining_idxs if idx not in wide_idxs]

    if wide_idxs:
        wide_share = int(remaining_budget * 0.7 / len(wide_idxs))
        plain_budget = remaining_budget - wide_share * len(wide_idxs)
        plain_share = int(plain_budget / len(plain_idxs)) if plain_idxs else 0
        for idx in wide_idxs:
            widths[idx] = wide_share
        for idx in plain_idxs:
            widths[idx] = plain_share
    elif remaining_idxs:
        share = int(remaining_budget / len(remaining_idxs))
        for idx in remaining_idxs:
            widths[idx] = share

    return widths


def build_table(header_cells: list[str], rows: list[list[str]], layout: str = "default") -> dict:
    grid = [[{} for _ in header_cells]] + [[{} for _ in row] for row in rows]
    validate_table_grid(grid, table_label="table")
    colwidths = compute_colwidths(header_cells)

    def cell(text: str, header: bool, idx: int) -> dict:
        node_type = "tableHeader" if header else "tableCell"
        node = {"type": node_type, "content": [{"type": "paragraph", "content": parse_inline(text)}]}
        if colwidths:
            node["attrs"] = {"colspan": 1, "rowspan": 1, "colwidth": [colwidths[idx]]}
        return node

    table_rows = [{"type": "tableRow", "content": [cell(c, True, idx) for idx, c in enumerate(header_cells)]}]
    for row in rows:
        table_rows.append({"type": "tableRow", "content": [cell(c, False, idx) for idx, c in enumerate(row)]})

    return {
        "type": "table",
        "attrs": {"isNumberColumnEnabled": False, "layout": layout},
        "content": table_rows,
    }
