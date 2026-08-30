---
name: markdown-to-adf
description: Convert GitHub Flavored Markdown into Atlassian Document Format (ADF). Use when Jira or Confluence content contains tables, fenced code blocks, bullet lists, blockquotes, inline code, or other Markdown that must be represented as structured ADF.
---

# Convert Markdown to ADF

**Superseded** by `map-markdown-adf` (`plugins/atl/skills/map-markdown-adf/`), which replaces this skill's prose mapping tables with the single, tested, executable ADF implementation in both directions. Use that skill instead.

Convert user-provided GitHub Flavored Markdown into a valid Atlassian Document Format document while preserving the source wording and structure.

## Inputs

- **markdown** — source Markdown to convert.
- **target** — Jira or Confluence when target-specific behavior matters.

## Output

Return:

- `contentFormat: "adf"`
- a complete ADF root document (see [references/adf-skeletons.md](references/adf-skeletons.md))

Return only the converted ADF payload unless the caller requests an explanation.

## Workflow

1. Parse the Markdown block structure in source order.
2. Convert each block to the corresponding ADF node.
3. Convert supported inline Markdown to ADF marks.
4. Preserve source text, whitespace, line breaks, ordering, and nesting wherever ADF supports them.
5. Wrap all generated block nodes in a root `doc` node.
6. Validate required `type`, `content`, and `attrs` fields.
7. Validate table geometry: every row must resolve to the same effective column count after `colspan` and `rowspan` are applied.

## Block mapping

| Markdown | ADF |
| --- | --- |
| Paragraph | `paragraph` |
| Heading | `heading` with `attrs.level` |
| Bullet list | `bulletList` containing `listItem` nodes |
| Ordered list | `orderedList` containing `listItem` nodes |
| Blockquote | `blockquote` |
| Fenced code block | `codeBlock` |
| Table | `table` containing `tableRow`, `tableHeader`, and `tableCell` nodes |
| Horizontal rule | `rule` |
| `<details>`/`<summary>` | `expand` with `attrs.title` |

## Inline mapping

| Markdown | ADF mark |
| --- | --- |
| `**strong**` | `strong` |
| `*emphasis*` | `em` |
| `` `code` `` | `code` |
| `[text](url)` | `link` with `attrs.href` |
| `~~deleted~~` | `strike` |

## General rules

- **Do not rephrase.** Preserve wording verbatim. Do not summarize, correct, improve, or reinterpret the source.
- Do not invent headings, paragraphs, list items, table rows, cells, or formatting.
- Preserve block order exactly.
- Preserve fenced-code content exactly, including internal newlines and indentation.
- Use the fenced language identifier as `codeBlock.attrs.language` when present.
- Map GFM `-`, `*`, and `+` list markers to `bulletList` nodes.
- Preserve nested lists. Place the nested list inside the parent `listItem`, after its paragraph.
- Map `>` blockquotes to `blockquote`; do not emit the literal `>` marker.
- Do not leave Markdown syntax such as fences, list markers, table pipes, blockquote markers, or link syntax in converted text.
- Do not mix Markdown strings into an ADF description. Once ADF is selected, convert the complete description into one root document.

## Text node

See [references/adf-skeletons.md](references/adf-skeletons.md).

## Paragraph

See [references/adf-skeletons.md](references/adf-skeletons.md).

## Heading

See [references/adf-skeletons.md](references/adf-skeletons.md).

### Heading mapping

| Markdown | ADF |
| --- | --- |
| `#` | `heading` with `attrs.level: 1` |
| `##` | `heading` with `attrs.level: 2` |
| `###` | `heading` with `attrs.level: 3` |
| `####` | `heading` with `attrs.level: 4` |
| `#####` | `heading` with `attrs.level: 5` |
| `######` | `heading` with `attrs.level: 6` |

### Heading rules

- Preserve the Markdown heading level exactly.
- Do not promote or demote headings.
- Remove the Markdown `#` markers from the emitted text.
- Emit heading content as inline nodes.
- Preserve supported inline marks inside headings.
- Use heading levels `1` through `6` only.

## Tables

### Markdown conversion rules

