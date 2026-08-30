"""Block-level Markdown -> ADF parsing (pure): headings, lists, tables, quotes, code, and
`<details>` expands.
"""
from __future__ import annotations

import re

from .inline import parse_inline
from .patterns import HEADING_RE
from .table_grid import validate_table_grid

CODE_LANG_ALLOWLIST = {
    "text",
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
_RULE_RE = re.compile(r"^(-{3,}|\*{3,}|_{3,})\s*$")
_TABLE_ROW_RE = re.compile(r"^\|(.*)\|\s*$")
_TABLE_SEP_RE = re.compile(r"^\|[\s:|-]+\|\s*$")
_FENCE_OPEN_RE = re.compile(r"^```(\w*)\s*$")
_DETAILS_OPEN_RE = re.compile(r"^\s*<details>\s*$")
_DETAILS_CLOSE_RE = re.compile(r"^\s*</details>\s*$")
_SUMMARY_RE = re.compile(r"^\s*<summary>(.*)</summary>\s*$")


def split_table_row(row: str) -> list[str]:
    row = row.strip()
    if row.startswith("|"):
        row = row[1:]
    if row.endswith("|"):
        row = row[:-1]
    # Split on unescaped pipes.
    cells = re.split(r"(?<!\\)\|", row)
    return [c.strip().replace("\\|", "|") for c in cells]


def parse_blocks(lines: list[str]) -> list[dict]:
    """Parse a list of Markdown lines into ADF block nodes."""
    blocks: list[dict] = []
    i = 0
    n = len(lines)
    while i < n:
        line = lines[i]

        if not line.strip():
            i += 1
            continue

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
            blocks.append(node)
            continue

        if line.startswith(">"):
            quote_lines = []
            while i < n and lines[i].startswith(">"):
                quote_lines.append(re.sub(r"^>\s?", "", lines[i]))
                i += 1
            blocks.append({"type": "blockquote", "content": paragraphs_from_lines(quote_lines)})
            continue

        if _DETAILS_OPEN_RE.match(line):
            i += 1
            title = ""
            if i < n:
                sm = _SUMMARY_RE.match(lines[i])
                if sm:
                    title = sm.group(1).strip()
                    i += 1
            inner_lines = []
            depth = 1
            while i < n and depth > 0:
                if _DETAILS_OPEN_RE.match(lines[i]):
                    depth += 1
                elif _DETAILS_CLOSE_RE.match(lines[i]):
                    depth -= 1
                    if depth == 0:
                        i += 1
                        break
                inner_lines.append(lines[i])
                i += 1
            content = parse_blocks(inner_lines)
            if not content:
                content = [{"type": "paragraph", "content": [{"type": "text", "text": ""}]}]
            blocks.append({"type": "expand", "attrs": {"title": title}, "content": content})
            continue

        if _TABLE_ROW_RE.match(line) and i + 1 < n and _TABLE_SEP_RE.match(lines[i + 1]):
            header_cells = split_table_row(line)
            i += 2
            rows = []
            while i < n and _TABLE_ROW_RE.match(lines[i]):
                rows.append(split_table_row(lines[i]))
                i += 1
            blocks.append(build_table(header_cells, rows))
            continue

        if _BULLET_RE.match(line) or _ORDERED_RE.match(line):
            list_block, i = parse_list(lines, i)
            blocks.append(list_block)
            continue

        # Paragraph: consume consecutive plain lines until a blank line or block start.
        para_lines = []
        while i < n and lines[i].strip() and not _is_block_start(lines[i], lines, i):
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
    if _DETAILS_OPEN_RE.match(line) or _DETAILS_CLOSE_RE.match(line):
        return True
    if _TABLE_ROW_RE.match(line) and i + 1 < len(lines) and _TABLE_SEP_RE.match(lines[i + 1]):
        return True
    if _BULLET_RE.match(line) or _ORDERED_RE.match(line):
        return True
    return False


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


def parse_list(lines: list[str], i: int) -> tuple[dict, int]:
    n = len(lines)
    is_ordered, first_m = _match_list_marker(lines[i])
    base_indent = len(first_m.group(1))
    list_type = "orderedList" if is_ordered else "bulletList"
    items: list[dict] = []

    while i < n:
        line = lines[i]
        if not line.strip():
            # A single blank line inside a tight list doesn't necessarily end it;
            # stop when the following line isn't this same list (different marker
            # type at the same level ends it, so a new list can start after it).
            nxt_ordered, nxt_m = _match_list_marker(lines[i + 1]) if i + 1 < n else (None, None)
            if nxt_m is None:
                break
            if len(nxt_m.group(1)) <= base_indent and nxt_ordered != is_ordered:
                break
            i += 1
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
            nested_block, i = parse_list(lines, i)
            if items:
                items[-1]["content"].append(nested_block)
            continue

        item_text = m.group(2)
        i += 1
        item_content = [{"type": "paragraph", "content": parse_inline(item_text)}]

        # Continuation: only a deeper-indented nested list is folded into this item.
        while i < n and lines[i].strip():
            _, sub_m = _match_list_marker(lines[i])
            if sub_m and len(sub_m.group(1)) > indent:
                nested_block, i = parse_list(lines, i)
                item_content.append(nested_block)
                continue
            break  # keep list-item parsing simple: one paragraph + optional nested list only

        items.append({"type": "listItem", "content": item_content})

    return {"type": list_type, "content": items}, i


def build_table(header_cells: list[str], rows: list[list[str]]) -> dict:
    grid = [[{} for _ in header_cells]] + [[{} for _ in row] for row in rows]
    validate_table_grid(grid, table_label="table")

    def cell(text: str, header: bool) -> dict:
        node_type = "tableHeader" if header else "tableCell"
        return {"type": node_type, "content": [{"type": "paragraph", "content": parse_inline(text)}]}

    table_rows = [{"type": "tableRow", "content": [cell(c, True) for c in header_cells]}]
    for row in rows:
        table_rows.append({"type": "tableRow", "content": [cell(c, False) for c in row]})

    return {
        "type": "table",
        "attrs": {"isNumberColumnEnabled": False, "layout": "default"},
        "content": table_rows,
    }
