# ADR Format

An ADR records a **localized, point-in-time decision** — the choice made for one context or feature that a future reader would not find obvious. Not a backbone rule (that's a Concept).

Files live in `docs/adr/` as `{{nnnn}}-{{slug}}.md`.

## Template

```md
---
id: "{{nnnn}}"
title: {{decisionTitle}}
status: Accepted
trigger: >-
  {{comma-separated trigger clauses}}
summary: >-
  {{one-paragraph summary}}
default: >-
  {{the choice to take when the design doesn't state one}}
owns: ["{{decision area}}"]
applies_to:
  - {{path glob}}
related: ["{{nnnn}}"]
---

# {{decisionTitle}}

<!-- 1-3 sentences: what's the context, what did we decide, and why. -->
```

The **body** can be a single paragraph. The value is recording *that* a decision was made and *why* — not filling out sections. The frontmatter is not optional, though: it is the machine-readable contract that makes the record self-sufficient on retrieval and is the source of truth for the ADR index row.

## Frontmatter

| Key | Required | Value |
|-----|----------|-------|
| `id` | yes | Quoted four-digit record number, matching the filename prefix. |
| `title` | yes | Same text as the `# ` heading and the index row's Decision cell. |
| `status` | yes | `Proposed`, `Accepted`, `Superseded by NNNN`, or `Retired`. Never repeat it as prose in the body. |
| `trigger` | yes | Comma-separated clauses naming the change types that make this decision apply. Source of truth for the index's Trigger condition cell. |
| `summary` | yes | The index row's Summary cell, verbatim. |
| `default` | yes | One sentence naming the choice to take when the design doesn't state one. `index-docs` prepends it to the index row's Summary cell; it is what lets the decision be reapplied without asking. State the choice, never the reference implementation that embodies it. |
| `owns` | no | Decision-area phrases this record has **sole** authority over. Add one only where another record could plausibly claim the same area; a phrase may appear in exactly one record. |
| `applies_to` | no | Repo-relative path globs the decision governs. **Widens matching only** — a glob miss never overrides a `trigger` clause hit. |
| `related` | no | Quoted ids of Concepts/ADRs a reader must also load. Keep **bidirectional**. |

Use folded block scalars (`>-`) for `trigger`, `summary`, and `default` — all three routinely contain `:`, backticks, and `→`.

## Optional sections

Only when they add genuine value. Most ADRs won't need them.

- **Considered Options** — only when the rejected alternatives are worth remembering
- **Consequences** — only when non-obvious downstream effects need to be called out
