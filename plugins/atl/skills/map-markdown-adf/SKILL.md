---
name: map-markdown-adf
description: Convert Markdown to Atlassian Document Format (ADF) and back, and detect the constructs only ADF can express, through the single shared conversion capability for the `atl` plugin. Use when a skill needs to send Markdown to Jira/Confluence as ADF, needs to read a fetched ADF body back as Markdown, or needs to decide whether Markdown alone will carry a document. Preserves source wording verbatim — never summarizes, corrects, or reinterprets content.
---

# Map Markdown <-> ADF

The conversion capability shared by every `atl` skill that reads or publishes content. One CLI, both directions plus a detection gate, pure and offline — no filesystem, no config, no network.

## Setup

`pytest` (dev-only, for tests) is installed once by `/init-atl` for the whole `atl` plugin. The CLI itself has no third-party runtime dependencies.

## Action: Convert Markdown to ADF

From the directory holding this `SKILL.md`:

```bash
python scripts/map_markdown_adf.py md-to-adf < input.md > output.json
```

Stdin Markdown → stdout one ADF document (`{"version": 1, "type": "doc", "content": [...]}`).

## Action: Convert ADF to Markdown

```bash
python scripts/map_markdown_adf.py adf-to-md < input.json > output.md
```

Stdin one ADF document → stdout Markdown. A Draw.io macro (`extension`) becomes a `<!-- adf:diagram ... -->` placeholder naming the diagram. A `media`/`mediaSingle`/`mediaGroup` node (a `mediaGroup` can hold more than one file) becomes a neutral `<!-- adf:attachment ... -->` placeholder per file — it could be a diagram, a plain image, or an arbitrary attached file; classifying and resolving it is `/fetch-page`'s job for a Confluence page (matching by `media-id`) and `/fetch-work`'s job for a Jira issue (matching by filename via `alt` — see its own SKILL.md), not this converter's. When the source `media` node carries both `width` and `height` (an image attached through the Confluence/Jira UI, never a generic-file `mediaGroup` node), the placeholder also carries `width="<w>" height="<h>"` so the caller can pass that reported size along. Every other unrecognized node type still raises `NotImplementedError`.

## Action: Detect ADF-only constructs

```bash
python scripts/map_markdown_adf.py detect-adf-only < input.md > report.json
```

Stdin Markdown → stdout `{"adfOnly": <bool>, "constructs": [{"kind": ..., "line": <1-based>}]}`, listing every construct marked **ADF-only** in Supported structure, in source order. Kinds are `expand`, `panel`, `status`, `toc`, `wideTable`. Markers inside a fenced code block are literal text and go unreported.

Exits `0` whether or not anything is found — branch on `adfOnly`, not the exit code. `adfOnly: false` means the source is plain CommonMark and a caller may publish it as-is with `contentFormat: "markdown"`; `adfOnly: true` means it must convert first.

## Preserved verbatim

Source wording is never summarized, corrected, or reinterpreted in either direction — only structure and marks are translated.

## Supported structure

Rows marked **ADF-only** have no Markdown equivalent on the Atlassian side — `detect-adf-only` reports them so a caller knows Markdown alone will not carry the document.

| Markdown | ADF |
| --- | --- |
| Paragraph | `paragraph` |
| Heading (`#`–`######`) | `heading` (`attrs.level`) |
| Bullet list (`-`, `*`, `+`) | `bulletList` / `listItem` |
| Ordered list | `orderedList` / `listItem` |
| Blockquote (`>`) | `blockquote` |
| `> [!INFO]` / `[!NOTE]` / `[!WARNING]` / `[!SUCCESS]` / `[!ERROR]` blockquote | `panel` (`attrs.panelType`) — **ADF-only** |
| Fenced code block | `codeBlock` (`attrs.language` when recognized) |
| Table | `table` / `tableRow` / `tableHeader` / `tableCell` |
| Horizontal rule (`---`) | `rule` |
| `<details><summary>` | `expand` (`attrs.title`) — **ADF-only** |
| `<!-- adf:toc -->` | `expand` + `toc` extension — **ADF-only** |
| `<!-- adf:wide-table -->` | `table.attrs.layout: "wide"` — **ADF-only** |
| `<!-- adf:diagram drawio="<name>" -->` | `extension` (Draw.io macro) — **ADF-only, `adf-to-md` direction only** |
| `<!-- adf:attachment media-id="<id>" alt="<alt>" [width="<w>" height="<h>"] -->` | `mediaSingle`/`media`/`mediaGroup` (one placeholder per file) — **ADF-only, `adf-to-md` direction only** |

A list item's soft-wrapped continuation lines fold into its paragraph, joined by a single space. `- first line` followed by `  continues here` is one `listItem`, not a list plus a stray paragraph:

```json
{"type": "bulletList", "content": [
  {"type": "listItem", "content": [
    {"type": "paragraph", "content": [{"type": "text", "text": "first line continues here"}]}]}]}
```

Marks spanning the join survive, so `- lead **bold` + `  spanning** tail` yields one `strong` span reading `bold spanning`. A deeper-indented marker still nests, and any block start — heading, table, fence, rule, blockquote, `</details>`, or a Confluence marker comment — ends the list instead of folding into it.

## Supported marks

`**strong**`, `*em*`, `` `code` ``, `[link](href)`, `~~strike~~`.

Marks nest and combine onto one text node, innermost first: `` [`Foo.Bar`](href) `` is a single text node carrying `code` **and** `link`, and `**[label](href)**` carries `link` **and** `strong`. A partly marked label splits into several nodes that all keep the outer mark. Both directions agree — `adf-to-md` re-wraps a combined node in the same order. A code span's content is literal, so nothing nests inside it.

`[STATUS:text|color]` maps to the inline `status` node — **ADF-only** (`color` one of `neutral`, `purple`, `blue`, `red`, `yellow`, `green`; defaults to `neutral` when omitted).

## Table validation

Every table's rows must resolve to one consistent column count once `colspan`/`rowspan` are applied. A mismatched table is rejected — non-zero exit, `error:` on stderr naming the table — with no partial output.

## Verification

`python -m pytest plugins/atl/skills/map-markdown-adf/` (from the repo root). Tests invoke the CLI as a subprocess — the only test seam — and assert only on emitted JSON/Markdown, never on which internal module produced it.
