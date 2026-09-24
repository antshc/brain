# Concept Record Format

`/record-concept` owns frontmatter, record identity, file writing, and the `ARCHITECTURE.md` index. `/doc-concept` owns all body templates and writing rules.

Files live in `docs/concepts/` as `{{kind}}-{{slug}}.md`, where `{{kind}}` is `domain`, `structure`, or `ops` — the kind of the `/doc-concept` template the body was written from, so a listing sorts the records into their families.

## Frontmatter template

```md
---
id: {{kind}}-{{slug}}
title: {{conceptTitle}}
trigger: >-
  {{comma-separated trigger clauses}}
summary: >-
  {{one-paragraph summary}}
default: >-
  {{the choice to take when the design doesn't state one}}
owns: ["{{decision area}}"]
applies_to:
  - {{path glob}}
related: ["{{kind}}-{{slug}}"]
---

# {{conceptTitle}}
```

## Frontmatter


YAML frontmatter is **mandatory** and is the machine-readable contract for the record. It makes the file self-sufficient on retrieval — a reader landing on it via search must be able to decide relevance without opening `ARCHITECTURE.md`.

| Key | Required | Value |
|-----|----------|-------|
| `id` | yes | The filename stem, `{{kind}}-{{slug}}`, matching the file it opens. |
| `title` | yes | Same text as the `# ` heading and the index row's record cell. |
| `trigger` | yes | Comma-separated clauses naming the change types that make this Concept apply. Source of truth for the index's Trigger condition cell. |
| `summary` | yes | The index row's Summary cell, verbatim. |
| `default` | yes | One sentence naming the choice to take when the design doesn't state one. Written so a reader can act on it without opening the body — `index-docs` prepends it to the index row's Summary cell, and it is what lets a decision be settled without asking. State the choice, never the reference implementation that happens to embody it. |
| `owns` | no | Decision-area phrases this record has **sole** authority over. Add one only where another record could plausibly claim the same area; a phrase may appear in exactly one record. |
| `applies_to` | yes | Repo-relative path globs the Concept governs; `- "**"` when genuinely universal. **Widens matching only** — a change outside these globs is still governed whenever a `trigger` clause fires. Never treat a glob miss as "this Concept doesn't apply". |
| `related` | no | Quoted ids of Concepts/ADRs a reader must also load. Keep **bidirectional** — add the reciprocal entry to each linked record in the same change. |

Use folded block scalars (`>-`) for `trigger`, `summary`, and `default`: all three routinely contain `:`, backticks, and `→`, which break plain YAML scalars.
