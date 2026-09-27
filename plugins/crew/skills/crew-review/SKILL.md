---
name: crew-review
description: "Inspect a commit or uncommitted changes for behavior-preserving cleanup, apply safe refactors, and report uncertain candidates as findings. Use during Chorey's REVIEW step; Chorey owns verification."
---

# Review

Copy this checklist and check off each item as you complete it:

```
- [ ] 0 Identify the change set and establish a revert baseline
- [ ] 1 Review for behavior-preserving cleanup
- [ ] 2 Apply safe fixes; record unsafe candidates as findings
```

## 0. Identify the change set and establish a revert baseline

**`BASELINE_COMMIT` supplied** → identify the files that commit changed (`git show --stat <BASELINE_COMMIT>`). The commit itself is the pre-review state; **Revert** restores against it directly — no snapshot needed.

**`BASELINE_COMMIT` absent** → gather every uncommitted change in the workspace yourself, by running your own git commands (e.g. `git status --porcelain`, `git diff`). Cover staged, unstaged, and untracked files. Before changing any file, record its exact current content so it can be restored verbatim.

**Emit**: "Reviewing commit <sha>: [files]", "Reviewing uncommitted files: [list]", or "No work to review."

## 1. Review

Run `python3 <skill-directory>/scripts/match_changed_files.py <changed-file> ...` on Step 0's files before applying cleanup. Its JSON maps each Stack to its matching paths; an empty change set returns `{}`. The helper's `review_scopes.json` owns file patterns independently of the agents' task-routing descriptions and validates the installed roster. A helper error stops review before edits and is reported to the caller.

If the helper returns no matching Stack, emit "Chorey not configured: no matching chore rules skill." and stop before applying cleanup. For every matching Stack, require `$HARNESS_REPO_PATH/.github/skills/chore-<stack>-rules/SKILL.md`. If any required rules skill is missing, emit "Chorey not configured: missing [paths]." and stop before applying cleanup. Otherwise, load every matching rules skill; several Stacks can match one file, so apply each and report conflicts as findings. Review only files mapped to the configured skills; leave unmatched files untouched. Emit "Review rules: [list of chore-<stack>-rules skill paths applied]."

Read Copilot instructions applicable to every changed file and follow observed neighboring conventions; a cleanup that would violate either is a finding, not an edit. Emit "Style rules: [applicable instruction paths] | observed conventions".

Review every file from Step 0 for behavior-preserving cleanup candidates only — never a behavior change, a new feature, or scope beyond cleanup.

## 2. Apply safe fixes; record unsafe candidates as findings

For each candidate:

- **Safe** (unambiguous and provably behavior-preserving) → apply it.
- **Not safe** (ambiguous intent, risks behavior change, or needs a human/Codey decision) → leave the file untouched, record a finding.

**Emit**: "Applied: [list of files changed] or 'none'. Findings (not applied): [list or 'none']."

Zero fixes applied → do not proceed to a Verify phase; the previously verified result stands untouched and the caller reports that directly.

## Revert (used by the caller when its own Verify phase fails)

When verification of the applied changes cannot pass within the caller's retry cap, or hits an environment blocker, restore every file this skill touched:

- **`BASELINE_COMMIT` supplied** → `git checkout <BASELINE_COMMIT> -- <file>` per touched file; delete any file created that didn't exist at that commit.
- **`BASELINE_COMMIT` absent** → restore each file from its Step 0 snapshot; delete any file created new.

Either way, move each discarded change from "Applied" into "Findings" in the caller's report. Never leave the workspace in a state the caller cannot account for.

## Hard rules

- Never touch a file solely to record a finding — findings are informational only.
- Only apply a refactor that provably preserves behavior; anything else is a finding, not an edit.
- When `BASELINE_COMMIT` is absent, snapshot a file's exact pre-review content before editing it.
