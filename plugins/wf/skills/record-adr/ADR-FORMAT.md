# ADR Format

An ADR records a **localized, point-in-time decision** — the choice made for one context or feature that a future reader would not find obvious. Not a backbone rule (that's a Concept).

Files live in `docs/adr/` as `{{nnnn}}-{{slug}}.md`.

## Template

```md
# {{decisionTitle}}

<!-- 1-3 sentences: what's the context, what did we decide, and why. -->
```

An ADR can be a single paragraph. The value is recording *that* a decision was made and *why* — not filling out sections.

## Optional sections

Only when they add genuine value. Most ADRs won't need them.

- **Considered Options** — only when the rejected alternatives are worth remembering
- **Consequences** — only when non-obvious downstream effects need to be called out
