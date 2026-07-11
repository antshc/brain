# ADF Node Skeletons

Reference skeletons for the ADF nodes produced by the `markdown-to-adf` skill. Preserve source wording; use these only as structural templates.

## Root document

```json
{
  "version": 1,
  "type": "doc",
  "content": []
}
```

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

## Heading

Markdown:

```markdown
## Heading
```

ADF node:

```json
{
  "type": "heading",
  "attrs": {
    "level": 2
  },
  "content": [
    {
      "type": "text",
      "text": "Heading"
    }
  ]
}
```

## Table

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

Merged cell:

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

Cell with paragraph and bullet list:

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

## Expand (details/summary)

Maps `<details><summary>Title</summary>…</details>` to an ADF `expand` node.

```json
{
  "type": "expand",
  "attrs": {
    "title": "Response"
  },
  "content": [
    {
      "type": "paragraph",
      "content": [
        { "type": "text", "text": "" }
      ]
    }
  ]
}
```
