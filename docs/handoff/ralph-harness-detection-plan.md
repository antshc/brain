# Plan: Harden ralph-harness with new detection logic

## TL;DR
Keep the `ralph-harness` skill (do not remove it) and strengthen its
resolution logic in place. Replace the current blind `HARNESS_ROOT=$(pwd)`
trust with a validated block that fails closed when cwd is not a genuine,
initialized Harness Root:
- requires the Ralph-install marker `.github/agents/codey.agent.md`
- rejects any path containing `.worktrees/` (a worktree of the same repo,
  which would also carry that marker in the no-`workspace/` topology)

This closes the gap where a mis-resolved `HARNESS_ROOT` could silently
`git add -A / commit / push` (ralph-dev step 9) into the wrong repo/branch.
Because the logic stays centralized in `ralph-harness`, its 3 callers
(`ralph-dev`, `ralph-fix`, `ralph-worktree`) need **no changes** — they keep
invoking `/ralph-harness` exactly as today.

## New resolution logic for ralph-harness/SKILL.md

Replace the current body:
```bash
HARNESS_ROOT=$(pwd)
src_git=$(find "$HARNESS_ROOT/workspace" -maxdepth 2 -name .git -type d 2>/dev/null | head -n1)
if [ -n "$src_git" ]; then
  SOURCE_REPO=$(dirname "$src_git")
else
  SOURCE_REPO=$HARNESS_ROOT
fi
```
with:
```bash
HARNESS_ROOT=$(pwd)
if [ ! -f "$HARNESS_ROOT/.github/agents/codey.agent.md" ]; then
  echo "Refusing: $HARNESS_ROOT is not a Ralph Harness Root (missing .github/agents/codey.agent.md)"
  exit 1
fi
case "$HARNESS_ROOT" in
  */.worktrees/*) echo "Refusing: HARNESS_ROOT resolved into a worktree path ($HARNESS_ROOT)"; exit 1 ;;
esac
src_git=$(find "$HARNESS_ROOT/workspace" -maxdepth 2 -name .git -type d 2>/dev/null | head -n1)
if [ -n "$src_git" ]; then
  SOURCE_REPO=$(dirname "$src_git")
else
  SOURCE_REPO=$HARNESS_ROOT
fi
```

Add a short note above the block documenting why the two guards exist (marker
= confirms an initialized Harness Root; `.worktrees/` exclusion = a worktree
of the same repo would otherwise also pass the marker check when there's no
`workspace/` folder).

## Steps

1. Update [ralph-harness/SKILL.md](../../plugins/ralph/skills/ralph-harness/SKILL.md) — replace the resolution block with the hardened version above; keep the existing "Output" section (`HARNESS_ROOT` / `SOURCE_REPO` report) unchanged.
2. No changes to [ralph-dev/SKILL.md](../../plugins/ralph/skills/ralph-dev/SKILL.md), [ralph-fix/SKILL.md](../../plugins/ralph/skills/ralph-fix/SKILL.md), or [ralph-worktree/SKILL.md](../../plugins/ralph/skills/ralph-worktree/SKILL.md) — they already just say "Invoke the `/ralph-harness` skill," and the hardening is transparent to them (same output contract: `HARNESS_ROOT`, `SOURCE_REPO`).
3. No changes to `ralph-init/SKILL.md` or `plugins/ralph/README.md` — `ralph-harness` stays in the install list and skills table as-is.

This is a single-file change; no phased grouping needed.

## Relevant files
- `plugins/ralph/skills/ralph-harness/SKILL.md` — only file touched, replace resolution block body

## Verification
1. Manually trace `/ralph-harness` with `pwd` set to: (a) a proper initialized Harness Root → resolves `HARNESS_ROOT`/`SOURCE_REPO` and reports normally; (b) a directory without `.github/agents/codey.agent.md` → exits with the "not a Ralph Harness Root" message; (c) a `<repo>.worktrees/<branch>` path → exits with the "resolved into a worktree path" message.
2. Re-run `/ralph-dev`, `/ralph-fix`, `/ralph-worktree` end to end (or trace their step 0 sections) to confirm they still receive `HARNESS_ROOT`/`SOURCE_REPO` from `/ralph-harness` unchanged — the guard is purely additive/fail-closed, no output contract change.
3. `grep -rn "ralph-harness" plugins/ralph/` — confirm all 3 caller references and the README/ralph-init entries are untouched (no accidental removal).

## Decisions
- Detection strengthening is a **guard/validation** on the invocation `cwd`,
  not an ancestor-walk discovery — preserves the existing `Harness Root`
  definition ("the repository the loop is invoked from"). Included: marker
  check (`.github/agents/codey.agent.md`) + `.worktrees/` path exclusion.
  Excluded: ancestor walk-up, `.git`-file-vs-directory check (redundant once
  `.worktrees/` path exclusion is in place).
- `ralph-harness` remains the single owner of this resolution logic — reverses
  the earlier direction (removing the skill and inlining into 3 callers).
  Centralizing here means future changes to the resolution rule are edited
  once, not duplicated across 3 files.

## Further Considerations
1. `TEST_PLAN.md`'s "Deterministic Source Repository development" scenarios
   reference `prepare_worktree.sh`/`resolve_source_repository.sh`, scripts
   that no longer exist (ralph-worktree is markdown-only now) — pre-existing
   drift, out of scope here. Optionally add 2 new scenarios covering the
   marker/worktree-path guard for explicit regression coverage — recommend
   skipping unless you want that safety net formalized in tests.
