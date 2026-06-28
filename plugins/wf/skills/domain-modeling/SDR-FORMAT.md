# SDR Format

Solution Design Records (SDRs) capture the **backbone** of the architecture: the
solution-strategy decisions about the top-level decomposition of the system — the use of
an architectural or design pattern that every feature is expected to follow. An SDR is a
*main architecture rule*, not a one-off.

SDRs live in `docs/sdr/` and use sequential numbering: `0001-slug.md`, `0002-slug.md`,
etc. Create the `docs/sdr/` directory lazily — only when the first SDR is needed.

Every SDR is **indexed in `ARCHITECTURE.md`** under a `## Solution Design Strategy` section with a
one-line summary and a link. The index is the entry point: read it during a modeling
session, and open the full SDR only when a decision is relevant to the work at hand.

## Template

```md
# {The rule / pattern name}

**Summary:** {1-3 sentences. This same line is copied verbatim into the
ARCHITECTURE.md Solution Design Strategy index.}

## Context
{The forces and the problem. Why does the architecture need a backbone rule here?}

## Decision
{The rule itself — the pattern, the layers/steps, the file map, the checklist, the
invariants. This is the part the agent loads and follows when building a feature of
this kind. Cite a canonical reference implementation in the codebase.}
```

## Optional sections

Only include these when they add genuine value. Most ADRs won't need them.

- **Context** — the forces and the problem; why the architecture needs a backbone rule here
- **Decision** — the rule itself: the pattern, the layers/steps, the file map, the checklist, the invariants; cite a canonical reference implementation in the codebase
- **Status** frontmatter (`proposed | accepted | deprecated | superseded by SDR-NNNN`)
- **Rationale / Trade-offs** — why this pattern over the alternatives
- **Consequences** — non-obvious downstream effects of adopting the pattern

## Numbering

Scan `docs/sdr/` for the highest existing number and increment by one.

## Writing style

1. Prioritize directness and facts: keep only sentences that add actionable value; cut any that just take up space.
2. Remove bloat: filler words, redundant explanations, verbose phrasing. If the text already has no removable bloat, leave it unchanged.

## When to offer an SDR

See *"Offer Solution Design Records (SDRs)"* in [SKILL.md](./SKILL.md) for the criteria
(structural, reusable, backbone-defining) and how an SDR differs from an ADR.

## Keeping the index in sync

When you add, supersede, or retire an SDR, update the `## Solution Design Strategy` table in
`ARCHITECTURE.md` in the same change. The index summary must match the SDR's `**Summary:**`
line.
