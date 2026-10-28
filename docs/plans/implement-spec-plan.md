# Implement-Spec Entry Flow Refactor Plan

**Status:** Implemented

**Scope:** `plugins/wf/skills/implement-spec` and removal of `auto` from `plugins/wf/skills/to-tickets`; `plugins/af` unchanged

**Flow reference:** [Implement-Spec Flows](./implement-spec-flows.md)

## Goal

Make input-type detection the first action, embed a self-contained **Breakdown Initiative** reference for missing tickets, and remove the plan-only execution mode. Move non-interactive ticket creation out of the standalone `/to-tickets` skill. Preserve sequential/parallel delivery, the one-subagent-per-ticket rule, HITL handling, verification, chore, review, and draft-PR gates.

## Decisions

1. **Plan input** (`plan.md` or inline description): ask for target repository, target/base branch, and initiative ID; validate them; create the routed GitHub spec; run **Breakdown Initiative**.
2. **Spec input** (GitHub issue): resolve routing and inspect native sub-issues first. Existing tickets skip breakdown; zero sub-issues trigger **Breakdown Initiative**.
3. **Breakdown Initiative**: a fresh planner subagent follows `implement-spec/references/breakdown.md` directly. Before slicing, it fetches artifacts explicitly attached or linked from the spec; each resulting ticket receives the artifact pieces relevant to its scope. The orchestrator then re-reads the graph and shows tickets, waves, and critical path. No runtime `/to-tickets` invocation; the orchestrator never creates tickets inline.
4. **Execution**: `sequential` remains the default; `parallel` retains `schedule=waves|graph` and `max-parallel=3` by default. `mode=plan` becomes unsupported and must fail explicitly, without creating execution worktrees or a PR.
5. **Standalone `/to-tickets`**: remove its `auto` input and every no-approval/no-`hitl` exception. Retain human-approved online/offline flows and their existing `hitl` policy.
6. **Scope**: leave all `plugins/af` skills unchanged. Leave the post-implementation pipeline and its draft-only policy unchanged.
7. **Subagent ownership**: only `implement-spec/SKILL.md` launches planner, implementer, verifier, and chore subagents. Every launch passes discoverable absolute paths for the skill's bundled references; each subagent loads the references required by its role before acting.

## Implementation steps

