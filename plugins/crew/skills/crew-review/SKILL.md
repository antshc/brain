---
name: crew-review
description: Behavior-preserving cleanup review — reviews a commit (when the caller supplies BASELINE_COMMIT) or uncommitted work for refactor candidates, applies only safe fixes, and reports the rest as findings without touching them. Apply during Chorey's REVIEW step.
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

**`BASELINE_COMMIT` absent** → gather every uncommitted change in the workspace (staged and unstaged). Before changing any file, record its exact current content so it can be restored verbatim.

**Emit**: "Reviewing commit <sha>: [files]", "Reviewing uncommitted files: [list]", or "No work to review."

## 1. Review

`CHORE_PATH` resolved by the agent during INPUT → follow that `CHORE.md`'s review rules; emit "Review rules: CHORE.md". Unresolved → review under the **Hard rules** below only; emit "Review rules: none".

`CODE_PATH` resolved → read it in full; every fix you apply must obey its conventions, and a cleanup that would violate one is a finding, not an edit. Emit "Style rules: CODE.md | none".

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
