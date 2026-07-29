---
name: bootstrap-docs
description: Own the existence-and-creation mechanics for ARCHITECTURE.md and CONTEXT.md — mandatorily create either the moment it's missing. Owns no templates, no prose, no section insertion (that's index-docs), no directory creation for docs/adr, docs/concepts, or docs/services (each owned by the skill that writes into it), and no "when is it appropriate to create" criteria — that stays with the owning skill. Invoked only when a caller's own existence check finds ARCHITECTURE.md or CONTEXT.md missing.
---

# Bootstrap Docs

Own the *mechanics* of `ARCHITECTURE.md`/`CONTEXT.md` existence and creation. Section-skeleton
insertion belongs to `index-docs` (*Ensure section exists*). Directory creation for `docs/adr/`,
`docs/concepts/`, `docs/services/` belongs to the skill that writes into that directory
(`record-adr`, `record-concept`, `record-service`). Every template, every piece of prose, and every
"is now the right time?" judgment belongs to the skill that owns that content — `record-term`
(`CONTEXT-FORMAT.md`), `index-docs` (`ARCHITECTURE-FORMAT.md`).

## Mandatory creation

If `ARCHITECTURE.md` and/or `CONTEXT.md` don't exist, create them **immediately** — don't wait for
a term, structural rule, ADR, Concept, or service to be ready to capture.

- **`ARCHITECTURE.md`** is the index hub every other document links into. Fill in only the
  required sections (`{{systemName}} Overview`, `Context`) from what's already known about the
  codebase, using [ARCHITECTURE-FORMAT.md](../index-docs/ARCHITECTURE-FORMAT.md) (`index-docs`'
  template). Leave the optional sections (`Building blocks`, `Deployment View`, the
  `Architecture Decision Records` / `Crosscutting Concepts` indexes) out until there's content for
  them — `index-docs` adds those via *Ensure section exists*.
- **`CONTEXT.md`** is the glossary every other document assumes as shared vocabulary. Create it
  with its `{{contextName}}` heading and an empty `Language` section — leave individual terms out
  until `record-term` captures the first one, using
  [CONTEXT-FORMAT.md](../record-term/CONTEXT-FORMAT.md) (`record-term`'s template).

These are the **two non-lazy cases**. Every other document (`docs/adr/`, `docs/concepts/`,
`docs/services/`) stays genuinely lazy — and each is created directly by the skill that writes
into it, not by `bootstrap-docs`.

