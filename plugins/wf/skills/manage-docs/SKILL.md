---
name: manage-docs
description: Create and update the project's domain-model documentation — the glossary (CONTEXT.md), the Crosscutting Concept (Concept), the ADR, the architecture map (ARCHITECTURE.md), and the decision records (Crosscutting Concepts in docs/concepts/ and ADRs in docs/adr/). Owns the doc templates and the rules for where each file lives, when to create it, and how to keep the indexes in sync. Use when creating a new Crosscutting Concept or ADR, not just when updating an existing one. Called by the grill-* skills to set up and update docs as decisions crystallise.
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

## Lazy creation

Read this once when setting up the domain-model files for a repo that doesn't have them yet, or
when deciding where a new file belongs.

Repo structure:

```
/
├── ARCHITECTURE.md                      ← also indexes the Crosscutting Concepts
├── CONTEXT.md
├── docs/
│   ├── concepts/                        ← Crosscutting Concepts (backbone rules)
│   │   └── 0001-persisted-domain-model-repository.md
│   └── adr/
│       ├── 0001-event-sourced-orders.md
│       └── 0002-postgres-for-write-model.md
└── src/
```

**Create files lazily — only when you have something to write.** This rule applies for the whole
session, every time a term, structural rule, Concept, or ADR is about to be captured — never skip
it just because the file didn't exist at session start.

- No `CONTEXT.md` → create one when the first term is resolved.
- No `ARCHITECTURE.md` → **don't wait.** Offer to create it the moment its absence is noticed, regardless of whether a structural rule, Concept, or ADR is ready yet. Fill in its required sections (`# {{systemName}} Overview`, `## Context`) from what's already known about the codebase; leave the optional sections (`Deployment View`, the ADR/Concepts indexes) out until there's content for them.
- No `docs/concepts/` → create it when the first Concept is needed, then add it to the `Crosscutting Concepts` index in `ARCHITECTURE.md`.
- No `docs/adr/` → create it when the first ADR is needed, then add it to the `Architecture Decision Records` index in `ARCHITECTURE.md`.

## Inline-update discipline

Capture each decision in the right document **the moment it crystallises** — never batch updates.

###  CONTEXT.md

When a term is resolved, update `CONTEXT.md` right there.

### ARCHITECTURE.md

When the structure or layering changes, update `ARCHITECTURE.md` right there. Whenever a Concept or ADR is added, superseded, or retired, call `/trigger-indexer` **Keeping the indexes in sync** in the same change to keep its index row current — not just when writing a brand-new record. Pass `{{indexFile}}`=`ARCHITECTURE.md`, `{{indexSection}}`=`Crosscutting Concepts` or `Architecture Decision Records`, and `{{recordDirectory}}`=`docs/concepts/` or `docs/adr/` explicitly in context — `/trigger-indexer` never assumes these.

## Keep each document in its lane

- `CONTEXT.md` is a **glossary only** — totally devoid of implementation details. Not a spec, not a scratch pad, not a repository for implementation decisions.
- `ARCHITECTURE.md` describes **shape and rules**, not implementation detail. Not a spec, not a scratch pad, not a place to inline backbone decisions — the step-by-step detail lives in the code and in the linked Concepts.

## Repo topology (documentation repository)

When the docs live in a dedicated documentation/context repository (separate from the codebase), use the `copilot-instructions.md` to define where `CONTEXT.md`, `ARCHITECTURE.md`, `docs/adr/`, and `docs/concepts/` live at the reporoot and where the source code and worktrees live.
