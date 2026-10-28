# Implement-Spec Entry Flow Refactor Plan

**Status:** Proposed — not implemented

**Scope:** `plugins/wf/skills/implement-spec` only

**Flow reference:** [Implement-Spec Flows](./implement-spec-flows.md)

## Goal

Make input-type detection the first action, reuse one **Breakdown Initiative** subflow for missing tickets, and remove the plan-only execution mode. Preserve sequential/parallel delivery, the one-subagent-per-ticket rule, HITL handling, verification, chore, review, and draft-PR gates.

## Decisions

1. **Plan input** (`plan.md` or inline description): ask for target repository, target/base branch, and initiative ID; validate them; create the routed GitHub spec; run **Breakdown Initiative**.
2. **Spec input** (GitHub issue): resolve routing and inspect native sub-issues first. Existing tickets skip breakdown; zero sub-issues trigger **Breakdown Initiative**.
3. **Breakdown Initiative**: a fresh planner subagent invokes `/to-tickets auto`, then the orchestrator re-reads the graph and shows tickets, waves, and critical path. The orchestrator never creates tickets inline.
4. **Execution**: `sequential` remains the default; `parallel` retains `schedule=waves|graph` and `max-parallel=3` by default. `mode=plan` becomes unsupported and must fail explicitly, without creating execution worktrees or a PR.
5. **Scope**: leave `plugins/af/skills/implement-spec` unchanged. Leave the post-implementation pipeline and its draft-only policy unchanged.

## Implementation steps

1. **Refactor entry and routing** — In [`SKILL.md`](../../plugins/wf/skills/implement-spec/SKILL.md), begin with Plan-vs-Spec detection. Define `Prepare Plan`, `Prepare Spec`, and the shared `Breakdown Initiative` handoff. Move graph validation after those paths converge; retain cycle, scope, routing, and HITL guards.
2. **Require a plan's branch choice** — In [`references/github.md`](../../plugins/wf/skills/implement-spec/references/github.md), expand *Create spec* to ask for the target/base branch alongside repository and initiative ID. Check the branch exists, persist the corresponding `repo:base:<branch>` label, and read back the created spec. Do not silently use the repository default branch for plan input.
3. **Unify breakdown** — In [`SKILL.md`](../../plugins/wf/skills/implement-spec/SKILL.md) and [`references/plan.md`](../../plugins/wf/skills/implement-spec/references/plan.md), use the name **Breakdown Initiative**, preserving the planner template, its required placeholders, and `/to-tickets auto` behavior. A spec with existing sub-issues must not run the planner.
4. **Remove plan-only mode** — Delete `plan` from the mode contract, workflow branches, output, and completion criteria. In [`references/parallel.md`](../../plugins/wf/skills/implement-spec/references/parallel.md), retain planning *as a phase of parallel execution*, but remove `mode=plan` termination and worktree exceptions. Reject obsolete `mode=plan` explicitly.
5. **Update discovery** — Correct the stale `implement-spec` link in [`README.md`](../../README.md) to the `wf` path. Do not change the `af` implementation or marketplace registration.
6. **Add regression coverage** — Create contract tests under `tests/wf/implement-spec/` for entry ordering, input routing, shared breakdown, supported modes, no planner for an already-ticketed spec, and preserved downstream guards. Keep the tests consistent with existing repository test conventions.
7. **Validate** — Run the new focused tests and applicable repository consistency checks; search the affected `wf` files for stale `Bootstrap tickets`, `mode=plan`, and plan-only worktree/PR exceptions. Confirm links and referenced prompt placeholders resolve.

## Acceptance scenarios

| Input | Required behavior |
| --- | --- |
| Plan file or inline description | Ask repository, branch, initiative ID → create spec → Breakdown Initiative |
| Spec with no sub-issues | Breakdown Initiative → validate created graph |
| Spec with sub-issues | Reuse graph; no planner or ticket creation |
| `mode=sequential` or no mode | One fresh ticket implementer at a time in the integration worktree |
| `mode=parallel` | Conflict-aware scheduling, isolated ticket worktrees, serialized cherry-picks |
| `mode=plan` | Explicit unsupported-mode response |
| Open `hitl` ticket | Skip it; defer unsatisfied dependants |
| Completed implementation | Verify app → chore → clean/push → remove integration worktree → independent review → conditional spec closure; PR remains draft |

## Risks and safeguards

- **Wrong branch/repository:** Validate all three Plan answers, routing labels, source checkout, and the remote base before GitHub writes or worktree creation.
- **Duplicate tickets on retry:** Keep `/to-tickets auto` reconciliation and re-read native relationships after breakdown.
- **Unexpected implementation from an old `mode=plan` caller:** Reject that mode rather than treating it as sequential.
- **Cross-plugin drift:** `af` remains intentionally out of scope; this plan changes only `wf` and the documented `wf` link.
- **Regressions after ticket integration:** Retain commit evidence, HITL exclusions, app-verification limits, independent code review, and draft-only PR behavior.

**Done when:** The [flow reference](./implement-spec-flows.md) matches the implemented `wf` contract, all acceptance scenarios pass, and no delivery or review safeguards have weakened.
