---
name: ralph-gotchas
description: Shared agent Gotchas guidance. Reads skill-owned GOTCHAS.md before work and distills reusable one-line directives after successful implementation.
---

# Gotchas

Copy this checklist and check off items as you complete them:

```
Gotchas Progress:
- [ ] Step 1: Read sibling GOTCHAS.md in full (or use FALLBACK.md)
- [ ] Step 2: Apply every directive during work
- [ ] Step 3: Identify reusable problem candidates after successful implementation
- [ ] Step 4: Deduplicate and persist directives
```

## Read Workflow

- When sibling `GOTCHAS.md` is present, read it in full. When it is absent, create new.
- Apply every directive found during work. Do not contradict one without reporting the conflict.

**Emit**: "Gotchas loaded: [summary]" or "No Gotchas recorded yet."

## Write Workflow

Identify friction from the invocation that would help a future run avoid a recurring mistake. Discard routine steps, one-off typos, and transient issues fixed on first retry.

For each kept candidate, distill one directive in the form `- <directive>`. Extend a clearly matching existing directive; otherwise append it under `## Gotchas`.

When no candidates exist, write nothing. When sibling `GOTCHAS.md` is absent, do not create it and emit "Gotchas update: reference missing; no directives persisted."

**Emit**: "Gotchas updated: [count added/extended]" or "No Gotchas to record."

## Hard Constraints

- Write only sibling `GOTCHAS.md` when it is present.
- Never fabricate a directive that is not grounded in this invocation.
- Never delete or contradict unrelated guidance.