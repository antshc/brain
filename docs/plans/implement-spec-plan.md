# Implement-Spec Entry Flow Refactor Plan

**Status:** Proposed — not implemented

**Scope:** `plugins/wf/skills/implement-spec` and removal of `auto` from `plugins/wf/skills/to-tickets`; `plugins/af` unchanged

**Flow reference:** [Implement-Spec Flows](./implement-spec-flows.md)

## Goal

Make input-type detection the first action, embed a self-contained **Breakdown Initiative** reference for missing tickets, and remove the plan-only execution mode. Move non-interactive ticket creation out of the standalone `/to-tickets` skill. Preserve sequential/parallel delivery, the one-subagent-per-ticket rule, HITL handling, verification, chore, review, and draft-PR gates.

## Decisions

1. **Plan input** (`plan.md` or inline description): ask for target repository, target/base branch, and initiative ID; validate them; create the routed GitHub spec; run **Breakdown Initiative**.
2. **Spec input** (GitHub issue): resolve routing and inspect native sub-issues first. Existing tickets skip breakdown; zero sub-issues trigger **Breakdown Initiative**.
3. **Breakdown Initiative**: a fresh planner subagent follows `implement-spec/references/breakdown.md` directly, then the orchestrator re-reads the graph and shows tickets, waves, and critical path. No runtime `/to-tickets` invocation; the orchestrator never creates tickets inline.
4. **Execution**: `sequential` remains the default; `parallel` retains `schedule=waves|graph` and `max-parallel=3` by default. `mode=plan` becomes unsupported and must fail explicitly, without creating execution worktrees or a PR.
5. **Standalone `/to-tickets`**: remove its `auto` input and every no-approval/no-`hitl` exception. Retain human-approved online/offline flows and their existing `hitl` policy.
6. **Scope**: leave all `plugins/af` skills unchanged. Leave the post-implementation pipeline and its draft-only policy unchanged.

## Implementation steps

1. **Refactor entry and routing** — In [`SKILL.md`](../../plugins/wf/skills/implement-spec/SKILL.md), begin with Plan-vs-Spec detection. Define `Prepare Plan`, `Prepare Spec`, and the shared `Breakdown Initiative` handoff. Move graph validation after those paths converge; retain cycle, scope, routing, and HITL guards.
2. **Require a plan's branch choice** — In [`references/github.md`](../../plugins/wf/skills/implement-spec/references/github.md), expand *Create spec* to ask for the target/base branch alongside repository and initiative ID. Check the branch exists, persist the corresponding `repo:base:<branch>` label, and read back the created spec. Do not silently use the repository default branch for plan input.
3. **Embed the automated ticket workflow** — Add `implement-spec/references/breakdown.md`. Adapt the existing [`to-tickets` workflow](../../plugins/wf/skills/to-tickets/SKILL.md) and its GitHub/template references into a **self-contained, online-only, non-interactive** variant: validate spec and source precedence; explore Concepts/ADRs; draft end-to-end vertical slices; preserve full requirements, acceptance criteria, and the complete ticket-body template; reconcile prior children; create/link tickets and native blockers; verify readback. Keep the shared GitHub procedures in `references/github.md`; do not add separate breakdown-GitHub or issue-template files. Exclude approval questions, `hitl` labeling, offline publication, and fallback to the standalone skill. Fail/report incomplete GitHub operations without misreporting success.
4. **Wire the embedded reference** — In [`SKILL.md`](../../plugins/wf/skills/implement-spec/SKILL.md) and `agents/planner.md`, use the name **Breakdown Initiative**. The planner subagent must load `references/breakdown.md`, follow its ticket-publication procedure, and remain the only ticket writer. Replace all `/to-tickets auto` invocations and external-skill availability checks. A spec with existing sub-issues must not run the planner.
5. **Remove standalone auto mode** — In [`to-tickets/SKILL.md`](../../plugins/wf/skills/to-tickets/SKILL.md), delete `auto` from its description and argument hint, mode detection, approval and label exceptions, review/publish branches, and completion criteria. Require explicit user approval for every standalone publication; retain `hitl` labels and explicit offline handling. Check its references for stale auto-mode guidance.
6. **Separate execution references and remove plan-only mode** — Rename `references/Sequential.md` to lowercase `references/sequential.md`; route default sequential execution through it. Retain `references/parallel.md` for parallel scheduling. Delete `plan` from the `implement-spec` mode contract, workflow branches, output, and completion criteria; remove `mode=plan` termination and worktree exceptions. Reject obsolete `mode=plan` explicitly.
7. **Update discovery** — Correct the stale `implement-spec` link in [`README.md`](../../README.md) to the `wf` path. Do not change the `af` implementations or marketplace registration.
8. **Author main skill and agent bodies** — Use [`/write-skill`](../../plugins/skill/skills/write-skill/SKILL.md) for `implement-spec/SKILL.md`. Use [`/write-agent`](../../plugins/skill/skills/write-agent/SKILL.md) for the content of each `agents/*.md`, but **omit all agent frontmatter**: these are internal prompt bodies, not independently registered coding agents. Preserve all behavior and prompt placeholders while moving existing prompt files into `agents/` (mapping below).
9. **Add regression coverage** — Add tests under `tests/wf/implement-spec/` for routing, embedded-reference completeness, non-interactive ticket publication, native links/reconciliation, supported modes, no planner for an already-ticketed spec, agent prompt placeholders, no agent frontmatter, and preserved downstream guards. Add `tests/wf/to-tickets/` tests for approval-required behavior and rejection of `auto`; follow existing repository test conventions.
10. **Validate** — Run focused tests and repository consistency checks. Search `wf` for obsolete `/to-tickets auto`, `Bootstrap tickets`, `mode=plan`, and plan-only exceptions; verify every new relative link, renamed prompt, template, and Graph/PR guard. Remove obsolete prompt/reference files only after their content is accounted for.

