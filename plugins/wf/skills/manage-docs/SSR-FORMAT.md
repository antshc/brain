# SSR Format

Solution Strategy Records (SSRs) capture the **backbone** of the architecture: the
solution-strategy decisions about the top-level decomposition of the system — the use of
an architectural or design pattern that every feature is expected to follow. An SSR is a
*main architecture rule*, not a one-off.

SSRs live in `docs/ssr/` and use sequential numbering: `0001-slug.md`, `0002-slug.md`,
etc. Create the `docs/ssr/` directory lazily — only when the first SSR is needed.

Every SSR is **indexed in `ARCHITECTURE.md`** under a `## Solution Strategy` section with a
one-line summary and a link. The index is the entry point: read it during a modeling or grilling session, and open the full SSR only when a decision is relevant to the work at hand.

## Template

```md
# {The rule / pattern name}

**Summary:** {1-3 sentences. This same line is copied verbatim into the
ARCHITECTURE.md Solution Strategy index.}

```

## Optional sections

Only include these when they add genuine value. Most SSRs won't need them.

- **Context** — the forces and the problem; why the architecture needs a backbone rule here
- **Decision** — the rule itself: the pattern, the layers/steps, the file map, the checklist, the invariants; cite a canonical reference implementation in the codebase
- **Status** frontmatter (`proposed | accepted | deprecated | superseded by SSR-NNNN`)
- **Rationale / Trade-offs** — why this pattern over the alternatives
- **Consequences** — non-obvious downstream effects of adopting the pattern

## Numbering

Scan `docs/ssr/` for the highest existing number and increment by one.

## Writing style

1. Prioritize directness and facts: keep only sentences that add actionable value; cut any that just take up space.
2. Remove bloat: filler words, redundant explanations, verbose phrasing. If the text already has no removable bloat, leave it unchanged.

## When to offer an SSR

See *"When to write an SSR"* in [SKILL.md](./SKILL.md) for the criteria
(structural, reusable, backbone-defining) and how an SSR differs from an ADR.

## Keeping the index in sync

When you add, supersede, or retire an SSR, update the `## Solution Strategy` table in
`ARCHITECTURE.md` in the same change. The index summary must match the SSR's `**Summary:**`
line.
