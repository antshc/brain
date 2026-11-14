# How

Orchestrate current-system research: frame → discover → trace → verify → explain → deliver. Research selects this route; Hunter executes Explore. Apply Constraints and Caller-owned destinations from the skill body.

## Workflow

1. **Frame.** Preserve the original question, targets/refs, framing, start, outcome, and caller destination. Infer a bounded interpretation when possible; state it so the caller can redirect. *Done when* the question and observable outcome are explicit.
2. **Select depth.** Narrow question → **Concise**, one focused Explore pass. Cross-boundary or complex question → **Detailed**, relevant boundaries, failures, and edge cases. Explicit inspection or verification → **Full** within the requested scope, including runtime-dependent claims or named blockers. Escalate when conflicts or deciding boundaries leave the answer open; depth never implies full-repository coverage. *Done when* depth matches the requested proof.
3. **Discover.** When topology or ownership is unknown, send Hunter a bounded discovery angle using the Explorer prompt: deployables, functional slices, triggers, candidate paths, boundaries. A known narrow target combines discovery and tracing in one pass. *Done when* relevant owners and candidate paths are cited or unresolved.
4. **Plan evidence.** Select Behavior for a deployable's contribution, Flow for cross-deployable handoffs, Data for storage/ownership semantics, or focused checks for an isolated call. Mix only outcome-relevant checks into the same answer. Split independent angles only when useful; sequence dependent checks after discovery. *Done when* each angle has bounded scope, proof checks, and a Hunter Explore request.
5. **Trace.** Fill the Explorer prompt with question, angle, targets/refs, depth, and applicable checks; pass it verbatim as `@work` to Hunter. Use its Evidence return as inline `@outputShape`, preserving caller framing as report context. Follow executing paths, selected providers, data, failures, and handoffs; deepen into restored package implementation when decisive. *Done when* relevant branches have cited outcomes, justified stops, or named gaps.
6. **Verify.** Apply Inspection evidence and runtime checks. Reconcile conflicts and send material source gaps to Hunter as bounded follow-ups. When cloud semantics or live values determine the answer, obtain inline evidence with Cloud inspection's applicable checks. If blocked, retain claim, consequence, blocker, and exact next check. *Done when* every deciding claim has evidence or an explicit limitation.
7. **Explain.** Fill the Explainer prompt with the question, scope/depth, findings, selected presentation guidance, and caller framing. Apply it in the coordinator for concise answers; for detailed/full answers, *load and follow the `subagents` skill to dispatch independent workers using role-based models and isolated outputs* using Dispatch for one read-only general-purpose Explainer. Pass the loaded How report contract. If synthesis delegation is unavailable, apply the prompt to collected evidence in the coordinator. The Explainer returns one draft inline; material gaps return to Verify. *Done when* the draft explains the mechanism without inventing evidence.
8. **Validate and deliver.** Check the draft against How report, render every included Mermaid block, and resolve material defects. Apply Caller-owned destinations: inline unless saving was requested with an explicit destination. A missing destination blocks saving, not evidence collection. *Done when* one cited explanation is delivered or the missing evidence/destination is named.

## Dispatch

Use Research’s Explore request contract. Hunter owns local target resolution, Graphify, NuGet, and read-only enforcement; do not duplicate them. Repository evidence comes only from local checkouts; report missing checkouts/refs as blockers, without remote lookup, clone, or fetch. If Hunter is unavailable, report the blocked evidence request and continue independent work. For a bounded follow-up, send the exact question/check without rebuilding the whole Explorer prompt.

The coordinator owns splitting and dispatch; require neither multiple explorers nor fixed models. Stop when the framed question is answered; leave unrelated branches unexplored.

## Completion criteria

- Each in-scope trigger/branch reaches a cited outcome, a justified stopping boundary, or a gap with consequence and exact next check.
- One explanation integrates deciding Behavior, Flow, Data, and provider findings; static possibilities remain distinct from runtime observations.
- The final delivery follows the caller's framing and destination contract; workers do not write final reports.

Finally, sweep the original question and requested branches against the evidence. Resolve omissions or report them explicitly; do not claim complete inspection with unaccounted scope.
