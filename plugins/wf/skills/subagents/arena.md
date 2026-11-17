# Arena

Compare independent candidate artifacts against a caller-supplied contract. For runner roles, panels, and the judge, apply Model selection and Ordered panels from the skill body.

**Launch rules.** Spawn runners as skill-capable `general-purpose` workers, together in the background, each with its own output path. Collect every terminal result or blocker with its model, artifact path, and worktree path. Runners never start Arena or spawn subagents.

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

Give every candidate the same prompt.

1. Confirm the artifact contract and runner brief from the caller. Write the task, requirements, and human decisions to `<output-root>/task.md`.
2. Derive 3–6 gradeable criteria from the caller's rubric inputs. Candidates see the task and contract.
3. Resolve the requested runner role and ordered panel count (1–3, default 1). When no role is provided and independent model perspectives are needed, choose distinct supported model families and report unavailable seats. Use Model selection and Ordered panels for named pools and fallbacks.
4. Give each candidate an isolated output under `<output-root>/candidate-<n>/` and *Load and follow the `git` skill to run worktree lifecycle and creation* using Worktrees for one detached worktree per candidate where possible. A shared checkout is read-only. Pass the task, grounding, candidate brief and output path in each runner brief.

## Phase B: Fan out

Launch the selected runners per Launch rules. Require each runner to produce the caller's artifact contract and explain the alternatives it rejected where applicable.

After all runners complete, screen candidates against the caller's rules before judging. Record failed or nonviable candidates as dropouts; continue with viable outputs. With none, report failure and stop. With one, read it end to end, score it against the rubric, adopt it as the base, skip Phases C–E, and continue to Verify. If N was greater than one, explicitly report incomplete comparison.

## Phase C: Cross-judge

After all runners complete, cross-judge only with at least two viable candidates. Select from the configured `arena cross-judge pool`, then its fallback, in order, filtering for another vendor than the parent. Treat `claude-fable-*` and `claude-*` as the same vendor; `auto`/`inherit-parent` means the parent and cannot judge. Unknown parent/vendor → report that independence cannot be established and skip the judge.

Apply Model selection and Ordered panels rejection handling from the skill body, preserving the other-vendor filter on every fallback. Never fall back to the parent for judging. No eligible supported model → skip the judge, report the gap and pick the base yourself. Otherwise spawn one read-only judge (`explore`) with rubric and candidates by path label. While you read in Phase D, it scores each criterion and recommends a base with rationale. Never launch it while candidates are writing.

## Phase D: Pick a base

Read every candidate end to end before picking. Score each against the rubric criterion by criterion, not on holistic feel, and compare with the cross-judge when Phase C ran one. Disagreement means one of you is biased or the rubric was ambiguous. Read both rationales before deciding.

Pick the base a future maintainer can extend most easily without breaking invariants. For a design, break ties in favor of the cleaner boundary or smaller API. *Load and follow the `principles` skill to load `Laziness protocol` and apply it to the base pick.*

## Phase E: Graft

Walk each losing candidate once more for what is worth porting into the base, usually one or two things per candidate. If the caller requests an evidence union, include every distinct verified finding. Fold each graft in by hand so the result stays coherent under one mental model. *Load and follow the `principles` skill to load `Redesign from first principles` and apply it to each graft.*

For design candidates, if they converge on one shape, that is strong agreement. Note it and ship the consensus shape. No graft is needed. If design candidates wildly diverge, Phase A was under-specified. Reframe and re-run rather than averaging the divergence.

## Phase F: Verify

Verify the synthesized artifact against the caller's criteria. *Load and follow the `principles` skill to load `Prove it works` and apply it to this verification.* If verification finds a problem the arena missed, either Phase A was wrong (re-frame and re-run) or a candidate caught it and you missed the graft (go back to Phase E). Don't paper over it.

## Re-run for corrections

When the caller supplies a corrected incumbent and requests a rerun, run Phases A–F once more:

- Phase A: the task is the original task plus the corrections as hard constraints; the corrected current design is extra grounding. Rubric adds one criterion per correction. Keep the resolved runner count unless the user changed it.
- Output location: `<output-root>/arena-r<k>/candidate-<n>/`, `k` = re-run number from 1. Never overwrite earlier candidates.
- Phase D–E: the corrected current design joins as the incumbent candidate; scoring includes the corrections criteria, so an incumbent that ignores a correction loses on it.
- Output: the new synthesis under `arena-r<k>/synthesis/`; the incumbent stays untouched until the user picks.

## Outputs

One synthesized artifact matching the caller's contract in `<output-root>/synthesis/`, with a short `synthesis-note.md` alongside naming the base and why, the cross-judge's verdict or that Phase C skipped the judge, each graft with its source candidate, what was rejected and why, any convergence or dropouts, requested and completed runner counts, models and fallbacks used, the reason for any skipped judge, and screening and verification results. With one viable candidate, keep the same artifact contract; record adoption without comparison or grafting.
