# Arena

Compare independent candidate artifacts against a caller-supplied contract. Use the Model selection and Dispatch actions in the skill body.

Copy the checklist before launching.

```markdown
- [ ] Frame
- [ ] Fan out
- [ ] Cross-judge
- [ ] Pick
- [ ] Graft
- [ ] Verify
```

## Phase A: Frame

Every candidate gets the same prompt, so the prompt is the contract.

1. Confirm the artifact contract and runner brief from the caller. Write the task, requirements, and human decisions to `<output-root>/task.md`.
2. Derive 3–6 gradeable criteria from the caller's rubric inputs. Candidates see the task and contract.
3. Resolve the requested runner role and ordered panel count (1–3, default 1). When no role is provided and independent model perspectives are needed, choose distinct supported model families and report unavailable seats. Use Model selection for named pools and fallbacks.
4. Give each candidate an isolated output under `<output-root>/candidate-<n>/` and request a detached worktree through Dispatch for repository reads where possible. A shared checkout is read-only. Pass the task, grounding, candidate brief and output path through Dispatch.

## Phase B: Fan out

Launch the selected runners together through Dispatch. Require each runner to produce the caller's artifact contract and explain the alternatives it rejected where applicable.

After all runners complete, screen candidates against the caller's rules before judging. Record failed or nonviable candidates as dropouts; continue with viable outputs. With none, report failure and stop. With one, read it end to end, score it against the rubric, adopt it as the base, skip Phases C–E, and continue to Verify. If N was greater than one, explicitly report incomplete comparison.

## Phase C: Cross-judge

With at least two viable candidates, after all Phase B candidates complete, choose one model from the `arena cross-judge pool` role in `models.md`. If the value is missing, choose from its fallback. Spawn one read-only judge subagent (`explore`). The judge is never from the parent's family, per Model selection. Try only the entries from another family, in pool order. An `auto` or `inherit-parent` entry is the parent model, so it never judges. With the fallback pool, a Claude parent gets `grok-4.7 xhigh`. A parent from any other family gets `claude-opus-5.5 xhigh` first. If the subagent tool rejects an entry, use a valid effort of the same model at the closest level from the error message, or move to the next entry when there is none. If no entry from another family runs, try the fallback pool's entries from another family the same way. If none of those runs, skip the judge, pick the base alone in Phase D, and say so. If you do not know the parent's model, try the pool's real slugs in pool order and say that the family check did not run. The judge sees the rubric and the candidates by path label, scores each criterion, and recommends a base with rationale. It runs in parallel with your reading in Phase D. Don't spawn it while candidates are still writing.

## Phase D: Pick a base

Read every candidate end to end before picking. Score each against the rubric criterion by criterion, not on holistic feel, and compare with the cross-judge when Phase C ran one. Agreement on the base confirms the pick. Disagreement means one of you is biased or the rubric was ambiguous. Read both rationales before deciding.

Pick the base a future maintainer can extend most easily without breaking invariants. For a design, break ties in favor of the cleaner boundary or smaller API. *Run `principles` skill to load only the engineering principles needed here; read its entire `SKILL.md`, then read each selected Index file in full from that skill's own folder.* Select `Laziness protocol`.

## Phase E: Graft

Walk each losing candidate once more for what is worth porting into the base, usually one or two things per candidate. If the caller requests an evidence union, include every distinct verified finding. Fold each graft in by hand so the result stays coherent under one mental model. *Run `principles` skill to load only the engineering principles needed here; read its entire `SKILL.md`, then read each selected Index file in full from that skill's own folder.* Select `Redesign from first principles`. Don't paste mechanically.

For design candidates, if they converge on one shape, that is strong agreement. Note it and ship the consensus shape. No graft is needed. If design candidates wildly diverge, Phase A was under-specified. Reframe and re-run rather than averaging the divergence.

## Phase F: Verify

Verify the synthesized artifact against the caller's criteria. *Run `principles` skill to load only the engineering principles needed here; read its entire `SKILL.md`, then read each selected Index file in full from that skill's own folder.* Select `Prove it works`. If verification finds a problem the arena missed, either Phase A was wrong (re-frame and re-run) or a candidate caught it and you missed the graft (go back to Phase E). Don't paper over it.

## Re-run for corrections

When the caller supplies a corrected incumbent and requests a rerun, run Phases A–F once more:

- Phase A: the task is the original task plus the corrections as hard constraints; the corrected current design is extra grounding. Rubric adds one criterion per correction. Keep the resolved runner count unless the user changed it.
- Output location: `<output-root>/arena-r<k>/candidate-<n>/`, `k` = re-run number from 1. Never overwrite earlier candidates.
- Phase D–E: the corrected current design joins as the incumbent candidate; scoring includes the corrections criteria, so an incumbent that ignores a correction loses on it.
- Output: the new synthesis under `arena-r<k>/synthesis/`; the incumbent stays untouched until the user picks.

## Outputs

One synthesized artifact matching the caller's contract in `<output-root>/synthesis/`, with a short `synthesis-note.md` alongside naming the base and why, the cross-judge's verdict or that Phase C skipped the judge, each graft with its source candidate, what was rejected and why, any convergence or dropouts, requested and completed runner counts, models and fallbacks used, the reason for any skipped judge, and screening and verification results. With one viable candidate, keep the same artifact contract; record adoption without comparison or grafting.
