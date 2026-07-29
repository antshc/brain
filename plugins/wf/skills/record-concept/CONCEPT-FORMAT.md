# Concept Format

Crosscutting Concepts capture the **backbone** of the architecture: the solution concepts about the top-level decomposition of the system — the use of
an architectural or design pattern that every feature is expected to follow. A Concept is a
*main architecture rule*, not a one-off.

Concepts live in `docs/concepts/` and use sequential numbering: `0001-slug.md`, `0002-slug.md`,
etc. Create the `docs/concepts/` directory lazily — only when the first Concept is needed; this is
`record-concept`'s own mechanic (see [SKILL.md](./SKILL.md)'s **Lazy creation**).

Every Concept is **indexed in `ARCHITECTURE.md`** under a `Crosscutting Concepts` section with a summary and a link. The index is the entry point: read it during a modeling or grilling session, and open the full Concept only when a concept is relevant to the work at hand.

## Template

```md
# {{conceptTitle}}


## Purpose
<!-- 1-3 sentences.-->
Describe the recurring architectural problem this concept solves.

## Design Guidance
<!-- be terse, concise, factual -->

Design Guidance explains how to apply the concept’s rules in normal design and implementation work. It gives practical direction and judgment criteria without becoming a low-level coding standard.
May include:diagrams and schemas; reference flows or sequences; recommended patterns and structures; etc..

```
## Optional sections

Only include these when they add genuine value.

- **Exceptions** - Document permitted deviations and their conditions.
- **Examples** - Provide one or two concise examples of correct application.

## Next record number

<!-- Deliberately duplicated in record-adr and record-concept: each skill must be self-contained. Do not factor out. -->

Scan `docs/concepts/` for filenames starting with a four-digit `NNNN` prefix, take the highest, and
return `NNNN + 1`, zero-padded to four digits. An empty or absent directory returns `0001`.

## When to offer a Concept

See *"When to write a Concept"* in [SKILL.md](./SKILL.md) for the criteria
(structural, reusable, backbone-defining) and how a Concept differs from an ADR.

## Keeping the index in sync

When you add, supersede, or retire a Concept, run `/index-docs`' **Sync index row** in the same change to update the `Crosscutting Concepts` table in `ARCHITECTURE.md`.