1. **Refactor entry and routing** — In [`SKILL.md`](../../plugins/wf/skills/implement-spec/SKILL.md), begin with Plan-vs-Spec detection. Define `Prepare Plan`, `Prepare Spec`, and the shared `Breakdown Initiative` handoff. Move graph validation after those paths converge; retain cycle, scope, routing, and HITL guards.
2. **Require a plan's branch choice** — In [`references/github.md`](../../plugins/wf/skills/implement-spec/references/github.md), expand *Create spec* to ask for the target/base branch alongside repository and initiative ID. Check the branch exists, persist the corresponding `repo:base:<branch>` label, and read back the created spec. Do not silently use the repository default branch for plan input.
3. **Embed the automated ticket workflow** — Add `implement-spec/references/breakdown.md`. Adapt the existing [`to-tickets` workflow](../../plugins/wf/skills/to-tickets/SKILL.md) and its GitHub/template references into a **self-contained, online-only, non-interactive** variant: validate spec and source precedence; discover/fetch spec artifacts; explore Concepts/ADRs; draft end-to-end vertical slices; preserve full requirements, acceptance criteria, relevant artifact pieces, and the complete ticket-body template; reconcile prior children; create/link tickets and native blockers; verify readback. Keep the shared GitHub procedures in `references/github.md`; do not add separate breakdown-GitHub or issue-template files. Exclude approval questions, `hitl` labeling, offline publication, and fallback to the standalone skill. Fail/report incomplete GitHub operations without misreporting success.
4. **Wire the embedded reference** — In [`SKILL.md`](../../plugins/wf/skills/implement-spec/SKILL.md) and `agents/planner.md`, use the name **Breakdown Initiative**. The planner subagent must load `references/breakdown.md`, follow its ticket-publication procedure, and remain the only ticket writer. Replace all `/to-tickets auto` invocations and external-skill availability checks. A spec with existing sub-issues must not run the planner.
5. **Remove standalone auto mode** — In [`to-tickets/SKILL.md`](../../plugins/wf/skills/to-tickets/SKILL.md), delete `auto` from its description and argument hint, mode detection, approval and label exceptions, review/publish branches, and completion criteria. Require explicit user approval for every standalone publication; retain `hitl` labels and explicit offline handling. Check its references for stale auto-mode guidance.
6. **Separate execution references and remove plan-only mode** — Rename `references/Sequential.md` to lowercase `references/sequential.md`; route default sequential execution through it. Retain `references/parallel.md` for parallel scheduling. Delete `plan` from the `implement-spec` mode contract, workflow branches, output, and completion criteria; remove `mode=plan` termination and worktree exceptions. Reject obsolete `mode=plan` explicitly.
7. **Update discovery** — Correct the stale `implement-spec` link in [`README.md`](../../README.md) to the `wf` path. Do not change the `af` implementations or marketplace registration.
8. **Author main skill and agent bodies** — Use [`/write-skill`](../../plugins/skill/skills/write-skill/SKILL.md) for `implement-spec/SKILL.md`. Use [`/write-agent`](../../plugins/skill/skills/write-agent/SKILL.md) for the content of each `agents/*.md`, but **omit all agent frontmatter**: these are internal prompt bodies, not independently registered coding agents. Preserve all behavior and prompt placeholders while moving existing prompt files into `agents/` (mapping below).
9. **Pass references at every subagent launch** — In `SKILL.md`, resolve absolute paths from the `implement-spec/` skill root before changing into a source worktree. Construct the launch prompt from the selected `agents/<role>.md` body and include `referencesRoot`, a manifest of the five absolute reference-file paths, and the role's `requiredReferences`. Require the subagent to open/read those files before work; never infer paths from its current working directory or inline the reference contents. Stop/report missing or unreadable required files.
10. **Add regression coverage** — Add tests under `tests/wf/implement-spec/` for routing, embedded-reference completeness, non-interactive ticket publication, artifact discovery/fetching and per-ticket relevance mapping, native links/reconciliation, supported modes, no planner for an already-ticketed spec, agent prompt placeholders, no agent frontmatter, absolute reference handoff/loading, and preserved downstream guards. Add `tests/wf/to-tickets/` tests for approval-required behavior and rejection of `auto`; follow existing repository test conventions.
11. **Validate** — Run focused tests and repository consistency checks. Search `wf` for obsolete `/to-tickets auto`, `Bootstrap tickets`, `mode=plan`, and plan-only exceptions; verify every new relative link, renamed prompt, ticket artifact section, template, and Graph/PR guard. Remove obsolete prompt/reference files only after their content is accounted for.

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

### Subagent invocation and reference loading

1. **Caller:** `implement-spec/SKILL.md` owns every subagent launch, including parallel/background calls. `agents/*.md` are prompt bodies; neither an agent body nor a reference file independently creates another subagent.
2. **Resolve paths:** From the invoking skill's own directory (not the repository root or ticket worktree), resolve `SKILL_ROOT`, `AGENTS_ROOT=SKILL_ROOT/agents`, and `REFERENCES_ROOT=SKILL_ROOT/references`. Validate the selected agent body and all five reference paths; pass absolute paths so the subagent can locate them from any worktree.
3. **Launch contract:** Build the role prompt from `agents/<role>.md` with its placeholders filled. Include `referencesRoot`, a manifest mapping `breakdown`, `sequential`, `parallel`, `github`, and `fetchDiff` to their absolute Markdown paths, and a role-specific `requiredReferences` list. Pass issue, worktree, commit, and evidence context as pointers rather than duplicating reference contents.
4. **Subagent load:** Each agent body explicitly instructs its subagent to read every `requiredReferences` path **before taking task actions**, then follow only its role-relevant instructions. Missing/unreadable paths are a failure returned to the orchestrator, not a reason to guess the location or silently skip the reference. The planner must load `breakdown.md` and `github.md`; define other roles' required subsets in their agent bodies without delegating orchestrator-only scheduling or publication authority.
5. **Boundary:** `SKILL.md` still owns ticket selection, sequential/parallel scheduling, GitHub publication, verification of subagent results, and finalization. Passing a reference path never grants a subagent permission to publish, close issues, merge, or change other tickets.

