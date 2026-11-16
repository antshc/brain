---
name: draft-artifact
description: >-
  Create and update user stories, implementation tasks, bug reports, specifications, high-level designs, and technical handovers. Use for drafting or revising these artifacts from supplied context.
argument-hint: "story | task | bug | spec | hld | toi"
---

# Draft an artifact

Own artifact structure, rendering and document checks. Callers own design decisions, decomposition, evidence dispatch, approvals, integration and publication.

## Routing

| Route | Select for | Playbook | Output |
|---|---|---|---|
| `story` | One atomic user story | [Story](playbooks/story.md) | Title and story body |
| `task` | One implementation work item with supplied scope | [Task](playbooks/task.md) | Complete task body |
| `bug` | One defect report from observed behavior | [Bug](playbooks/bug.md) | Reproduction, actual and expected results |
| `spec` | A specification or PRD from supplied requirements and decisions | [Spec](playbooks/spec.md) | Specification body |
| `hld` | A high-level design from supplied evidence and resolved decisions | [HLD](playbooks/hld.md) | New or incrementally updated HLD |
| `toi` | A developed feature's technical handover | [TOI](playbooks/toi.md) | TOI document |

## Execution

1. Honor an explicit route; otherwise infer the artifact type. Ambiguous type → ask and wait. Replies continue the active route unless redirected. Combined requests → author in dependency order, then request order for independent artifacts. Done when each requested artifact has a route.
2. Select `draft` (new), `update` (existing) or `normalize` (requirements wording only). For standalone requirements without an artifact type, use `spec normalize`; preserve the supplied fragment's structure. Done when operation, scope and caller constraints are known.
3. Read the selected playbook and its required resources fully; load conditional resources only when triggered. Resolve paths from this skill directory. Done when all inputs for the next action are loaded.
4. Execute the route. Use supplied context and permitted local reads; return missing evidence or decisions to the caller. Do not independently dispatch research/proof, decompose work, publish, commit or manage worktrees. Existing Bug and TOI read-only exploration remains permitted. Done when the artifact or an explicit incomplete result is returned.

## Shared requirements rules

For `story`, `task`, `spec`, `hld`, and Bug expected behavior, read [Requirements](references/requirements.md) and [Requirements terms](references/requirements-terms.md). Normalize authored behavioral statements at their existing level using the domain glossary.

Preserve authoritative verbatim text. Report leaked implementation in such text as a source conflict; do not silently rewrite it. Keep technical decisions, structural relocation constraints, contracts, reproduction steps, observations and evidence exact. Document-specific rendering may derive criteria from rules/edge cases while retaining their source relationships.

For `normalize`, return the supplied text's structure with corrected wording and a correction note; skip full-template rendering, contract/diagram generation and unrelated edits. No leaks → report no corrections.

## Conditional resources

| Trigger | Resource |
|---|---|
| `story` draft/update | [Story template](templates/story-template.md) |
| `task` draft/update | [Task template](templates/task-template.md) |
| `bug` draft/update | [Bug template](templates/bug-template.md) |
| `spec` draft/update | [Spec template](templates/spec-template.md) |
| `hld` draft/update, including evolving drafts | [HLD template](templates/hld-template.md), [Decision bullets](references/decision-bullet.md), [HLD updates](references/hld-updates.md) |
| `toi` | [TOI template](templates/toi-template.md) |

Changed contracts → *Load and follow the `doc-contracts` skill to write an API, database, resource, or GUI contract delta* using the route's listed kinds and inputs. Missing contract facts return as gaps; never hand-write a delta.

Required diagrams → *Load and follow the `doc-diagram` skill to create Mermaid architecture or behavior diagrams* using the selected route's view and source facts. Missing decisions/evidence return as gaps.

General prose refinement when needed → *Load and follow the `writing-style` skill to apply clear, precise writing to technical docs* using the matching prose route; preserve the artifact template and protected text.

## Output contract

Return the selected route's artifact. Use an explicit output path when supplied; HLD and TOI define defaults. Save drafts only within caller authorization; otherwise print the body. Return update summaries, source conflicts and missing evidence separately from publishable content. Keep exact-body-only route outputs free of wrapper prose; report blockers to the caller separately.

Mark unsupported facts Unknown or Pending as the route requires. Incomplete content is a draft, not readiness or publication success.

## Completion criteria

- Every requested artifact follows its selected route and canonical template, or the normalize operation preserves the supplied structure.
- Behavioral text passes shared requirements rules; protected source text and technical evidence retain their required fidelity.
- No unsupported decisions, invented facts, authoring directives or unintended placeholders remain; required structural markers survive.
- Updates preserve unaffected content and report conflicts/gaps. No publication or workflow authority is inferred from drafting.
