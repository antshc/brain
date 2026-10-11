---
name: implement-template
description: Implements scoped features, bug fixes, and refactors as small functional slices with observable tests, compatibility checks, and safe version-control changes.
---

# Implementation Skill Template

## Inputs
- `{{change|Approved behavior or acceptance outcomes}}`
- `{{scope|Owned files, repository, and compatibility boundaries}}`

## Workflow
1. Inspect affected implementation, tests, and working-tree changes; protect unrelated edits. *Done when* impacted scope is known.
2. Implement the smallest complete vertical slice, including boundary and failure behavior. *Done when* the consumer-observable result exists.
3. Verify focused behavior and relevant regressions; correct failures before further slices. *Done when* checks pass or blockers are documented.
4. Stage only task-owned changes; commit when required by `{{workflow|Repository delivery process}}`. *Done when* change and evidence are traceable.
5. Perform a final completeness sweep for multi-part changes. *Done when* no required slice, test, docs, or configuration obligation is unaccounted.

## Guardrails
- MUST NOT weaken tests or quality thresholds to force a pass.
- MUST NOT stage unrelated files or alter existing behavior without a stated requirement.

## Completion criteria
- `{{change}}` works through its actual boundary; verification results and uncovered obligations are reported.

## Handoff
- `{{implementationSummary|Changed files, behavior, checks, commit, limitations}}`
