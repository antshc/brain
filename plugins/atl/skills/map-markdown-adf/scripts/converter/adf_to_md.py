"""Atlassian Document Format -> Markdown entrypoint (pure)."""
from __future__ import annotations

from .patterns import COMMENT_CLOSE_TAG, STATUS_EMOJI, comment_open_tag
from .table_grid import validate_table_grid

# Applied innermost-first, so combined marks on one text node wrap in a fixed order
# regardless of the order they appear in `marks` (code+link -> [`text`](href)).
_MARK_ORDER = ("code", "strike", "em", "strong", "link")

# Confluence stores a `bash` code block as `shell`; read it back as `bash` so the common fence
# round-trips unchanged (Confluence keeps no distinction between the two).
_LANGUAGE_ALIASES = {"shell": "bash"}


def adf_to_markdown(doc: dict) -> str:
    if not isinstance(doc, dict):
        raise ValueError(f"ADF body must be a parsed JSON object, got {type(doc).__name__}")
    return render_blocks(doc.get("content", []))


def render_blocks(nodes: list[dict]) -> str:
    return "\n\n".join(s for s in (render_block(n) for n in nodes) if s != "")


def render_block(node: dict) -> str:
    rendered = _render_block_body(node)
    breakout = next((m for m in node.get("marks", []) if m.get("type") == "breakout"), None)
    if breakout and rendered:
        return f"{_breakout_marker(breakout.get('attrs', {}))}\n{rendered}"
    return rendered


def _breakout_marker(attrs: dict) -> str:
    fields = "".join(f' {key}="{_number(value) if key == "width" else value}"' for key, value in attrs.items())
    return f"<!-- adf:breakout{fields} -->"


def _table_marker(attrs: dict) -> str:
    """`adf:wide-table` for a plain wide table, `adf:table` when a width or another layout must
    survive, "" for a default table."""
    layout, width = attrs.get("layout"), attrs.get("width")
    if width is None:
        if layout == "wide":
            return "<!-- adf:wide-table -->"
        if layout in (None, "default"):
            return ""
    fields = f' layout="{layout}"' if layout not in (None, "default") else ""
    if width is not None:
        fields += f' width="{_number(width)}"'
    return f"<!-- adf:table{fields} -->"


def _render_block_body(node: dict) -> str:
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
    if node_type == "panel":
        panel_type = node.get("attrs", {}).get("panelType", "info").upper()
        inner = render_blocks(node.get("content", []))
        lines = [f"[!{panel_type}]"] + inner.split("\n")
        return "\n".join(f"> {line}" if line else ">" for line in lines)
    if node_type == "codeBlock":
        lang = node.get("attrs", {}).get("language", "")
        lang = _LANGUAGE_ALIASES.get(lang, lang)
        text = "".join(c.get("text", "") for c in node.get("content", []))
        return f"```{lang}\n{text}\n```"
    if node_type == "rule":
        return "---"
    if node_type == "expand":
        title = node.get("attrs", {}).get("title", "")
        content = node.get("content", [])
        if len(content) == 1 and content[0].get("attrs", {}).get("extensionKey") == "toc":
            return "<!-- adf:toc -->"
        inner = render_blocks(content)
        return f"<details>\n<summary>{title}</summary>\n\n{inner}\n</details>"
    if node_type == "table":
        rendered = render_table(node)
        marker = _table_marker(node.get("attrs", {}))
        return f"{marker}\n\n{rendered}" if marker else rendered
    if node_type == "extension":
        extension_key = node.get("attrs", {}).get("extensionKey", "")
        if extension_key == "toc":
            return "<!-- adf:toc -->"
        if "static/drawio" in extension_key:
            diagram_name = (
                node.get("attrs", {}).get("parameters", {}).get("guestParams", {}).get("diagramName", "")
            )
            return f'<!-- adf:diagram drawio="{diagram_name}" -->'
        if extension_key == "drawio":
            diagram_name = (
                node.get("attrs", {}).get("parameters", {}).get("macroParams", {})
                .get("diagramName", {}).get("value", "")
            )
            return f'<!-- adf:diagram drawio="{diagram_name}" -->'
        raise NotImplementedError(f"unhandled ADF extension '{extension_key}'")
    if node_type in ("mediaSingle", "media"):
        media_node = node if node_type == "media" else next(
            (c for c in node.get("content", []) if c.get("type") == "media"), None
        )
        if media_node is not None:
            return _attachment_placeholder(media_node, node.get("attrs", {}) if node_type == "mediaSingle" else None)
        raise NotImplementedError("unhandled ADF mediaSingle with no media child")
    if node_type == "mediaGroup":
        media_nodes = [c for c in node.get("content", []) if c.get("type") == "media"]
        if media_nodes:
            return "\n\n".join(_attachment_placeholder(m) for m in media_nodes)
        raise NotImplementedError("unhandled ADF mediaGroup with no media children")
    raise NotImplementedError(f"unhandled ADF node type '{node_type}'")


