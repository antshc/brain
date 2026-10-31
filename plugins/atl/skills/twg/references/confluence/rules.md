---
description: Confluence semantics, read formats, safe authoring, editing, archive, trash, and purge rules, and handoffs.
---

# Confluence Rules

Pass supported references and known scope/bounds in the first native call. Use `--reference-space` for exact titles; avoid separate resolve. Required write/auth guidance applies.

## Confluence Semantics

- Search snippets are discovery candidates. Read the selected content before summarizing or editing it.
- Use CQL for metadata lists. Batch up to 25 known pages.
  - Prose-only reads: `confluence content get <id-or-url...> --detail full --format md -o json`.
  - Rich, mixed, unknown, or pre-edit content: `confluence content get <id-or-url...> --detail full --format html -o json`. Pre-edit reads follow the Confluence editing draft and snapshot-token rules.
- Singles return `data.body`; batches return ordered `data.items` with `input`, `ok`, and `data` or `error`. Check failures and conversion warnings. Read each `body.outputFile` when present, otherwise `body.value`; omitted text is in `output_files.stdout`.
- Search with surrounding lines for focused questions; read full bodies for whole-page summaries. Reuse saved content. `--include-metadata` adds provenance. `--body-only` and version reads are single-page.
- Read prose with `--format md`. Use HTML for editing or required status markers, macros, and table details. If `data.body.lossyConversion` is true and relevant details are missing, fetch `--format html` once. Keep headings and table cells together. Never infer missing status from prose.
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
- For non-trivial edits, read current content, save the body locally, edit the file, then update with the snapshot token.
- Use the lossless HTML round trip when macros or exact storage matter.
- Use `--dry-run` only for explicit preview requests or unusually risky edits where direct execution was not requested.
- Read back the content or space after mutation and report its URL.
