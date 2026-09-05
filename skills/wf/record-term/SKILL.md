---
name: record-term
description: Capture one resolved domain term into CONTEXT.md, the project's glossary, the moment it crystallises. Owns the term-writing rules and glossary-only guardrail, and hosts CONTEXT-FORMAT.md; CONTEXT.md's existence is guaranteed by bootstrap-docs, not by this skill. Called by grill-design as terms resolve during an interview.
---

# Record Term

Capture **one resolved term** into `CONTEXT.md` in the same turn it crystallises — never batch. Structure and rules: [CONTEXT-FORMAT.md](./CONTEXT-FORMAT.md). The file's existence is guaranteed by `bootstrap-docs`; this skill only writes into it.

## Keep it in its lane

`CONTEXT.md` is a **glossary only** — totally devoid of implementation details. Not a spec, not a scratch pad, not a repository for implementation decisions.

