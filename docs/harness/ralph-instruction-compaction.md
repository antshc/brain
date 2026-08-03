# Ralph Plugin — Instruction Compaction Suggestions

**Date:** 2026-08-03
**Scope:** `plugins/ralph` — 569 lines across 4 skills + README

The mechanics are sound. The bulk is **restatement** — facts owned by one file repeated in two or three others. Suggestions ordered by payoff.

---

## S1 — Delegate harness resolution instead of restating it (~14 lines)

`dev/SKILL.md` step 0 and `fix/SKILL.md` Setup step 1 each spell out the same four fallback branches, all of which are already specified in `plugins/harness/skills/resolve-harness/SKILL.md` ("Callers already define the fallback…" — but the callers shouldn't have to).

Replace both blocks with:

```
Run `/resolve-harness` from cwd; retain the emitted `KEY=value` lines as `HARNESS_SETTINGS`.
Unavailable or empty `HARNESS_REPO_PATH` → use cwd for `HARNESS_REPO_PATH` and `CODEBASE_REPO_PATH`. Non-zero exit → **exit** and report.
```

**Reasoning:** three copies of one contract means three places to update and two chances to drift. The two copies already disagree — `fix` handles a missing `CODEBASE_REPO_PATH` separately, `dev` doesn't.

---

## S2 — Worktree lifecycle facts stated 5 times (~10 lines)

"The `/create-worktree` skill creates the worktree in `CODEBASE_REPO_PATH`" appears in both callers. "Removes the local worktree and local branch only, remote untouched" appears in `delete-worktree` Rules, `fix` Cleanup, `fix` Rules, and `dev` CLEANUP WORKTREE.

Keep it once, in `delete-worktree`. Callers just invoke:

```
/delete-worktree $CODEBASE_REPO_PATH $WORKTREE_PATH $branch
```

**Reasoning:** a callee's guarantees belong in the callee. The caller only needs to know *when* to call it, which is already implied by section position.

---

## S3 — `dev`'s RULES section is ~70% a re-run of the body (~14 lines)

Six of nine rules restate a step verbatim:

| Rule | Already stated in |
|---|---|
| CHOREY NEVER CHANGES THE RECORDED OUTCOME | step 6 + step 8 |
| CODEY'S CHECKPOINT LANDS BEFORE CHOREY | step 5 + step 6 |
| HARNESS ROOT COMMIT & PUSH RUNS ONCE | COMMIT & PUSH HARNESS REPO |
| `partial` TWICE → `hitl` | step 8 |
| NEVER IMPLEMENT `spec`/`hitl` | step 1 blockquote |
| ALL WORK INSIDE THE WORKTREE | step 3 |

Only **ONE TASK AT A TIME**, **re-read state**, **exit conditions**, and **ITERATION CAP** are load-bearing invariants not derivable from a single step. Keep those four; delete the rest.

**Reasoning:** a rules block earns its place by holding cross-cutting invariants the agent can't see from any one step. Duplicated rules train the agent to skim the section, which weakens the invariants that *are* unique.

---

## S4 — Chorey's gate is written twice, inverted (~3 lines)

`dev` step 6 states the run condition, then immediately states its own negation as the skip condition. Collapse to:

```
Run only when Codey's STATUS is **complete** and `chorey` is available; otherwise continue to **Handle task result**.
```

Same pattern in step 7.

---

## S5 — README copies both agent prompt templates verbatim (~20 lines)

`plugins/ralph/README.md` reproduces the Codey and Chorey prompts that live in `dev/SKILL.md` steps 3 and 6, plus the Chorey skip rules and the STATUS-precedence rule.

Reduce the README to the skills table plus one line per agent (role + where it's defined + which step invokes it). Link to the step; don't mirror it.

**Reasoning:** the README isn't read at execution time, so a stale copy costs maintenance with zero runtime benefit — the worst duplication trade.

---

## S6 — Fold repeated failure handling into one rule (~6 lines)

"If X fails, **exit** and report the error" appears seven times in `dev`. Replace with a single RULES entry:

```
Any failed skill invocation, `git push`, or `gh` call → **exit** and report the error.
```

Keep the inline form only where behavior differs (e.g. `delete-worktree` failure is explicitly non-fatal).

---

## S7 — `fix` setup micro-compaction (~5 lines)

Two `gh pr view` calls fetch one object; use one:

```bash
eval "$(gh pr view <number> --repo <owner>/<repo> --json headRefName,baseRefName \
  -q '"branch=\(.headRefName)\ntarget_branch=\(.baseRefName)"')"
```

Also drop `"prefix"` from the documented thread schema — the skill never reads it, so it's context spent on a field the agent must then decide to ignore.

---

## S8 — Trim explanatory asides in `dev` step 1 (~4 lines)

The two paragraphs justifying why `repo` is resolved once and reused compress to:

```
`repo` resolves the harness remote (tasks live there) and is reused for all harness-repo commands below.
```

---

## S9 — `plugin.json` description is stale

`"ralph AFK PR review automation skills."` describes only `/fix`.

Suggested: `"AFK autonomous development loop and PR review-comment automation."`

---

## S10 (optional) — Apply Progressive Disclosure to `dev`

After S1–S8, `dev/SKILL.md` lands around ~215 lines — within the ~500-line budget of `docs/concepts/0006-progressive-disclosure.md`, so no split is required. If it grows again, the natural cut is the post-loop tail (**Create Pull Request**, **Commit & Push Harness Repo**, **Cleanup**) into `references/finalize.md` — it runs once per invocation, not per iteration.

---

## Projected effect

| File | Now | After | Δ |
|---|---|---|---|
| `dev/SKILL.md` | 289 | ~215 | −26% |
| `fix/SKILL.md` | 96 | ~78 | −19% |
| `README.md` | 55 | ~30 | −45% |
| `delete-worktree/SKILL.md` | 31 | 31 | — (becomes the single source) |
| `create-worktree/SKILL.md` | 98 | 98 | — |
| **Total** | **569** | **~450** | **−21%** |

**No behavioral risk:** S1–S6, S9.
