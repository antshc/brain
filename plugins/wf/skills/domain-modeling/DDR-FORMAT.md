# DDR Format

Design Decision Records (DDRs) capture the **backbone** of the architecture: the
solution-strategy decisions about the top-level decomposition of the system — the use of
an architectural or design pattern that every feature is expected to follow. A DDR is a
*main architecture rule*, not a one-off.

DDRs live in `docs/design/` and use sequential numbering: `0001-slug.md`, `0002-slug.md`,
etc. Create the `docs/design/` directory lazily — only when the first DDR is needed.

Every DDR is **indexed in `ARCHITECTURE.md`** under a `## Design Decisions` section with a
one-line summary and a link. The index is the entry point: read it during a modeling
session, and open the full DDR only when a decision is relevant to the work at hand.

## Template

```md
# {The rule / pattern name}

**Summary:** {1-2 sentences. This same line is copied verbatim into the
ARCHITECTURE.md Design Decisions index.}

## Context
{The forces and the problem. Why does the architecture need a backbone rule here?}

## Decision
{The rule itself — the pattern, the layers/steps, the file map, the checklist, the
invariants. This is the part the agent loads and follows when building a feature of
this kind. Cite a canonical reference implementation in the codebase.}
```

## Optional sections

Include only when they add genuine value:

- **Status** frontmatter (`proposed | accepted | deprecated | superseded by DDR-NNNN`)
- **Rationale / Trade-offs** — why this pattern over the alternatives
- **Consequences** — non-obvious downstream effects of adopting the pattern

## Numbering

Scan `docs/design/` for the highest existing number and increment by one.

## When to offer a DDR

See *"Offer Design Decision Records (DDRs)"* in [SKILL.md](./SKILL.md) for the criteria
(structural, reusable, backbone-defining) and how a DDR differs from an ADR.

## Keeping the index in sync

When you add, supersede, or retire a DDR, update the `## Design Decisions` table in
`ARCHITECTURE.md` in the same change. The index summary must match the DDR's `**Summary:**`
line.
