---
description: Confluence semantics, read formats, safe authoring, editing, archive, trash, and purge rules, and handoffs.
---

# Confluence Rules

Pass supported references and known scope/bounds in the first native call. Use `--reference-space` for exact titles; avoid separate resolve. Required write/auth guidance applies.

## Confluence Semantics

- Search snippets are discovery candidates. Read the selected page as Markdown before summarizing, quoting, or editing it: `<atl> confluence content get <page> --output-file page.md` (the **Fetch page** tactic); search hits count as known pages. Use the raw-twg fallback `<atl> confluence content get <page> --native --detail full --format md` only if that fails, and warn that it is lossy (diagrams, media, attachments, comments may be missing).
- Use CQL for metadata lists. Read one page per Markdown body read. Batch up to 25 known pages only for summaries or metadata: `<atl> confluence content get <id-or-url...> --detail summary -o json`.
- Singles return `data.body`; batches return ordered `data.items` with `input`, `ok`, and `data` or `error`. Check failures and conversion warnings. Read each `body.outputFile` when present, otherwise `body.value`; omitted text is in `output_files.stdout`.
- Search with surrounding lines for focused questions; read full bodies for whole-page summaries. Reuse saved content. `--include-metadata` adds provenance. `--body-only` and version reads are single-page.
- Read and write bodies as Markdown through `<atl>`; it keeps status lozenges, panels, expands, TOC, table layout, and comment anchors in the Markdown dialect (Confluence body formats). Never request `--format html`. Keep headings and table cells together. Never infer missing status from prose.
- `docs get` searches a user's document activity window, not page bodies; it may miss accessible pages.
- Page titles are supplied separately from bodies. Do not repeat the title as the first body heading.
- Apply Remix/Maui ownership and embedding rules from Confluence content; an asset ID/URL is not proof of a page embed.

## Safe Authoring And Editing

- Treat user authorization and CLI confirmation as separate checks for archive, trash, and purge. `--yes` is an execution preflight, not evidence the user authorized the mutation. Use `--yes` only after the user named the mutation and the exact target or a previously displayed bounded target set.
- Explicit instructions such as "archive page XYZ" or "archive those 15 pages" after a concrete list authorize execution without another confirmation. Vague language such as "clean up", "organize", or "take care of" does not authorize archive, trash, or purge.
- If the mutation or targets were inferred, present the exact action and bounded target list and wait for the user to affirm it. Do not generalize approval from a similar prior action; `trash` does not authorize a permanent purge.
- Before authoring, apply the target space's instructions once per space per session (Confluence spaces, *Space Instructions*). Empty instructions mean defaults.
- Prefer `live_doc` for collaborative internal content where supported. Bare "page" or "doc" creation also defaults to live docs.
- Use `page` for explicit classic/non-live intent, knowledge bases, customer help, established classic-page spaces, or page-only operations. Preserve an existing target's type; a classic parent does not set a child's type.
- For non-trivial edits, fetch Markdown to a local file, edit the file, then update from it (Confluence editing).
- Content with no Markdown form (mentions, app macros) → report it and ask before rewriting; never switch to HTML.
- Use `--dry-run` only for explicit preview requests or unusually risky edits where direct execution was not requested.
- Read back the content or space after mutation and report its URL.
