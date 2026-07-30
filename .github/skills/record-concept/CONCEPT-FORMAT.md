# Concept Format

A Crosscutting Concept records the **backbone** of the architecture: the top-level decomposition, or an architectural/design pattern every feature of a given kind is expected to follow. A main architecture rule, not a one-off.

Files live in `docs/concepts/` as `{{nnnn}}-{{slug}}.md`.

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
