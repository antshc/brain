---
name: crew-review
description: Behavior-preserving cleanup review — reviews a commit (when the caller supplies BASELINE_COMMIT) or uncommitted work for refactor candidates, applies only safe fixes, and reports the rest as findings without touching them. Apply during Chorey's REVIEW step.
---

# Review

Copy this checklist and check off items as you complete them:
```
Review Progress:
- [ ] Step 0: Identify the change set to review and establish a revert baseline
- [ ] Step 1: Review for behavior-preserving cleanup (CHORE.md if resolved, else no rules file)
- [ ] Step 2: Apply safe fixes; record unsafe candidates as findings without touching them
```

## Step 0: Identify the change set and establish a revert baseline

**`BASELINE_COMMIT` supplied**: identify the files that commit changed (e.g. `git show --stat <BASELINE_COMMIT>`). No manual snapshot is needed — the commit itself is the exact pre-review state; **Revert** restores against it directly.

**`BASELINE_COMMIT` absent**: gather every uncommitted change already in the workspace (staged and unstaged) — whatever uncommitted work already exists when Chorey runs standalone with no baseline commit. Before changing any file, record its exact current content (e.g. a diff or copy) so it can be restored verbatim later if verification fails.

**Emit**: "Reviewing commit <sha>: [files]", "Reviewing uncommitted files: [list]", or "No work to review."

## Step 1: Review

Use the optional `CHORE_PATH` value resolved by the agent during INPUT. When it is resolved, follow that `CHORE.md`'s review rules; emit "Review rules: CHORE.md". When it is unresolved, review without a rules file, applying only the **Hard rules** below; emit "Review rules: none".

Review every file identified in Step 0 for behavior-preserving cleanup candidates only — never a behavior change, a new feature, or a scope expansion beyond cleanup.

## Step 2: Apply safe fixes; record unsafe candidates as findings

For each candidate found in Step 1:
- **Safe to apply** (the fix is unambiguous and provably behavior-preserving) → apply it.
- **Not safe to apply** (ambiguous intent, risks a behavior change, or requires a decision only a human or Codey should make) → leave the file untouched and record it as a finding instead.

**Emit**: "Applied: [list of files changed] or 'none'. Findings (not applied): [list or 'none']."

### No changes made

If this step applies zero fixes, do not proceed to a Verify phase — the previously verified result already stands untouched. The caller reports this directly; re-running verification over an unchanged tree is unnecessary.

## Revert (used by the caller when its own Verify phase fails)

If verification of the changes this skill applied cannot be made to pass within the caller's retry cap, or hits an environment blocker, restore every file this skill touched to its pre-review state:

- **`BASELINE_COMMIT` supplied**: run `git checkout <BASELINE_COMMIT> -- <file>` per touched file to restore its exact content; delete any file this skill created that didn't exist at that commit.
- **`BASELINE_COMMIT` absent**: restore each file to the content recorded in its Step 0 snapshot (delete any file this skill created new).

Either way, move each discarded change from "Applied" into "Findings" in the caller's report. Never leave the workspace in a state the caller cannot account for.

## Hard rules

- Never touch a file solely to record a finding — findings are informational only.
- Only apply a refactor that provably preserves behavior; anything else belongs in Findings, not in an edit.
- When `BASELINE_COMMIT` is absent, snapshot a file's exact pre-review content before editing it, so **Revert** can restore it verbatim; when supplied, the commit itself already is that snapshot.
