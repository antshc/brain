# Completeness Sweep

## Purpose

An agent pass can stop after delivering only part of a requested change — the code compiles and the happy path works, but a validation branch, a doc update, or a related CRUD case never gets touched. A Completeness Sweep is a final, systematic pass that asks *"did we cover everything required, not merely implement something that works?"* — reconstructing the full obligation list and checking each obligation for evidence before the task is declared complete. It is not a Copilot/GPT/Claude feature; it is a reusable agent-workflow pattern any skill can adopt as its closing step.

## Design Guidance

- Run the sweep last, after implementation and after other passes (code review, testing, simplification) — it checks coverage, not correctness or style.
- Reconstruct the obligation list from: the user request and acceptance criteria, existing architecture/conventions, affected code paths, tests, documentation, configuration/migrations, and error/security/observability/compatibility concerns.
- Map every obligation to evidence in the chain `Requirement → Implementation → Test → Documentation`. An obligation with no evidence in this chain is not done, regardless of how confident the implementation looks.
- Anything without evidence resolves to exactly one of: implement the missing item, ask a clarifying question, or record an explicit deferral. Never leave it silently unaddressed.
- Do not declare completion while an obligation lacks evidence — an explicit deferral is an acceptable close, silence is not.
- Distinct from other passes by the question each asks: code review asks "is the implementation correct and maintainable?"; testing asks "does the implemented behavior work?"; simplification asks "can the solution be made smaller or clearer?"; a Completeness Sweep asks "did we implement every required part?"
- Minimal skill instruction to embed as a closing step:

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

## Exceptions

- None recorded yet.
