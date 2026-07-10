---
name: markdown-to-adf
description: Convert GitHub Flavored Markdown into Atlassian Document Format (ADF). Use when Jira or Confluence content contains tables, fenced code blocks, bullet lists, blockquotes, inline code, or other Markdown that must be represented as structured ADF.
---

# Convert Markdown to ADF

Convert user-provided GitHub Flavored Markdown into a valid Atlassian Document Format document while preserving the source wording and structure.

## Inputs

- **markdown** — source Markdown to convert.
- **target** — Jira or Confluence when target-specific behavior matters.

## Output

Return:

- `contentFormat: "adf"`
- a complete ADF root document:

```json
{
  "version": 1,
  "type": "doc",
  "content": []
}
```

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

```json
{
  "type": "text",
  "text": "Text"
}
```

Text with marks:

```json
{
  "type": "text",
  "text": "identifier",
  "marks": [
    { "type": "code" }
  ]
}
```

## Paragraph

```json
{
  "type": "paragraph",
  "content": [
    { "type": "text", "text": "Paragraph text" }
  ]
}
```

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

```json
{
  "type": "table",
  "attrs": {
    "isNumberColumnEnabled": false,
    "layout": "default",
    "displayMode": "default"
  },
  "content": [
    {
      "type": "tableRow",
      "content": [
        {
          "type": "tableHeader",
          "attrs": {
            "background": "#F0F1F2",
            "colspan": 1,
            "rowspan": 1,
            "colwidth": [240]
          },
          "content": [
            {
              "type": "paragraph",
              "content": [
                {
                  "type": "text",
                  "text": "Header",
                  "marks": [{ "type": "strong" }]
                }
              ]
            }
          ]
        }
      ]
    },
    {
      "type": "tableRow",
      "content": [
        {
          "type": "tableCell",
          "attrs": {
            "colspan": 1,
            "rowspan": 1,
            "colwidth": [240]
          },
          "content": [
            {
              "type": "paragraph",
              "content": [
                { "type": "text", "text": "Value" }
              ]
            }
          ]
        }
      ]
    }
  ]
}
```

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

Example merged cell:

```json
{
  "type": "tableCell",
  "attrs": {
    "background": "#F0F1F2",
    "colspan": 4,
    "rowspan": 1,
    "colwidth": [80, 460, 140, 180]
  },
  "content": [
    {
      "type": "paragraph",
      "content": [
        { "type": "text", "text": "Merged content" }
      ]
    }
  ]
}
```

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

Example cell with paragraph and bullet list:

```json
{
  "type": "tableCell",
  "content": [
    {
      "type": "paragraph",
      "content": [
        { "type": "text", "text": "Summary" }
      ]
    },
    {
      "type": "bulletList",
      "content": [
        {
          "type": "listItem",
          "content": [
            {
              "type": "paragraph",
              "content": [
                { "type": "text", "text": "Item" }
              ]
            }
          ]
        }
      ]
    }
  ]
}
```

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

Markdown:

````markdown
```text
line1
line2
```
````

ADF node:

```json
{
  "type": "codeBlock",
  "attrs": {
    "language": "text"
  },
  "content": [
    {
      "type": "text",
      "text": "line1\nline2"
    }
  ]
}
```

## Nested bullet list

Markdown:

```markdown
- Level 1
  - Level 2
    - Level 3
```

ADF node:

```json
{
  "type": "bulletList",
  "content": [
    {
      "type": "listItem",
      "content": [
        {
          "type": "paragraph",
          "content": [
            { "type": "text", "text": "Level 1" }
          ]
        },
        {
          "type": "bulletList",
          "content": [
            {
              "type": "listItem",
              "content": [
                {
                  "type": "paragraph",
                  "content": [
                    { "type": "text", "text": "Level 2" }
                  ]
                },
                {
                  "type": "bulletList",
                  "content": [
                    {
                      "type": "listItem",
                      "content": [
                        {
                          "type": "paragraph",
                          "content": [
                            { "type": "text", "text": "Level 3" }
                          ]
                        }
                      ]
                    }
                  ]
                }
              ]
            }
          ]
        }
      ]
    }
  ]
}
```

## Blockquote

```json
{
  "type": "blockquote",
  "content": [
    {
      "type": "paragraph",
      "content": [
        { "type": "text", "text": "Quote" }
      ]
    }
  ]
}
```

## Complete example

Markdown:

````markdown
## Contract changes

- Add endpoint `POST /jobs`
- Return:

```json
{"id":"123"}
```
````

ADF:

```json
{
  "version": 1,
  "type": "doc",
  "content": [
    {
      "type": "heading",
      "attrs": { "level": 2 },
      "content": [
        { "type": "text", "text": "Contract changes" }
      ]
    },
    {
      "type": "bulletList",
      "content": [
        {
          "type": "listItem",
          "content": [
            {
              "type": "paragraph",
              "content": [
                { "type": "text", "text": "Add endpoint " },
                {
                  "type": "text",
                  "text": "POST /jobs",
                  "marks": [{ "type": "code" }]
                }
              ]
            }
          ]
        },
        {
          "type": "listItem",
          "content": [
            {
              "type": "paragraph",
              "content": [
                { "type": "text", "text": "Return:" }
              ]
            },
            {
              "type": "codeBlock",
              "attrs": { "language": "json" },
              "content": [
                { "type": "text", "text": "{\"id\":\"123\"}" }
              ]
            }
          ]
        }
      ]
    }
  ]
}
```

## Resources

- [Atlassian Document Format](https://developer.atlassian.com/cloud/jira/platform/apis/document/structure/)
- [ADF table node](https://developer.atlassian.com/cloud/jira/platform/apis/document/nodes/table/)
- [ADF table cell node](https://developer.atlassian.com/cloud/jira/platform/apis/document/nodes/table_cell/)
- [ADF table header node](https://developer.atlassian.com/cloud/jira/platform/apis/document/nodes/table_header/)
- [GitHub Flavored Markdown specification](https://github.github.com/gfm/)
