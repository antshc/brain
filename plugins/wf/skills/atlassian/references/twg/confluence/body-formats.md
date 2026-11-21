---
description: Write Confluence page bodies as Markdown through atl, use the Markdown dialect for panels, expands, TOC, status, tables, comment anchors, diagrams, and load whiteboard SVG or database CSV specs.
---

# Confluence Body Formats

Page, live doc, and blog post bodies are Markdown. `<atl>` defaults `--format` to `md` and routes the body through the skill's Markdown → ADF converter, so the constructs below survive. Never pass `--format html`, storage XML, or `--native` for a body.

## Markdown

Read and write with the routed commands; no `body-formats` load or `--ack-body-formats` needed (accepted and ignored):

```bash
<atl> confluence content get <page> --output-file page.md
<atl> confluence content update <page> --body-file page.md [--title "<title>"]
<atl> confluence content create --content-type page --space-id <spaceId> [--parent-id <parentId>] --title "<title>" --body-file page.md
```

Standard Markdown (headings, lists, tables, code fences, links, `---`) plus this dialect:

| Construct | Markdown |
|---|---|
| Panel | `> [!INFO]` / `[!NOTE]` / `[!WARNING]` / `[!SUCCESS]` / `[!ERROR]` blockquote |
| Expand | `<details><summary>Title</summary>` … `</details>` |
| Table of contents | `<!-- adf:toc -->` |
| Wide table / table layout | `<!-- adf:wide-table -->` or `<!-- adf:table layout="<layout>" width="<px>" -->` on the line before the table |
| Breakout | `<!-- adf:breakout mode="wide\|full-width" -->` on the line before `<details>` or a code fence |
| Status lozenge | `🔵[In Progress]` (`⚪` `🟣` `🔵` `🔴` `🟡` `🟢`) |
| Inline-comment anchor | `<!-- adf:comment id="<id>" -->text<!-- /adf:comment -->`; keep id and span unchanged |
| Diagram | ```` ```mermaid ```` fence, optional `%% diagram-id: <id>` first line |
| Image / file | `![alt](<local path>)` / `[name](<local path>)`; uploaded as an attachment |
| Excluded from publish | `<!-- adf:ignore:start -->` … `<!-- adf:ignore:end -->` |

- Check a draft offline: `<atl> map-markdown detect-adf-only < page.md` lists the dialect constructs found.
- Mentions, Jira macros, page trees, and other app macros have no Markdown form. On an existing page, edit around them only after a fetch shows they are absent; otherwise report that the page holds content this path cannot rewrite and ask the user.
- Never invent ids: comment anchors, `diagram-id`s, and media come only from fetched content or local files.

## Specialized Formats

Whiteboards and standalone databases (`--content-type database`) use their own formats, not Markdown. Load the helper before writing, and pass `--ack-body-formats` only after reading its output:

```bash
<atl> confluence content body-formats --content-type whiteboard
<atl> confluence content body-formats --content-type database
```

Each helper returns an index and follow-up `--reference` paths for that content type. Use the whiteboard helper only for whiteboards (SVG) and the database helper only for databases (CSV), then follow the referenced format contract exactly.

Keep title and body separate. Prefer body files over shell-inline multiline content. Verify returned content after consequential writes.
