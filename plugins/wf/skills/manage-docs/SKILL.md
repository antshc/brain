---
name: manage-docs
description: Create and update the project's domain-model documentation — the glossary (CONTEXT.md), the architecture map (ARCHITECTURE.md), and the decision records (Concepts and ADRs). Owns the doc templates and the rules for where each file lives, when to create it, and how to keep the indexes in sync. Called by the grill-* skills to set up and update docs as decisions crystallise.
disable-model-invocation: true
---

# Manage Docs

Create and update the domain-model documents. This skill owns the templates and the rules for
*where each file lives*, *when to create it*, and *how to keep it consistent*. The grill-* skills
run the interview and delegate every doc read, create, and update here.

The documents:

- `CONTEXT.md` — the glossary (the *language*). Use [CONTEXT-FORMAT.md](./CONTEXT-FORMAT.md).
- `ARCHITECTURE.md` — the structural map, and the index of Concepts and ADRs. Use [ARCHITECTURE-FORMAT.md](./ARCHITECTURE-FORMAT.md).
- `docs/concepts/` — Crosscutting Concepts: the backbone rules. Use [CONCEPT-FORMAT.md](./CONCEPT-FORMAT.md).
- `docs/adr/` — Architecture Decision Records: localized decisions. Use [ADR-FORMAT.md](./ADR-FORMAT.md).

## Where the files live

Read [FILE-STRUCTURE.md](./FILE-STRUCTURE.md) once when setting up the domain-model files for a repo that doesn't have them yet, or when deciding where a new file belongs. It covers the repo layout and the lazy-creation rules.

## When to create them

**Create files lazily — only when you have something to write.**

- No `CONTEXT.md` → create one when the first term is resolved.
- No `ARCHITECTURE.md` → create one when the first structural rule is captured.
- No `docs/concepts/` → create it when the first Concept is needed, then add it to the `Crosscutting Concepts` index in `ARCHITECTURE.md`.
- No `docs/adr/` → create it when the first ADR is needed, then add it to the `Architecture Decision Records` index in `ARCHITECTURE.md`.

## Inline-update discipline

Capture each decision in the right document **the moment it crystallises** — never batch updates.

###  CONTEXT.md

When a term is resolved, update `CONTEXT.md` right there.

### ARCHITECTURE.md

When the structure or layering changes, update `ARCHITECTURE.md` right there. When a decision
qualifies as a Concept or ADR, write the record and update the matching index in the same change.

## Keep each document in its lane

- `CONTEXT.md` is a **glossary only** — totally devoid of implementation details. Not a spec, not a scratch pad, not a repository for implementation decisions.
- `ARCHITECTURE.md` describes **shape and rules**, not implementation detail. Not a spec, not a scratch pad, not a place to inline backbone decisions — the step-by-step detail lives in the code and in the linked Concepts.

## Keeping the indexes in sync

`ARCHITECTURE.md` is the entry point a reader (or agent) scans before designing. Every record in
`docs/concepts/` and `docs/adr/` must appear in its index table with a matching summary; nothing is
added, superseded, or retired without updating the table in the same change. Link, don't inline —
keep the full record content out of `ARCHITECTURE.md` so the map stays scannable.

## Repo topology (documentation repository)

When the docs live in a dedicated documentation/context repository (separate from the codebase), seed its `copilot-instructions.md` from [instructions.template](./instructions.template). It defines where `CONTEXT.md`, `ARCHITECTURE.md`, `docs/adr/`, and `docs/concepts/` live at the reporoot and where the source code and worktrees live.
