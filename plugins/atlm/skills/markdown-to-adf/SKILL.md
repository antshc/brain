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
6. Validate that every node has the required `type`, `content`, and `attrs` fields.

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

## Rules

- **Do not rephrase.** Preserve wording verbatim. Do not summarize, correct, improve, or reinterpret the source.
- Do not invent headings, paragraphs, list items, table rows, cells, or formatting.
- Preserve block order exactly.
- Preserve fenced-code content exactly, including internal newlines and indentation.
- Use the fenced language identifier as `codeBlock.attrs.language` when present.
- Map GFM `-`, `*`, and `+` list markers to `bulletList` nodes.
- Preserve nested lists. Place the nested list inside the parent `listItem`, after its paragraph.
- Map `>` blockquotes to `blockquote`; do not emit the literal `>` marker.
- Treat the first row of a GFM table as `tableHeader` cells and subsequent rows as `tableCell` cells.
- Do not emit the Markdown table separator row.
- Use empty paragraphs where ADF requires block content for an otherwise empty table cell.
- Wrap endpoint paths, identifiers, commands, and source inline-code spans in `code` marks only when they are inline code in the source or the calling skill explicitly requires it.
- Do not leave Markdown syntax such as fences, list markers, table pipes, blockquote markers, or link syntax in the converted text.
- Do not mix Markdown strings into an ADF description. Once ADF is selected, convert the complete description into one root document.

## Text node

```json
{
  "type": "text",
  "text": "Text"
}
```

Text nodes with marks:

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

## Table

Markdown:

```markdown
| Col |
| --- |
| val |
```

ADF node:

```json
{
  "type": "table",
  "attrs": {
    "isNumberColumnEnabled": false,
    "layout": "default"
  },
  "content": [
    {
      "type": "tableRow",
      "content": [
        {
          "type": "tableHeader",
          "content": [
            {
              "type": "paragraph",
              "content": [
                { "type": "text", "text": "Col" }
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
          "content": [
            {
              "type": "paragraph",
              "content": [
                { "type": "text", "text": "val" }
              ]
            }
          ]
        }
      ]
    }
  ]
}
```

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

Markdown:

```markdown
> Quote
>
> Second paragraph
```

ADF node:

```json
{
  "type": "blockquote",
  "content": [
    {
      "type": "paragraph",
      "content": [
        { "type": "text", "text": "Quote" }
      ]
    },
    {
      "type": "paragraph",
      "content": [
        { "type": "text", "text": "Second paragraph" }
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
- [GitHub Flavored Markdown specification](https://github.github.com/gfm/)
