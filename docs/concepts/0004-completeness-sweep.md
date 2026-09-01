---
id: "0004"
title: Completeness Sweep
trigger: >-
  designing a skill's closing or completion step, declaring a task complete, reviewing whether a change covers
  every requirement, a change that compiles but may have missed a branch, deciding what a final pass should
  check, deferring an obligation
summary: >-
  A final, systematic pass run after implementation that maps every explicit and implied obligation
  (requirements, tests, docs, config/migrations, error/security/observability cases) to implementation evidence,
  resolving anything without evidence as a fix, a question, or an explicit deferral before completion is
  declared.
default: >-
  Close any task-completing skill with a sweep that maps each obligation to evidence and resolves the gaps as a
  fix, a question, or an explicit deferral — never silence.
owns:
  - "closing completeness check before a task is declared done"
applies_to:
  - plugins/**
  - skills/**
related: ["0002", "0005"]
---

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

Distinct from [0005](0005-checklist-workflow.md): a checklist orders execution *during* the task, this sweep
checks coverage *after* the work is believed done.

## Exceptions

- None recorded yet.