## Target skill structure

```text
implement-spec/
├── SKILL.md
│
├── agents/
│   ├── planner.md
│   ├── implementer.md
│   ├── verifier.md
│   └── chore.md
│
└── references/
    ├── breakdown.md
    ├── sequential.md
    ├── parallel.md
    ├── github.md
    └── fetch-diff.md
```

The root is `plugins/wf/skills/implement-spec/`. Keep this structure exact; do not add extra agent or reference files. `breakdown.md` owns the auto-only procedure and full ticket template, with reusable GitHub operations in `github.md`. The standalone `plugins/wf/skills/to-tickets/` stays separate and approval-based.

### Authoring and migration rules

1. **Main skill:** Run `/write-skill` in write mode for `SKILL.md`, supplying this plan, the [flows](./implement-spec-flows.md), and the existing skill as input. Keep valid `SKILL.md` frontmatter and the orchestration/guard contract; verify the write-skill draft/shrink phases preserve behavior.
2. **Agent bodies:** Run `/write-agent` individually for `agents/planner.md`, `agents/implementer.md`, `agents/verifier.md`, and `agents/chore.md`. Use its body-writing and review guidance, but **do not include YAML frontmatter, tool lists, model metadata, or routing descriptions** in these four files. This explicitly overrides `/write-agent`'s normal standalone-agent frontmatter requirement. `SKILL.md` owns subagent selection, runtime configuration, and invocation.
3. **Prompt migration:** Move `references/plan.md` → `agents/planner.md`, `references/implement.md` → `agents/implementer.md`, `references/verify.md` → `agents/verifier.md`, and `references/chore.md` → `agents/chore.md`. Preserve every prompt placeholder, output JSON contract, validation guard, and failure rule; update callers before removing old paths.
4. **Reference migration:** Consolidate the automated ticket workflow and issue template into `references/breakdown.md`; lowercase `references/Sequential.md` → `references/sequential.md`; retain `github.md`, `parallel.md`, and `fetch-diff.md`. Keep the ticket template semantically consistent with standalone `/to-tickets` unless divergence is intentional and tested.

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
- **Duplicate tickets on retry:** Preserve standalone reconciliation safeguards in `breakdown.md` and `github.md`; re-read native parent/blocker links after breakdown.
- **Embedded-reference drift:** Keep the full ticket body template and spec/Concept/ADR precedence; validate copied template parity until intentional divergence is approved.
- **Approval regression:** Standalone `/to-tickets` must never inherit the embedded no-approval path. Only `implement-spec`'s planner can publish without approval.
- **Agent-format mismatch:** `/write-agent` normally requires frontmatter; use it for instruction-body drafting only. Validate that final `agents/*.md` files contain no frontmatter and that the orchestrator supplies runtime tools/models/permissions.
- **Unexpected implementation from an old `mode=plan` caller:** Reject that mode rather than treating it as sequential.
- **Cross-plugin drift:** `af` remains intentionally out of scope; only the two named `wf` skills and their docs/tests change.
- **Regressions after ticket integration:** Retain commit evidence, HITL exclusions, app-verification limits, independent code review, and draft-only PR behavior.

**Done when:** The [flow reference](./implement-spec-flows.md) matches the implemented `wf` contract, all acceptance scenarios pass, and no delivery or review safeguards have weakened.