- Treat the first row of a GFM table as header cells and emit `tableHeader` nodes.
- Emit subsequent rows as `tableCell` nodes.
- Do not emit the Markdown separator row.
- Use an empty `paragraph` for an otherwise empty cell.
- Preserve inline marks inside cell paragraphs.
- Plain GFM does not represent merged cells, background colors, or explicit column widths. Add those attributes only when the calling skill or user explicitly specifies them.
- Markdown alignment markers such as `:---`, `:---:`, and `---:` have no reliable portable ADF cell-alignment equivalent. Preserve cell content and omit alignment unless the target integration explicitly supports it.

### Table skeleton

See [references/adf-skeletons.md](references/adf-skeletons.md).

### Supported table nodes

| Purpose | ADF node |
| --- | --- |
| Table | `table` |
| Row | `tableRow` |
| Header cell | `tableHeader` |
| Body cell | `tableCell` |
| Cell paragraph | `paragraph` |
| Cell bullet list | `bulletList` |
| Cell ordered list | `orderedList` |
| Cell code block | `codeBlock` |

ADF does not use HTML table wrappers such as `thead`, `tbody`, `tr`, `th`, or `td`.

### Table attributes

Supported `table.attrs` commonly include:

- `isNumberColumnEnabled` — show or hide the table number column.
- `layout` — target-supported table layout, normally `default`, `wide`, or `full-width`.
- `displayMode` — target-supported display mode; use `default` unless explicitly requested.
- `width` — explicit table width where supported by the target.

Do not invent non-ADF CSS properties on the table.

### Cell attributes

`tableCell` and `tableHeader` may use:

- `background` — cell background color as a hexadecimal string, for example `#F0F1F2`.
- `colspan` — number of columns covered horizontally.
- `rowspan` — number of rows covered vertically.
- `colwidth` — array of column widths in pixels.

See the merged cell example in [references/adf-skeletons.md](references/adf-skeletons.md).

### Table geometry rules

- `colspan` and `rowspan` must be positive integers.
- For a merged cell, `colwidth` must contain one width entry per spanned column.
- Keep column widths consistent across rows representing the same logical columns.
- Do not emit placeholder cells inside columns already occupied by a preceding cell's `rowspan`.
- The effective column count of every row must match the table width after spans are resolved.
- Use `tableHeader` only for semantic header cells; use `tableCell` for body cells even when body text is bold.
- Apply `background` explicitly to every cell requiring color. ADF has no CSS selectors such as `nth-child` and no inherited row background.
- Omit optional attributes when they are unknown rather than inventing values.

### Content allowed inside cells

Cells contain block nodes, not bare text nodes. Typical content includes:

- `paragraph`
- `bulletList`
- `orderedList`
- `codeBlock`
- `blockquote`
- supported nested block content accepted by the target

See the cell with paragraph and bullet list example in [references/adf-skeletons.md](references/adf-skeletons.md).

### Unsupported CSS-style table formatting

Do not attempt to encode these as arbitrary ADF attributes:

- custom border width, style, or color
- cell padding
- font family
- CSS margins
- CSS selectors
- vertical alignment
- arbitrary text alignment
- list indentation or item spacing

Jira or Confluence controls these during rendering. Never place CSS strings in `attrs` as a workaround.

## Fenced code block

See [references/adf-skeletons.md](references/adf-skeletons.md).

## Nested bullet list

See [references/adf-skeletons.md](references/adf-skeletons.md).

## Blockquote

See [references/adf-skeletons.md](references/adf-skeletons.md).

## Expand (details/summary)

Maps `<details><summary>Title</summary>…</details>` to an ADF `expand` node. See [references/adf-skeletons.md](references/adf-skeletons.md).

### Expand rules

- Use `attrs.title` for the `<summary>` text.
- `content` must contain at least one block node; use an empty `paragraph` when the body is empty.
- Use `nestedExpand` instead of `expand` when the node appears inside a `tableCell` or `tableHeader`.
- Do not nest `expand` inside `expand`; ADF does not support recursive expansion.

## Resources

- [ADF node skeletons](references/adf-skeletons.md)
- [Atlassian Document Format](https://developer.atlassian.com/cloud/jira/platform/apis/document/structure/)
- [ADF table node](https://developer.atlassian.com/cloud/jira/platform/apis/document/nodes/table/)
- [ADF table cell node](https://developer.atlassian.com/cloud/jira/platform/apis/document/nodes/table_cell/)
- [ADF table header node](https://developer.atlassian.com/cloud/jira/platform/apis/document/nodes/table_header/)
- [GitHub Flavored Markdown specification](https://github.github.com/gfm/)
