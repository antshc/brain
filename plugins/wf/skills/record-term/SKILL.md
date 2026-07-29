---
name: record-term
description: Capture one resolved domain term into CONTEXT.md, the project's glossary, the moment it crystallises. Owns the term-writing rules and glossary-only guardrail inside bootstrap-docs' CONTEXT-FORMAT.md; CONTEXT.md's existence and the template's top-level skeleton are guaranteed by bootstrap-docs, not by this skill. Called by grill-design as terms resolve during an interview.
---

# Record Term

Capture **one resolved term** into `CONTEXT.md` the moment it crystallises — never batch these up.
Use [CONTEXT-FORMAT.md](../bootstrap-docs/CONTEXT-FORMAT.md) for structure and rules.

## Existence

`bootstrap-docs` mandatorily creates `CONTEXT.md` at session start if it doesn't exist yet —
`record-term` doesn't need to check or create the file itself; it only writes into it.

## Inline-update discipline

When a term is resolved, update `CONTEXT.md` right there, in the same turn — never batch updates.

## Keep it in its lane

`CONTEXT.md` is a **glossary only** — totally devoid of implementation details. Not a spec, not a
scratch pad, not a repository for implementation decisions.

## Ownership

- Owns: the term-writing rules and format inside `CONTEXT-FORMAT.md`, inline-update timing, and
  the glossary-only guardrail.
- Does **not** own: `CONTEXT-FORMAT.md`'s file location or top-level skeleton, or file
  existence-and-creation mechanics (`bootstrap-docs`' job — see *Existence* above), or any other
  document's content.
