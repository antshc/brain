---
name: doc-decision
description: Render established architectural decisions in full ADR or compact bullet form. Use for decision lists, design appendices, and when draft-decision needs an ADR body. Owns formatting, not ADR placement or indexing.
---

# Document Decision

Render architectural decisions from established context.

## Formats

Prefer the **full** format when the ADR is one per single file. When multiple ADRs writes to the file then **compact** format.

- **Full** — use when the caller requests **full** format, requests a standalone ADR.
- **Compact** — use when the caller requests **compact** format, a compact decision, a decision list, or an appendix entry.



**Done when:** exactly one format is selected.

## 2. Render

Open the selected template before drafting:

- **Full** — [FULL-DECISION-TEMPLATE.md](./FULL-DECISION-TEMPLATE.md)
- **Compact** — [COMPACT-DECISION-TEMPLATE.md](./COMPACT-DECISION-TEMPLATE.md)

Apply that template and its rules to every decision in scope. Use only decision facts established by the caller or grounded in the source material.

**Done when:** every decision in scope matches the selected template and every rule under that format has been applied.
