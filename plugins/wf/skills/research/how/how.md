# How

Route procedure for current-system research: frame → discover → trace → verify → explain → deliver. Spawns the registered `codebase` agent for evidence; writes the explanation itself.

## Conditional resources

Read triggered resources in full; pass the ones a worker needs as absolute paths in its brief.

| Trigger | Resource |
|---|---|
| Every How run | `how/inspection.md`, `how/explorer-prompt.md` |
| Every How run, at Explain | `how/report.md` |
| Checks one deployable's triggers, implementation, outcomes | `how/behavior.md` |
| Checks cross-deployable handoffs/contracts/terminals | `how/flow.md` |
| Checks data shape, keys, ownership, consistency, migration, concurrency, retention | `how/data.md` |

## Workflow

1. **Frame.** Start from the router's Frame: rephrased question, glossary terms, resolved targets, and Deployables/boundaries. Preserve the original question, targets/refs, framing, start, outcome, and requested destination. Infer a bounded interpretation when possible; state it so the requester can redirect. *Done when* the question and observable outcome are explicit.
2. **Select depth.** Narrow question → **Concise**, one focused pass. Cross-boundary or complex question → **Detailed**, relevant boundaries, failures, and edge cases. Explicit inspection or verification → **Full** within the requested scope, including runtime-dependent claims or named blockers. Escalate when conflicts or deciding boundaries leave the answer open; depth never implies full-repository coverage. *Done when* depth matches the requested proof.
3. **Discover.** When topology or ownership is unknown, spawn `codebase` with a bounded discovery angle in the Explorer prompt: deployables, functional slices, triggers, candidate paths, boundaries. A known narrow target combines discovery and tracing in one pass. *Done when* relevant owners and candidate paths are cited or unresolved.
4. **Plan evidence.** Select Behavior for a deployable's contribution, Flow for cross-deployable handoffs, Data for storage/ownership semantics, or focused checks for an isolated call. Mix only outcome-relevant checks into the same answer. Split independent angles only when useful; sequence dependent checks after discovery. *Done when* each angle has bounded scope, proof checks, and a `codebase` brief.
5. **Trace.** Fill the Explorer prompt with question, angle, targets/refs, depth, and applicable checks; pass it as the `codebase` agent's task, asking for the Evidence return and preserving requested framing as report context. Spawn independent angles in one parallel batch. Follow executing paths, selected providers, data, failures, and handoffs; deepen into restored package implementation when decisive. *Done when* relevant branches have cited outcomes, justified stops, or named gaps.
6. **Verify.** Apply Inspection evidence and runtime checks. Reconcile conflicts; send material source gaps to a fresh `codebase` as bounded follow-ups with the exact question/check. When cloud semantics or live values determine the answer, obtain inline evidence by running the Web route for that part. If blocked, retain claim, consequence, blocker, and exact next check. *Done when* every deciding claim has evidence or an explicit limitation.
7. **Explain.** Apply How report to the evidence with the selected lens's Presentation guidance (Flow across two or more deployables → `how/flow.md` Presentation) and the requested framing. Material gaps return to Verify. *Done when* the draft explains the mechanism without inventing evidence.
8. **Present.** Check the draft against How report checks and render every Mermaid block; gaps return to Verify. Apply Delivery. *Done when* the report pointer is returned with its status.

## Evidence rules

Pass the router's Frame with every `codebase` task. The `codebase` agent owns the target checkout's contracts, multi-repo search, NuGet, and read-only enforcement; do not duplicate them in briefs. Repository evidence comes only from local checkouts; report missing checkouts/refs as blockers, without remote lookup, clone, or fetch. The router owns splitting; require neither multiple workers nor fixed models. Stop when the framed question is answered; leave unrelated branches unexplored.

## Completion criteria

- Each in-scope trigger/branch reaches a cited outcome, a justified stopping boundary, or a gap with consequence and exact next check.
- One explanation integrates deciding Behavior, Flow, Data, and provider findings; static possibilities remain distinct from runtime observations. Each explanation follows How report.

Finally, sweep the original question and requested branches against the evidence. Resolve omissions or report them explicitly; do not claim complete inspection with unaccounted scope.
