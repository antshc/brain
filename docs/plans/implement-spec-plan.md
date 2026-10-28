# Implement-Spec Entry Flow Refactor Plan

**Status:** Proposed — not implemented

**Scope:** `plugins/wf/skills/implement-spec` and removal of `auto` from `plugins/wf/skills/to-tickets`; `plugins/af` unchanged

**Flow reference:** [Implement-Spec Flows](./implement-spec-flows.md)

## Goal

Make input-type detection the first action, embed a self-contained **Breakdown Initiative** reference for missing tickets, and remove the plan-only execution mode. Move non-interactive ticket creation out of the standalone `/to-tickets` skill. Preserve sequential/parallel delivery, the one-subagent-per-ticket rule, HITL handling, verification, chore, review, and draft-PR gates.

## Decisions

1. **Plan input** (`plan.md` or inline description): ask for target repository, target/base branch, and initiative ID; validate them; create the routed GitHub spec; run **Breakdown Initiative**.
2. **Spec input** (GitHub issue): resolve routing and inspect native sub-issues first. Existing tickets skip breakdown; zero sub-issues trigger **Breakdown Initiative**.
3. **Breakdown Initiative**: a fresh planner subagent follows `implement-spec/references/breakdown-initiative.md` directly, then the orchestrator re-reads the graph and shows tickets, waves, and critical path. No runtime `/to-tickets` invocation; the orchestrator never creates tickets inline.
4. **Execution**: `sequential` remains the default; `parallel` retains `schedule=waves|graph` and `max-parallel=3` by default. `mode=plan` becomes unsupported and must fail explicitly, without creating execution worktrees or a PR.
5. **Standalone `/to-tickets`**: remove its `auto` input and every no-approval/no-`hitl` exception. Retain human-approved online/offline flows and their existing `hitl` policy.
6. **Scope**: leave all `plugins/af` skills unchanged. Leave the post-implementation pipeline and its draft-only policy unchanged.

## Implementation steps

1. **Refactor entry and routing** — In [`SKILL.md`](../../plugins/wf/skills/implement-spec/SKILL.md), begin with Plan-vs-Spec detection. Define `Prepare Plan`, `Prepare Spec`, and the shared `Breakdown Initiative` handoff. Move graph validation after those paths converge; retain cycle, scope, routing, and HITL guards.
2. **Require a plan's branch choice** — In [`references/github.md`](../../plugins/wf/skills/implement-spec/references/github.md), expand *Create spec* to ask for the target/base branch alongside repository and initiative ID. Check the branch exists, persist the corresponding `repo:base:<branch>` label, and read back the created spec. Do not silently use the repository default branch for plan input.
3. **Embed the automated ticket workflow** — Add `implement-spec/references/breakdown-initiative.md`, `breakdown-github.md`, and `breakdown-issue-template.md`. Adapt the existing [`to-tickets` workflow](../../plugins/wf/skills/to-tickets/SKILL.md) and its GitHub/template references into a **self-contained, online-only, non-interactive** variant: validate spec and source precedence; explore Concepts/ADRs; draft end-to-end vertical slices; preserve full requirements, acceptance criteria, and issue template; reconcile prior children; create/link tickets and native blockers; verify readback. Do not carry over approval questions, `hitl` labeling, offline publication, or fallback to the standalone skill. Fail/report incomplete GitHub operations without misreporting success.
4. **Wire the embedded reference** — In [`SKILL.md`](../../plugins/wf/skills/implement-spec/SKILL.md) and [`references/plan.md`](../../plugins/wf/skills/implement-spec/references/plan.md), use the name **Breakdown Initiative**. The planner subagent must load the embedded reference and its bundled GitHub/template files and execute ticket publication itself; it remains the only ticket writer. Replace all `/to-tickets auto` invocations and external-skill availability checks. A spec with existing sub-issues must not run the planner.
5. **Remove standalone auto mode** — In [`to-tickets/SKILL.md`](../../plugins/wf/skills/to-tickets/SKILL.md), delete `auto` from its description and argument hint, mode detection, approval and label exceptions, review/publish branches, and completion criteria. Require explicit user approval for every standalone publication; retain `hitl` labels and explicit offline handling. Check its references for stale auto-mode guidance.
6. **Remove plan-only execution mode** — Delete `plan` from the `implement-spec` mode contract, workflow branches, output, and completion criteria. In [`references/parallel.md`](../../plugins/wf/skills/implement-spec/references/parallel.md), retain planning *as a phase of parallel execution*, but remove `mode=plan` termination and worktree exceptions. Reject obsolete `mode=plan` explicitly.
7. **Update discovery** — Correct the stale `implement-spec` link in [`README.md`](../../README.md) to the `wf` path. Do not change the `af` implementations or marketplace registration.
8. **Add regression coverage** — Add tests under `tests/wf/implement-spec/` for routing, embedded-reference completeness, non-interactive ticket publication, native links/reconciliation, supported modes, no planner for an already-ticketed spec, and preserved downstream guards. Add `tests/wf/to-tickets/` tests for approval-required behavior and rejection of `auto`; follow existing repository test conventions.
9. **Validate** — Run focused tests and repository consistency checks. Search `wf` for obsolete `/to-tickets auto`, `Bootstrap tickets`, `mode=plan`, and plan-only exceptions; verify the embedded relative links, prompt placeholders, issue template, and Graph/PR guards.