def _attachment_placeholder(media_node: dict, single_attrs: dict | None = None) -> str:
    """A `media` node's neutral placeholder — could be a diagram, a plain image, or a generic
    file; `/fetch-page` classifies and resolves it, this converter only names it.

    Also carries `width`/`height` when the node has both (an image `media` node inside a
    `mediaSingle`, never a `mediaGroup` generic-file node) — the only place Confluence's own
    reported pixel size is ever captured, so `/fetch-page` can pass it along. A `mediaSingle`
    parent adds its display size as `display-width` (`<n>` pixels, `<n>%` percentage) and a
    non-default `layout`, so a republish shows the image at the size and position it had.
    """
    attrs = media_node.get("attrs", {})
    media_id = attrs.get("id", "")
    alt = attrs.get("alt", "")
    placeholder = f'<!-- adf:attachment media-id="{media_id}" alt="{alt}"'
    width, height = attrs.get("width"), attrs.get("height")
    if width is not None and height is not None:
        placeholder += f' width="{width}" height="{height}"'
    single_attrs = single_attrs or {}
    display_width = single_attrs.get("width")
    if display_width is not None:
        suffix = "%" if single_attrs.get("widthType") == "percentage" else ""
        placeholder += f' display-width="{_number(display_width)}{suffix}"'
    layout = single_attrs.get("layout")
    if layout and layout != "center":
        placeholder += f' layout="{layout}"'
    return placeholder + " -->"


def _number(value: float | int) -> str:
    return str(int(value)) if float(value).is_integer() else str(value)


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
    column_count = validate_table_grid(grid, table_label="table")

    lines: list[str] = []
    pending_rowspans: dict[int, int] = {}
    for row in rows:
        cells = [c for c in row.get("content", []) if c.get("type") in ("tableHeader", "tableCell")]
        is_header_row = any(c.get("type") == "tableHeader" for c in cells)
        rendered = [""] * column_count
        column = 0
        next_rowspans = {
            index: remaining - 1
            for index, remaining in pending_rowspans.items()
            if remaining > 1
        }
        for cell in cells:
            while column in pending_rowspans:
                column += 1
            attrs = cell.get("attrs", {})
            colspan = int(attrs.get("colspan", 1) or 1)
            rowspan = int(attrs.get("rowspan", 1) or 1)
            rendered[column] = render_table_cell(cell)
            if rowspan > 1:
                for index in range(column, column + colspan):
                    next_rowspans[index] = rowspan - 1
            column += colspan
        lines.append("| " + " | ".join(rendered) + " |")
        if is_header_row:
            lines.append("| " + " | ".join(["---"] * column_count) + " |")
        pending_rowspans = next_rowspans
    return "\n".join(lines)


def render_table_cell(cell: dict) -> str:
    parts = []
    for block in cell.get("content", []):
        if block.get("type") == "paragraph":
            parts.append(render_inline(block.get("content", [])).replace("  \n", "<br>"))
        else:
            parts.append(render_block(block))
    return " ".join(p.replace("\n", " ") for p in parts if p)


def _comment_ids(node: dict) -> list[str]:
    """Inline-comment annotation ids on a node; other annotation types have no Markdown form."""
    ids = []
    for mark in node.get("marks", []):
        attrs = mark.get("attrs", {})
        if mark.get("type") == "annotation" and attrs.get("annotationType", "inlineComment") == "inlineComment":
            if attrs.get("id") and attrs["id"] not in ids:
                ids.append(attrs["id"])
    return ids


def render_inline(nodes: list[dict]) -> str:
    parts = []
    open_ids: list[str] = []
    for node in nodes:
        # Keep the longest still-wanted prefix of open comment spans; close the rest, then open
        # what this node adds. Consecutive nodes sharing an id render as one span.
        wanted = _comment_ids(node)
        keep = 0
        while keep < len(open_ids) and open_ids[keep] in wanted:
            keep += 1
        parts.extend(COMMENT_CLOSE_TAG for _ in open_ids[keep:])
        open_ids = open_ids[:keep]
        for comment_id in wanted:
            if comment_id not in open_ids:
                parts.append(comment_open_tag(comment_id))
                open_ids.append(comment_id)
        node_type = node.get("type")
        if node_type == "text":
            parts.append(render_text(node))
        elif node_type == "hardBreak":
            parts.append("  \n")
        elif node_type == "status":
            parts.append(render_status(node))
        elif node_type == "inlineCard":
            parts.append(render_inline_card(node))
        elif node_type == "inlineExtension":
            parts.append(render_inline_extension(node))
        else:
            raise NotImplementedError(f"unhandled inline node type '{node_type}'")
    parts.extend(COMMENT_CLOSE_TAG for _ in open_ids)
    return "".join(parts)


def render_inline_card(node: dict) -> str:
    url = node.get("attrs", {}).get("url", "")
    if not url:
        raise ValueError("inlineCard node is missing a non-empty url")
    return f"[{url}]({url})"


def render_inline_extension(node: dict) -> str:
    extension_key = node.get("attrs", {}).get("extensionKey", "")
    if extension_key in ("create-from-template", "anchor"):
        return ""
    else:
        raise NotImplementedError(f"unhandled ADF inline extension '{extension_key}'")


def render_status(node: dict) -> str:
    attrs = node.get("attrs", {})
    text = attrs.get("text", "")
    color = attrs.get("color", "neutral")
    emoji = STATUS_EMOJI.get(color)
    return f"{emoji}[{text}]" if emoji else f"[STATUS:{text}|{color}]"


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
