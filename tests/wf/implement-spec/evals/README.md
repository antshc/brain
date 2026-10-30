# Planning evaluations

Use `planning-scenarios.json` as raw task input for a fresh agent with the current `to-tickets` decomposition rules, planner body, and breakdown reference. Supply each case's `files` as its synthetic repository context and preserve `existingTickets` identities. Draft only; use no live tracker, publication, or implementation. Supply exact runtime-supported model/effort candidates. Do not give the agent this rubric or previous results.

Return task outcomes/exclusions, producer assumptions, blocker graph, footprints/conflicts, criterion-to-check mappings, commands/prerequisites/evidence, and model recommendations with reasons. Mark unsupported environment facts and missing commands as unknown.

Judge outputs against the raw requirements, not an exact task count or golden wording:

| Case | Required observations |
|---|---|
| API feature | Cohesive endpoint/store/test outcome; found and missing cases; existing-route compatibility; API checks and concrete evidence. |
| Pure relocation | Exact source/destination and import/reference checks; unchanged behavior; no new business logic. |
| Shared contract | Backward-compatible schema deliverable with named consumers and independent migration check; real producer-consumer ordering. A cohesive combined task is also valid if justified. |
| Shared hot file | Shared registry recognized; file conflict or justified merge; no artificial producer-consumer blocker. |
| Missing dependency | Existing identities retained; reader precedes consuming exporter; inferred blocker survives native refresh via effective-graph handling. |
| Discovered cycle | Both prerequisite directions recognized; cycle blocks execution; no invented stub, removed requirement, or silent tracker rewrite. |

For every runnable task, assess requirement coverage, unnecessary fragmentation, context cohesion, dependency correctness, feasible verification, and model-selection rationale. Record task counts and misses rather than optimizing a numeric score. Re-run after material prompt changes; keep prompts separate from scored outputs.

CLI regression tests exercise edge preservation, native-edge union, HITL propagation, cycles, malformed/stale results, explicit edge revision, and tracker-write isolation. They do not evaluate language-model planning quality. A fresh-agent draft run is a smoke evaluation, not a comparison of Sonnet/high against Opus/medium. Calibrate model defaults using representative completed tasks and actual recorded rework, validation, elapsed time, and cost.

## Smoke run, 2026-10-31

One fresh agent used the revised instructions and raw cases, without the rubric or previous outputs. No implementation, live tracker access, or model override was used. Raw drafts are retained in `planning-smoke-results.json`; their verification commands were proposed, not executed.

| Case | Observed result | Review |
|---|---|---|
| API feature | One functional task; 200/404 and existing-route criteria; supplied API command. | Covers requested behavior without separate layer/test tickets. Order representation remains an explicit assumption. |
| Pure relocation | One relocation task; exact old/new paths, imports, package discovery, regression checks. | No new logic. Packaging command is explicitly unknown rather than invented. |
| Shared contract | Three tasks: additive nullable migration, order consumer, invoice consumer; both consumers blocked by migration. | Stable prerequisite and named consumers. Column representation and nullable response details remain unresolved; these drafts are not execution authorization. |
| Shared hot file | Two independent metric tasks with a registry file conflict and no blocker edge. | Correct serialization boundary. Metric semantics and observation prerequisites are explicit unresolved assumptions. |
| Missing dependency | Original reader/exporter identities retained; inferred reader-to-export edge; reader is the dependency-ready root. | Correct producer ordering. Missing currency policy and exact format-v2 output remain unresolved, so dependency readiness alone is insufficient to launch. |
| Discovered cycle | Both directions retained; blocked result, empty ready frontier, explicit resolution required. | No invented stub, silent blocker removal, or tracker rewrite. |

All six produced the intended decomposition/graph decisions. Several synthetic inputs deliberately omit runnable fixtures or exact contract semantics; the drafts expose these gaps and are not claimed to be executable or complete implementations. Deterministic tests separately prove inferred-edge preservation across real fake-GitHub graph refreshes. This run does not establish comparative model quality, latency, or cost.
