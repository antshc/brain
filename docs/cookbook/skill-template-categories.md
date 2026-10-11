# Skill Template Categories

Reusable skill-template families derived from the [Cookbook Principle Index](index.md).

**Category** = what kind of task a skill performs. **Cookbook practice** = how the agent must perform the task. Practices may apply to multiple categories. The examples below are illustrative, not additional cookbook recipes.

| Category / template | Problem, context, areas, and example | Practices from cookbook |
|---|---|---|
| **1. Investigation** `investigate-*` | **Problem:** Unknown system behavior or rationale. **Context/areas:** Codebase exploration, dependency tracing, legacy systems. **Example:** Find how authentication works across services. | Investigate current code paths; reconstruct rationale from evidence; record investigation queries and contradictions; separate evidence collection from synthesis. |
| **2. Requirements** `specify-*` | **Problem:** Ambiguous requirements or unclear scope. **Context/areas:** Product discovery, feature specifications, stakeholder alignment. **Example:** Define expected behavior for an RBAC feature. | Clarify intent and assumptions; challenge unnecessary scope; explore alternatives; define measurable thresholds; track open questions. |
| **3. Planning** `plan-*` | **Problem:** Complex work needs decomposition and ordering. **Context/areas:** Feature delivery, migrations, multi-repository changes. **Example:** Split an epic into dependency-ordered implementation tickets. | Build dependency-ordered verifiable slices; preserve incomplete plans; establish approval gates; separate planning from implementation. |
| **4. Architecture & contracts** `design-*` | **Problem:** Components or APIs have unclear boundaries. **Context/areas:** System architecture, API design, deep modules, refactoring. **Example:** Design Git branch and worktree service contracts. | Derive contracts from consumer usage; model domain invariants; choose foundations before features; minimize abstractions; document alternatives and tradeoffs. |
| **5. Experimentation** `experiment-*` | **Problem:** Technical uncertainty cannot be resolved reliably by reasoning alone. **Context/areas:** SDK evaluation, integration feasibility, architectural decisions. **Example:** Compare approaches for controlling Copilot CLI in Docker. | Compare prototypes; resolve decisions with throwaway experiments; prove key safety assumptions; measure observable results; reject unsupported hypotheses. |
| **6. Implementation** `implement-*` | **Problem:** Deliver functionality without regressions or unnecessary complexity. **Context/areas:** Features, bug fixes, refactoring. **Example:** Implement an API endpoint with tests and commit gates. | Implement complete vertical slices; prefer the smallest change; preserve observable behavior; make operations idempotent; verify each slice. |
| **7. Debugging** `diagnose-*` | **Problem:** A failure exists, but its root cause is unknown. **Context/areas:** Production incidents, failing tests, integration errors. **Example:** Diagnose intermittent 503 responses from a service. | Reproduce failures; gather runtime observations; eliminate hypotheses; fix root causes rather than symptoms; verify regression resolution. |
| **8. Verification & testing** `verify-*` | **Problem:** Completed work may not satisfy its requirements. **Context/areas:** Acceptance, integration, and regression testing. **Example:** Verify RBAC covers every required role and operation. | [Verification, exit criteria, completeness sweep](verification-exit-criteria-completeness-sweep.md); test observable behavior; prove the real artifact; focused functional-slice testing. |
| **9. Review** `review-*` | **Problem:** An implementation or design needs independent evaluation. **Context/areas:** Code, architecture, and security reviews. **Example:** Review whether a refactor preserves behavior. | Challenge claims independently; inspect tests; classify findings by severity; require evidence for each finding; reconcile disagreements. |
| **10. Security** `secure-*` | **Problem:** Changes can introduce vulnerabilities or violate trust boundaries. **Context/areas:** Authentication, authorization, secrets, supply chain. **Example:** Verify tenant isolation in a multi-tenant API. | Threat-model system boundaries; validate untrusted inputs; protect destructive operations; review authorization; keep secrets out of code and logs. |
| **11. Performance** `optimize-*` | **Problem:** A system is slow or consumes excessive resources. **Context/areas:** Backend throughput, databases, memory, frontend latency. **Example:** Improve worker throughput without increasing resource consumption. | Measure bottlenecks; compare equivalent baselines; repeat benchmarks; remove unnecessary work; retain only proven optimizations. |
| **12. Delivery & operations** `deliver-*` | **Problem:** Verified changes must reach production safely. **Context/areas:** CI/CD, deployments, releases, migrations. **Example:** Deploy a schema change with rollback validation. | Verify the reviewed PR patch; enforce CI gates; use staged rollout thresholds; test rollback paths; verify live user flows and health signals. |
| **13. Orchestration** `orchestrate-*` | **Problem:** Multiple agents or tasks require coordination without losing ownership or context. **Context/areas:** Agent crews, parallel development, autonomous workflows. **Example:** Assign independent tickets to coding agents and aggregate results. | Delegate bounded responsibilities; isolate agent context; use explicit handoff contracts; coordinate parallel workers; enforce stop conditions. |
| **14. Context & continuity** `resume-*` | **Problem:** Sessions lose decisions, progress, or prior failure knowledge. **Context/areas:** Long-running tasks, session recovery, autonomous loops. **Example:** Resume interrupted development without repeating investigation. | [Persistent memory and gotchas](gotchas-and-persistent-memory.md); session ledgers; resume from the execution trail; preserve decisions, changed files, and verification. |
| **15. Documentation** `document-*` | **Problem:** Technical knowledge is difficult to communicate or maintain. **Context/areas:** ADRs, architecture docs, guides, runbooks. **Example:** Document a selected architecture and rejected alternatives. | Choose tutorial/how-to/reference/explanation structure; preserve rationale; cite authoritative sources; distinguish evidence from assumptions; use concise language. |
| **16. Skill authoring & learning** `author-*` | **Problem:** Agent instructions are unreliable, duplicated, or difficult to reuse. **Context/areas:** Agent skills, instruction design, prompt evaluation. **Example:** Create a reusable skill enforcing completeness verification. | Constraint-first instructions; skill triggers; progressive disclosure; canary verification; skill-on/off evaluation; improvement flywheel. |

## Shared template

```yaml
name: <verb-object>
description: <trigger and purpose>

inputs:
  - <required context>

constraints:
  - MUST <required behavior>
  - MUST NOT <forbidden shortcut>

workflow:
  - <category-specific steps>

exit:
  - <observable completion criteria>

handoff:
  - <evidence, decisions, gotchas>
```

Use only applicable sections. Reuse cookbook recipes instead of duplicating common instructions.

## Cookbook coverage

The index currently marks five principles covered by two recipes:

- [Verification, exit criteria, completeness sweep](verification-exit-criteria-completeness-sweep.md) — categories 6, 8, 9, 12.
- [Gotchas and persistent memory](gotchas-and-persistent-memory.md) — categories 7, 13, 14, 16.

Uncovered checklist entries are **sources of candidate practices**, not completed recipes. Keep the categories separate from recipe coverage tracking.