## Proposed skill structure

```text
plugins/wf/skills/
├── implement-spec/
│   ├── SKILL.md                         # Orchestrator; Plan/Spec entry and delivery
│   └── references/
│       ├── breakdown-initiative.md      # Embedded auto-only ticket workflow
│       ├── breakdown-github.md          # Online reconcile/create/link/readback
│       ├── breakdown-issue-template.md  # Complete ticket body template
│       ├── plan.md                      # Planner prompt, loads embedded breakdown
│       ├── github.md                    # Repository routing, PR, worktrees, closure
│       ├── parallel.md                  # Dependency/conflict scheduling
│       ├── implement.md                 # One-ticket implementer prompt
│       ├── verify.md                    # App verifier-fixer prompt
│       ├── chore.md                     # Cleanup prompt
│       └── fetch-diff.md                # PR diff retrieval
└── to-tickets/
    ├── SKILL.md                         # Interactive approval only; no auto
    └── references/
        ├── github.md                    # Standalone GitHub/offline operations
        └── issue-template.md            # Standalone ticket body template
```

`breakdown-initiative.md` is the entry reference; its two supporting files keep the embedded workflow independent of `/to-tickets`. The issue templates initially match so ticket structure does not regress; maintain an explicit consistency check or document intentional divergence.

## Acceptance scenarios

| Input | Required behavior |
| --- | --- |
| Plan file or inline description | Ask repository, branch, initiative ID → create spec → Breakdown Initiative |
| Spec with no sub-issues | Breakdown Initiative → validate created graph |
| Spec with sub-issues | Reuse graph; no planner or ticket creation |
| Embedded Breakdown Initiative | No questions; publish immediately through bundled online GitHub procedures; new tickets have no `hitl` label |
| Standalone `/to-tickets` | Present breakdown, wait for explicit approval, publish `hitl` tickets; `auto` unsupported |
| `mode=sequential` or no mode | One fresh ticket implementer at a time in the integration worktree |
| `mode=parallel` | Conflict-aware scheduling, isolated ticket worktrees, serialized cherry-picks |
| `mode=plan` | Explicit unsupported-mode response |
| Open `hitl` ticket | Skip it; defer unsatisfied dependants |
| Completed implementation | Verify app → chore → clean/push → remove integration worktree → independent review → conditional spec closure; PR remains draft |

## Risks and safeguards

- **Wrong branch/repository:** Validate all three Plan answers, routing labels, source checkout, and the remote base before GitHub writes or worktree creation.
- **Duplicate tickets on retry:** Copy the standalone reconciliation safeguards into `breakdown-github.md`; re-read native parent/blocker links after breakdown.
- **Embedded-reference drift:** Keep the full ticket body template and spec/Concept/ADR precedence; validate copied template parity until intentional divergence is approved.
- **Approval regression:** Standalone `/to-tickets` must never inherit the embedded no-approval path. Only `implement-spec`'s planner can publish without approval.
- **Unexpected implementation from an old `mode=plan` caller:** Reject that mode rather than treating it as sequential.
- **Cross-plugin drift:** `af` remains intentionally out of scope; only the two named `wf` skills and their docs/tests change.
- **Regressions after ticket integration:** Retain commit evidence, HITL exclusions, app-verification limits, independent code review, and draft-only PR behavior.

**Done when:** The [flow reference](./implement-spec-flows.md) matches the implemented `wf` contract, all acceptance scenarios pass, and no delivery or review safeguards have weakened.
