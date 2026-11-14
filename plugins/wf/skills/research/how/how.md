# How

Route procedure for current-system research: frame → discover → trace → verify → explain → deliver. Spawns `hunty` for evidence and `explainy` for Detailed/Full explanations. Graphify and NuGet are `hunty` tactics.

## Conditional resources

Read triggered resources in full; pass the ones a worker needs as absolute paths in its brief.

| Trigger | Resource |
|---|---|
| Every How run | `how/inspection.md`, `how/explorer-prompt.md` |
| Detailed or Full depth | `how/report.md` (pass to `explainy`) |
| Checks one deployable's triggers, implementation, outcomes | `how/behavior.md` |
| Checks cross-deployable handoffs/contracts/terminals | `how/flow.md` |
| Checks data shape, keys, ownership, consistency, migration, concurrency, retention | `how/data.md` |
| Restored NuGet API/implementation evidence | `how/nuget.md` (`hunty` loads it) |
| Relationship lookup or direct graph query/path/explain | `how/graphify.md` (`hunty` loads it) |
| Caller needs system question examples | `how/README.md` |

## Workflow

1. **Frame.** Start from the router's Frame: rephrased question, glossary terms, resolved targets, Deployables/boundaries, and graph coverage. Preserve the original question, targets/refs, framing, start, outcome, and requested destination. Infer a bounded interpretation when possible; state it so the requester can redirect. *Done when* the question and observable outcome are explicit.
2. **Select depth.** Narrow question → **Concise**, one focused pass. Cross-boundary or complex question → **Detailed**, relevant boundaries, failures, and edge cases. Explicit inspection or verification → **Full** within the requested scope, including runtime-dependent claims or named blockers. Escalate when conflicts or deciding boundaries leave the answer open; depth never implies full-repository coverage. *Done when* depth matches the requested proof.
3. **Discover.** When topology or ownership is unknown, spawn `hunty` with a bounded discovery angle in the Explorer prompt: deployables, functional slices, triggers, candidate paths, boundaries. A known narrow target combines discovery and tracing in one pass. *Done when* relevant owners and candidate paths are cited or unresolved.
4. **Plan evidence.** Select Behavior for a deployable's contribution, Flow for cross-deployable handoffs, Data for storage/ownership semantics, or focused checks for an isolated call. Mix only outcome-relevant checks into the same answer. Split independent angles only when useful; sequence dependent checks after discovery. *Done when* each angle has bounded scope, proof checks, and a `hunty` brief.
5. **Trace.** Fill the Explorer prompt with question, angle, targets/refs, depth, and applicable checks; pass it as `@work` in the `hunty` Brief, asking for the Evidence return and preserving requested framing as report context. Spawn independent angles in one parallel batch. Follow executing paths, selected providers, data, failures, and handoffs; deepen into restored package implementation when decisive. *Done when* relevant branches have cited outcomes, justified stops, or named gaps.
6. **Verify.** Apply Inspection evidence and runtime checks. Reconcile conflicts; send material source gaps to a fresh `hunty` as bounded follow-ups with the exact question/check. When cloud semantics or live values determine the answer, obtain inline evidence by running the Cloud route for that part. If blocked, retain claim, consequence, blocker, and exact next check. *Done when* every deciding claim has evidence or an explicit limitation.
7. **Explain.** Concise → apply `agents/explainy.md` to the collected evidence yourself. Detailed/Full → fill `agents/explainy.md` with the question, scope/depth, findings, selected presentation guidance, and requested framing; spawn one `explainy` with How report. The draft returns inline; material gaps return to Verify. *Done when* the draft explains the mechanism without inventing evidence.
8. **Validate and deliver.** Check the draft against How report, render every included Mermaid block, and resolve material defects. Apply Delivery. *Done when* the report pointer is returned with its status.

## Evidence rules

The router's Frame owns target resolution, contract discovery, and graph coverage (including worktree → main checkout); pass it as `@frame` in every `hunty` Brief. `hunty` owns the target checkout's own contracts, Graphify, NuGet, and read-only enforcement; do not duplicate them in briefs. Repository evidence comes only from local checkouts; report missing checkouts/refs as blockers, without remote lookup, clone, or fetch. The router owns splitting; require neither multiple workers nor fixed models. Stop when the framed question is answered; leave unrelated branches unexplored.

Graph build, update, or export requests → report the build entry point named in `<root>/GRAPHIFY.md`; never build.

## Completion criteria

- Each in-scope trigger/branch reaches a cited outcome, a justified stopping boundary, or a gap with consequence and exact next check.
- One explanation integrates deciding Behavior, Flow, Data, and provider findings; static possibilities remain distinct from runtime observations. Each Detailed/Full explanation follows How report.
- Codebase targets covered by a graph, including worktrees via their main checkout, record `hunty` graph commands or skip reasons.

Finally, sweep the original question and requested branches against the evidence. Resolve omissions or report them explicitly; do not claim complete inspection with unaccounted scope.
