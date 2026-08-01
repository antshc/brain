# `ralph-dev` — Improvement Suggestions

**Date:** 2026-08-01
**Target:** [plugins/ralph/skills/ralph-dev/SKILL.md](../../plugins/ralph/skills/ralph-dev/SKILL.md)
**Status:** Proposed — not yet applied

Suggested landing order: items 1–7 (correctness) as one change, then 8–10 (safety), then 11–12 (consistency).

## Blocking correctness

### 1. Infinite loop on `partial` outcomes

**Where:** Handle result, `partial` branch (L175)

A `partial` task only gets a comment; the issue stays open, so the next iteration re-selects the same issue with the same priority ranking and repeats the same failing work forever. `blocked` is safe (gets `hitl`, which the step-1 filter excludes) — `partial` is not.

**Fix:** Track attempted issue numbers for the session and exclude them from selection, or escalate to `hitl` after the second `partial` on the same issue.

### 2. `$repo` does not survive into the loop

**Where:** assigned at L24; used at L74 and L159

`repo` is assigned in a setup-phase bash block, but loop step 1 runs from `WORKTREE_PATH` in a different invocation. Combined with `2>/dev/null || echo "[]"`, an unset `$repo` degrades into "no tasks" → the loop exits reporting success while nothing was done.

**Fix:** Declare `repo` as a captured session value alongside `HARNESS_ROOT`/`SOURCE_REPO` (state it explicitly in step 0's output contract), and re-derive it inside the loop block rather than relying on shell persistence.

### 3. Error suppression conflates failure with completion

**Where:** Read state (L74)

`2>/dev/null || echo "[]"` makes auth failures, rate limits, and typo'd milestone titles indistinguishable from an empty backlog — and step 2 treats empty as "all done, exit".

**Fix:** Capture `gh`'s exit code; on non-zero **exit and report the error** instead of falling through to the exit condition.

### 4. TASKS output type flips between array and string

**Where:** Read state (L74)

The trailing `jq 'if length == 0 then "No issues found." else . end'` emits a *string* when empty, but step 1 then instructs "Parse the `TASKS` json array".

**Fix:** Keep the JSON array shape and let step 2 branch on `length == 0`; move the human-readable message to an `echo` outside the JSON.

### 5. Contradictory Codey-unavailable handling

**Where:** L97 vs L109

One line says report `STATUS: blocked` (stop); the next says synthesize a blocked report and continue to step 5. An agent will pick either.

**Fix:** Keep only the continue-to-step-5 path — it preserves work and routes the issue to `hitl`, which is the stated intent.

### 6. "ONE TASK ONLY" contradicts the orchestrator loop

**Where:** L224 vs L64 and L197

The RULES section caps the skill at one task per invocation, while the loop repeats until the milestone is empty and only then opens a PR. The frontmatter description ("picks the next open issue") sides with the rule.

**Fix:** Decide one. If the loop is intended, reword the rule to "one task per *iteration*, sequentially" and align the frontmatter description.

### 7. `$branch` vs `$BRANCH`

**Where:** L201, L217

Step 3 captures `BRANCH`; the PR section reads `$branch`. Also `<spec-title>` in the PR title is never defined anywhere (only `Feature ID` and `Target Branch` are extracted).

**Fix:** Use `$BRANCH` throughout and define `<spec-title>` explicitly (milestone title, or the `spec` issue title fetched in step 7).

## Operational safety

### 8. Unscoped `git add -A` + bare `git push` in the harness root

**Where:** Commit harness root (L184–L191)

"Stage **any** change in the harness root" will sweep up unrelated in-progress user work — scratch files, half-finished edits, local config — and push it. This is the one step operating in the user's live checkout rather than an isolated worktree, so it deserves the tightest scoping, not the loosest.

**Fix:** Scope to the artifacts this loop actually writes (Gotchas/memory files), and emit `git status --short` before committing so the diff is visible in the transcript.

### 9. No push-rejection path

**Where:** Publish non-empty progress (L147)

`ralph-fix` states "If `git push` to the PR branch is rejected, stop and report"; `ralph-dev` has no equivalent, so a rejected push silently precedes issue closure — the issue gets closed with unpublished work.

**Fix:** Add the same stop-and-report rule, placed before step 8.

### 10. Spec body rewrite via `--body`

**Where:** Update spec (L167); same class of problem at L74 and L159

Passing a full multi-paragraph issue body as a shell-quoted argument breaks on backticks, `$`, and embedded quotes — and can silently truncate. Milestone titles containing `:` or quotes hit the same issue.

**Fix:** Write the body to a temp file and use `gh issue edit --body-file`; store the milestone title in a quoted variable rather than inlining the placeholder. Also state what to do when `## Implementation Decisions` is absent (create the section).

## Consistency with repo conventions

### 11. No checklist workflow

The file has 3 setup steps plus 9 loop steps, all order-sensitive and resumable, which is squarely the case [Checklist-Driven Workflow](../concepts/0005-checklist-workflow.md) prescribes; the concept's exception clause even says the Codey/Chorey/Ralph family should embed one for uniformity. `codey.agent.md` has one, `ralph-dev` does not.

**Fix:** Add `Copy this checklist and check off items as you complete them:` with a fenced `Ralph Dev Progress:` checklist covering setup plus the loop steps, per the concept's minimal template.

### 12. Chorey's STATUS overriding Codey's `complete`

**Where:** Combine outcomes (L128 onward)

A `blocked` Chorey (a *refactor* review) currently downgrades a successfully implemented task to `hitl`. That may be intended, but it is a real design decision buried in one clause.

**Fix:** State the rationale inline, or restrict Chorey's influence to `complete`/`partial` and let a blocked Chorey degrade to `partial`.
