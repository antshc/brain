# Completeness Sweep

## Purpose

An agent pass can stop after delivering only part of a requested change — the code compiles and the happy path
works, but a validation branch, a doc update, or a related CRUD case never gets touched. A Completeness Sweep is
the closing pass that asks *"did we cover everything required, not merely implement something that works?"*,
reconstructing the full obligation list and checking each obligation for evidence before completion is declared.

## Rules

- A Completeness Sweep MUST run last, after implementation and after every other pass.
- The obligation list MUST be reconstructed from the request and acceptance criteria, existing
  architecture/conventions, affected code paths, tests, documentation, configuration/migrations, and
  error/security/observability/compatibility concerns.
- Every obligation MUST be mapped to evidence in the chain `Requirement → Implementation → Test → Documentation`.
- An obligation without evidence MUST resolve to exactly one of: implement it, ask a clarifying question, or
  record an explicit deferral.
- Completion MUST NOT be declared while an obligation lacks evidence.

## Design Guidance

The sweep checks coverage, not correctness or style — that is what separates it from the passes around it. Code
review asks "is the implementation correct and maintainable?", testing asks "does the implemented behavior
work?", simplification asks "can this be smaller or clearer?", and the sweep asks "did we implement every
required part?".

An explicit deferral is an acceptable close; silence is not.

Minimal instruction to embed as a closing step:

```
## Completeness sweep

Before completion:

1. Re-read the request and acceptance criteria.
2. Build a checklist of all explicit and implied obligations.
3. Map each obligation to implementation evidence.
4. Check tests, documentation, configuration, migrations, and error paths.
5. Resolve missing items or report them explicitly as deferred.
6. Do not declare completion while an obligation lacks evidence.
```

Distinct from [structure-checklist-workflow](structure-checklist-workflow.md): a checklist orders execution *during* the task, this sweep
checks coverage *after* the work is believed done.

## Exceptions

- None recorded yet.
