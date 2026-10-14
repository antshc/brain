# ARCHITECTURE.md Bootstrap Format

Create only the required sections below. Omit optional Building blocks, Deployment View, Architecture Decision Records, and Crosscutting Concepts sections until `index-docs` inserts them for established content.

```md
# {{systemName}} Overview

{{systemSummary}}

## Context

See [CONTEXT.md](CONTEXT.md) for the shared language.
```

- `{{systemSummary}}`: 1-3 sentences on the system, architectural style, and core technology stack, using only known facts.
- Link `docs/building-blocks/system-context.md` from `Context` only when the diagram document exists; do not create it during bootstrap.
- Keep structural detail and rules in their owning records; do not invent index rows or initialize lazy record directories.
