---
name: map-markdown-adf
description: Convert Markdown to Atlassian Document Format (ADF) and back, through the single shared conversion capability for the `atl` plugin. Use when a skill needs to send Markdown to Jira/Confluence as ADF, or needs to read a fetched ADF body back as Markdown. Preserves source wording verbatim — never summarizes, corrects, or reinterprets content.
---

# Map Markdown <-> ADF

The single conversion capability shared by every `atl` skill that reads or publishes content. One CLI, both directions, pure and offline — no filesystem, no configuration, no network.

## Setup

`pip install -r requirements.txt` (relative to this skill's directory) — dev-only, for running tests. The CLI itself has no third-party runtime dependencies.

## Action: Convert Markdown to ADF

Run, from the directory holding this `SKILL.md`:

```bash
python3 scripts/map_markdown_adf.py md-to-adf < input.md > output.json
```

Reads Markdown from stdin, writes one ADF JSON document (`{"version": 1, "type": "doc", "content": [...]}`) to stdout.

## Action: Convert ADF to Markdown

```bash
python3 scripts/map_markdown_adf.py adf-to-md < input.json > output.md
```

Reads one ADF JSON document from stdin, writes Markdown to stdout.

## Preserved verbatim

Source wording is never summarized, corrected, or reinterpreted in either direction — only structure and marks are translated.

## Supported structure

| Markdown | ADF |
| --- | --- |
| Paragraph | `paragraph` |
| Heading (`#`–`######`) | `heading` (`attrs.level`) |
| Bullet list (`-`, `*`, `+`) | `bulletList` / `listItem` |
| Ordered list | `orderedList` / `listItem` |
| Blockquote (`>`) | `blockquote` |
| Fenced code block | `codeBlock` (`attrs.language` when recognized) |
| Table | `table` / `tableRow` / `tableHeader` / `tableCell` |
| Horizontal rule (`---`) | `rule` |
| `<details><summary>` | `expand` (`attrs.title`) |

## Supported marks

`**strong**`, `*em*`, `` `code` ``, `[link](href)`, `~~strike~~`.

## Table validation

Every table's rows must resolve to one consistent column count once `colspan`/`rowspan` are applied. A mismatched table is rejected — non-zero exit, an `error:` message on stderr naming the table as the cause — and no partial output is produced.

## Verification

Run `python3 -m pytest plugins/atl/skills/map-markdown-adf/` (from the repo root). Tests invoke the CLI as a subprocess — the only test seam — and assert only on the JSON/Markdown it emits, never on which internal module produced it.
