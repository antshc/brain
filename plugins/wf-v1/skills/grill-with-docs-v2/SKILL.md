---
name: grill-with-docs-v2
description: Grilling session that challenges your plan against the existing domain model, sharpens terminology, and updates documentation (CONTEXT.md, ADRs) inline as decisions crystallise. Assumes a fixed topology — the current repo (reporoot) holds the context/docs and a nested `workspace/` holds the source code and worktrees where development happens. Use when user wants to stress-test a plan against their project's language and documented decisions.
---

<repo-topology>

This skill assumes a fixed repository layout:

- **reporoot** (the current repository) is the **documentation/context repo**. It holds `CONTEXT.md` (and optional `CONTEXT-MAP.md`) at the root and ADRs under `docs/adr/`.
- **`reporoot/workspace/`** holds the **project source code and git worktrees**. All development and code changes happen here, inside the active worktree — never in reporoot.
- Documentation (`CONTEXT.md`, ADRs) is authored and updated at **reporoot**, never inside `workspace/`.

So:

- `<docs-path>` = `.` (reporoot) — where CONTEXT.md and `docs/adr/` live.
- `<code-path>` = `workspace/` — where source and worktrees live and where development must happen.

</repo-topology>

<what-to-do>

Interview me relentlessly about every aspect of this plan until we reach a shared understanding. Walk down each branch of the design tree, resolving dependencies between decisions one-by-one. For each question, provide your recommended answer.

Ask the questions one at a time, waiting for feedback on each question before continuing.

If a question can be answered by exploring the codebase, explore the codebase instead. Source code lives under `<code-path>` (`workspace/`).

</what-to-do>

<supporting-info>

## Domain awareness

During codebase exploration, also look for existing documentation in `<docs-path>` (reporoot):

### File structure

Most `<docs-path>` repos have a single context:

```
/                                    ← reporoot (docs/context)
├── CONTEXT.md
├── docs/
│   └── adr/
│       ├── 0001-event-sourced-orders.md
│       └── 0002-postgres-for-write-model.md
└── workspace/                       ← source code + worktrees (development happens here)
```

If a `CONTEXT-MAP.md` exists at the root, `<docs-path>` has multiple contexts. The map points to where each one lives:

```
/                                    ← reporoot (docs/context)
├── CONTEXT-MAP.md
├── docs/
│   └── adr/                          ← system-wide decisions
└── workspace/
    ├── ordering/
    │   ├── CONTEXT.md
    │   └── docs/adr/                 ← context-specific decisions
    └── billing/
        ├── CONTEXT.md
        └── docs/adr/
```

Create files lazily — only when you have something to write. If no `CONTEXT.md` exists, create one when the first term is resolved. If no `docs/adr/` exists, create it when the first ADR is needed. All documentation files are created at reporoot, never inside `workspace/`.

## During the session

### Challenge against the glossary

When the user uses a term that conflicts with the existing language in `CONTEXT.md`, call it out immediately. "Your glossary defines 'cancellation' as X, but you seem to mean Y — which is it?"

### Sharpen fuzzy language

When the user uses vague or overloaded terms, propose a precise canonical term. "You're saying 'account' — do you mean the Customer or the User? Those are different things."

### Discuss concrete scenarios

When domain relationships are being discussed, stress-test them with specific scenarios. Invent scenarios that probe edge cases and force the user to be precise about the boundaries between concepts.

### Cross-reference with code

When the user states how something works, check whether the code agrees. The code lives under `<code-path>` (`workspace/`, including the active worktree) — not at reporoot. If you find a contradiction, surface it: "Your code cancels entire Orders, but you just said partial cancellation is possible — which is right?"

### Update CONTEXT.md inline

When a term is resolved, update `CONTEXT.md` at reporoot right there. Don't batch these up — capture them as they happen. Use the format in [CONTEXT-FORMAT.md](./CONTEXT-FORMAT.md).

`CONTEXT.md` should be totally devoid of implementation details. Do not treat `CONTEXT.md` as a spec, a scratch pad, or a repository for implementation decisions. It is a glossary and nothing else.

### Offer ADRs sparingly

Only offer to create an ADR when all three are true:

1. **Hard to reverse** — the cost of changing your mind later is meaningful
2. **Surprising without context** — a future reader will wonder "why did they do it this way?"
3. **The result of a real trade-off** — there were genuine alternatives and you picked one for specific reasons

If any of the three is missing, skip the ADR. Use the format in [ADR-FORMAT.md](./ADR-FORMAT.md). ADRs live at reporoot under `docs/adr/`.

</supporting-info>
