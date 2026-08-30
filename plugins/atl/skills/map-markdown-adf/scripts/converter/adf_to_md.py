"""Atlassian Document Format -> Markdown entrypoint (pure)."""
from __future__ import annotations

from .table_grid import validate_table_grid

# Applied outermost-last so a single mark renders the same regardless of list order
# (nested/combined marks on one text node are a known limitation, not exercised here).
_MARK_ORDER = ("code", "strike", "em", "strong", "link")


def adf_to_markdown(doc: dict) -> str:
    return render_blocks(doc.get("content", []))


def render_blocks(nodes: list[dict]) -> str:
    return "\n\n".join(s for s in (render_block(n) for n in nodes) if s != "")


def render_block(node: dict) -> str:
    node_type = node.get("type")
    if node_type == "paragraph":
        return render_inline(node.get("content", []))
    if node_type == "heading":
        level = node.get("attrs", {}).get("level", 1)
        return f"{'#' * level} {render_inline(node.get('content', []))}"
    if node_type == "bulletList":
        return render_list(node, ordered=False)
    if node_type == "orderedList":
        return render_list(node, ordered=True)
    if node_type == "blockquote":
        inner = render_blocks(node.get("content", []))
        return "\n".join(f"> {line}" if line else ">" for line in inner.split("\n"))
    if node_type == "codeBlock":
        lang = node.get("attrs", {}).get("language", "")
        text = "".join(c.get("text", "") for c in node.get("content", []))
        return f"```{lang}\n{text}\n```"
    if node_type == "rule":
        return "---"
    if node_type == "expand":
        title = node.get("attrs", {}).get("title", "")
        inner = render_blocks(node.get("content", []))
        return f"<details>\n<summary>{title}</summary>\n\n{inner}\n</details>"
    if node_type == "table":
        return render_table(node)
    raise NotImplementedError(f"unhandled ADF node type '{node_type}'")


def render_list(node: dict, ordered: bool, depth: int = 0) -> str:
    indent = "  " * depth
    start = node.get("attrs", {}).get("order", 1) if ordered else None
    lines: list[str] = []
    for idx, item in enumerate(node.get("content", [])):
        marker = f"{start + idx}." if ordered else "-"
        item_lines = render_list_item(item, depth) or [""]
        first, *rest = item_lines
        lines.append(f"{indent}{marker} {first}")
        lines.extend(rest)
    return "\n".join(lines)


def render_list_item(item: dict, depth: int) -> list[str]:
    lines: list[str] = []
    for child in item.get("content", []):
        if child.get("type") in ("bulletList", "orderedList"):
            nested = render_list(child, ordered=(child["type"] == "orderedList"), depth=depth + 1)
            lines.extend(nested.split("\n"))
        else:
            lines.extend(render_block(child).split("\n"))
    return lines


def render_table(node: dict) -> str:
    rows = node.get("content", [])
    grid = []
    for row in rows:
        cells = [c for c in row.get("content", []) if c.get("type") in ("tableHeader", "tableCell")]
        grid.append([c.get("attrs", {}) for c in cells])
    validate_table_grid(grid, table_label="table")

    lines: list[str] = []
    for row in rows:
        cells = [c for c in row.get("content", []) if c.get("type") in ("tableHeader", "tableCell")]
        is_header_row = any(c.get("type") == "tableHeader" for c in cells)
        rendered = [render_table_cell(c) for c in cells]
        lines.append("| " + " | ".join(rendered) + " |")
        if is_header_row:
            lines.append("| " + " | ".join(["---"] * len(cells)) + " |")
    return "\n".join(lines)


def render_table_cell(cell: dict) -> str:
    parts = []
    for block in cell.get("content", []):
        if block.get("type") == "paragraph":
            parts.append(render_inline(block.get("content", [])))
        else:
            parts.append(render_block(block))
    return " ".join(p.replace("\n", " ") for p in parts if p)


def render_inline(nodes: list[dict]) -> str:
    parts = []
    for node in nodes:
        node_type = node.get("type")
        if node_type == "text":
            parts.append(render_text(node))
        elif node_type == "hardBreak":
            parts.append("  \n")
        else:
            raise NotImplementedError(f"unhandled inline node type '{node_type}'")
    return "".join(parts)


def render_text(node: dict) -> str:
    text = node.get("text", "")
    marks_by_type = {m.get("type"): m for m in node.get("marks", [])}
    for mark_type in _MARK_ORDER:
        mark = marks_by_type.get(mark_type)
        if mark is None:
            continue
        if mark_type == "code":
            text = f"`{text}`"
        elif mark_type == "strike":
            text = f"~~{text}~~"
        elif mark_type == "em":
            text = f"*{text}*"
        elif mark_type == "strong":
            text = f"**{text}**"
        elif mark_type == "link":
            href = mark.get("attrs", {}).get("href", "")
            text = f"[{text}]({href})"
    return text
