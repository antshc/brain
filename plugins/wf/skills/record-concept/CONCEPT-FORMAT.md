# Concept Format

A Crosscutting Concept records the **backbone** of the architecture: the top-level decomposition, or an architectural/design pattern every feature of a given kind is expected to follow. A main architecture rule, not a one-off.

Files live in `docs/concepts/` as `{{nnnn}}-{{slug}}.md`.

## Template

```md
---
id: "{{nnnn}}"
title: {{conceptTitle}}
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

# {{conceptTitle}}

## Purpose
<!-- 1-3 sentences.-->
Describe the recurring architectural problem this concept solves.

## Rules
<!-- atomic, normative, one obligation per line -->
- MUST / MUST NOT / SHOULD statements, each independently checkable against a diff.

## Design Guidance
<!-- be terse, concise, factual -->

Design Guidance explains how to apply the concept’s rules in normal design and implementation work. It gives practical direction and judgment criteria without becoming a low-level coding standard.
May include:diagrams and schemas; reference flows or sequences; recommended patterns and structures; etc..

```

## Frontmatter

YAML frontmatter is **mandatory** and is the machine-readable contract for the record. It makes the file self-sufficient on retrieval — a reader landing on it via search must be able to decide relevance without opening `ARCHITECTURE.md`.

| Key | Required | Value |
|-----|----------|-------|
| `id` | yes | Quoted four-digit record number, matching the filename prefix. |
| `title` | yes | Same text as the `# ` heading and the index row's record cell. |
| `status` | yes | `Accepted`, `Superseded by NNNN`, or `Retired`. Never repeat it as prose in the body. |
| `trigger` | yes | Comma-separated clauses naming the change types that make this Concept apply. Source of truth for the index's Trigger condition cell. |
| `summary` | yes | The index row's Summary cell, verbatim. |
| `default` | yes | One sentence naming the choice to take when the design doesn't state one. Written so a reader can act on it without opening the body — `index-docs` prepends it to the index row's Summary cell, and it is what lets a decision be settled without asking. State the choice, never the reference implementation that happens to embody it. |
| `owns` | no | Decision-area phrases this record has **sole** authority over. Add one only where another record could plausibly claim the same area; a phrase may appear in exactly one record. |
| `applies_to` | yes | Repo-relative path globs the Concept governs; `- "**"` when genuinely universal. **Widens matching only** — a change outside these globs is still governed whenever a `trigger` clause fires. Never treat a glob miss as "this Concept doesn't apply". |
| `related` | no | Quoted ids of Concepts/ADRs a reader must also load. Keep **bidirectional** — add the reciprocal entry to each linked record in the same change. |

Use folded block scalars (`>-`) for `trigger`, `summary`, and `default`: all three routinely contain `:`, backticks, and `→`, which break plain YAML scalars.

## Section skeleton

Fixed heading set, always `##`, always in this order. Omit an optional section entirely rather than renaming or re-nesting it — stable headings are what make section-level extraction possible.

| Section | Required | Content |
|---------|----------|---------|
| `Purpose` | yes | 1–3 sentences on the recurring problem. No rules here. |
| `Rules` | yes | Atomic normative lines (MUST / MUST NOT / SHOULD), one obligation each. |
| `Design Guidance` | yes | How to apply the rules: tables, diagrams, reference flows, resolvable code anchors. |
| `Violation signals` | no | 2–4 observable, greppable patterns that indicate a breach. |
| `Exceptions` | no | Permitted deviations and their conditions. |
| `Examples` | no | One or two concise examples of correct application. |
| `Consequences` | no | Trade-offs accepted. Never nest this under `Design Guidance`. |

## Writing rules

- **One obligation per `Rules` line.** Never bundle a naming rule, a placement rule, and a visibility rule into one bullet — each must be citable and checkable on its own.
- **Normative verbs.** MUST / MUST NOT / SHOULD, consistently. Avoid "prefer", "try to", bare present tense for obligations.
- **Resolvable anchors only.** Every "where" reference is a path glob or a symbol name a language server can resolve — never a vague label like "the repository layer". Mark deliberately non-canonical pointers "verify — may drift".
- **References corroborate, never instruct.** A `Reference:` or "follow its shape" pointer may appear in `Design Guidance` or `Examples` as evidence for a rule; it must never be the only statement of that rule. A reader who can't see the referenced code must still be able to act.
- **No embedded volatile lists.** Enumerations that grow with the codebase (collection names, module lists, test-project maps) belong in code or a runbook, linked from here.
- **Stable rule, not a runbook.** Commands, environment variables, and step-by-step invocations are operational content; a Concept states the rule they implement.
- **Escape wildcards.** Write `` `*Manager` ``, not `*Manager` — unescaped asterisks form Markdown emphasis spans and silently drop the wildcard.
