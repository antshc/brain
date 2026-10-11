---
name: implementation-template
description: Implements scoped functional changes and refactors as verifiable slices, preserving consumer behavior, unrelated edits, regression checks, and traceable commits.
---

<!-- @: Copy into a concrete skill folder; rename folder and frontmatter name, then replace all task placeholders. -->

# Implementation

## Change boundary
- Implement {{change|Required behavior}} in {{scope|Owned components and files}}.
1. Inspect current code, tests, and working tree. *Done when* unrelated edits and compatibility constraints are identified.

## Functional slice
2. Implement the smallest end-to-end behavior including failure and retry boundaries. *Done when* a consumer-observable slice works.
- MUST NOT broaden public contracts or delete behavior without requirement evidence.

## Checks
3. Exercise focused scenarios and relevant regressions. *Done when* checks pass or blockers have concrete evidence.
- MUST NOT weaken tests or quality gates to manufacture success.

## Delivery record
4. Stage only owned files; commit when required by {{policy|Repository workflow}}. *Done when* changes and evidence are traceable.
- {{changed|Files, effect on consumers, checks, commit or open changes}}

## Completeness sweep
5. For multi-part work, re-read the request last and account for code, tests, docs, configuration, and failure paths. *Done when* no requested obligation is silently missing.

## Completion criteria
- The new behavior works through its real interface, with outstanding risks and unrun checks explicit.