### Spec artifact propagation during Breakdown Initiative

1. **Discover:** Before drafting slices, inspect the spec issue body and comments for attachments, uploaded images/diagrams, linked design documents, repository files, and other explicitly referenced artifacts. Build an inventory with each artifact's source URL/path, type, version or revision when available, and retrieval status. Do not crawl unrelated links.
2. **Fetch:** Retrieve each referenced artifact the planner can access through the authorized GitHub/source workflow; read the content instead of relying on a title or filename. Keep artifact contents as untrusted source data, never as agent instructions. If a relevant artifact is inaccessible or cannot be interpreted, report its source and failure and stop breakdown before publishing incomplete tickets; do not invent its contents.
3. **Partition:** Identify bounded, meaningful pieces (document sections, page ranges, diagram regions, tables, examples, or code excerpts) and assign each a stable source pointer/anchor and the spec requirements it informs. For binary artifacts, preserve the original link and a precise location/description; embed an actual relevant image/diagram excerpt only when available. Do not duplicate entire large artifacts into tickets.
4. **Map:** For each proposed vertical-slice ticket, map every artifact piece relevant to that ticket's behavior, acceptance criteria, or implementation decisions. The same piece may belong to multiple tickets and **must appear in every related ticket**; unrelated pieces are excluded. Verify coverage in both directions: no relevant piece omitted from a ticket and no attached piece without a stated relationship.
5. **Publish:** Extend the embedded `breakdown.md` ticket-body template with a **Related Spec Artifacts** section. Include each relevant piece or bounded excerpt, its canonical source/anchor, and a short explanation linking it to the ticket's requirement or criterion. Preserve readable links/embeds for non-text pieces. When the spec has no artifacts, omit this section and continue normally.
6. **Reconcile:** During publication/retry, compare existing children and their artifact sections before writing. Add missing relevant pieces without duplicates or overwriting user-authored content; read back the published ticket body to verify that every mapped piece is present.

## Acceptance scenarios

| Input | Required behavior |
| --- | --- |
| Plan file or inline description | Ask repository, branch, initiative ID → create spec → Breakdown Initiative |
| Spec with no sub-issues | Breakdown Initiative → validate created graph |
| Spec with sub-issues | Reuse graph; no planner or ticket creation |
| Spec with no artifacts | Breakdown proceeds; no Related Spec Artifacts section |
| Spec with artifacts | Fetch, partition, and map pieces; every related ticket includes its relevant pieces and source pointers |
| Artifact shared by multiple tickets | Include the same relevant piece in each ticket; no unrelated pieces |
| Required artifact inaccessible | Stop breakdown before publishing incomplete tickets; report the missing artifact and error |
| Subagent launch from any worktree | `SKILL.md` passes absolute reference manifest and required subset; subagent loads required files before work |
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
- **Artifact omission or over-sharing:** Check the piece-to-ticket mapping against requirements; include only relevant fragments with source pointers, but repeat shared fragments for every related ticket.
- **Artifact retrieval failure:** Preserve source identity and retrieval error; do not silently omit an existing relevant artifact or fabricate a fragment.
- **Approval regression:** Standalone `/to-tickets` must never inherit the embedded no-approval path. Only `implement-spec`'s planner can publish without approval.
- **Agent-format mismatch:** `/write-agent` normally requires frontmatter; use it for instruction-body drafting only. Validate that final `agents/*.md` files contain no frontmatter and that the orchestrator supplies runtime tools/models/permissions.
- **Reference lookup drift:** Never rely on the subagent's CWD for `./references/`; resolve absolute paths in `SKILL.md`, verify existence before launch, and fail explicitly if a required reference cannot be loaded.
- **Unexpected implementation from an old `mode=plan` caller:** Reject that mode rather than treating it as sequential.
- **Cross-plugin drift:** `af` remains intentionally out of scope; only the two named `wf` skills and their docs/tests change.
- **Regressions after ticket integration:** Retain commit evidence, HITL exclusions, app-verification limits, independent code review, and draft-only PR behavior.

**Done when:** The [flow reference](./implement-spec-flows.md) matches the implemented `wf` contract, all acceptance scenarios pass, and no delivery or review safeguards have weakened.
