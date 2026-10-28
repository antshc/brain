# Finalize

App-verification evidence, publication read-back, and spec closure gates.

## Verification evidence

Set `EVIDENCE_ROOT` = `HARNESS_ROOT/workspace/REPO.evidence` (sibling of `SOURCE_ROOT`, git-ignored with `workspace/`) and `EVIDENCE_DIR` = `EVIDENCE_ROOT/INITIATIVE_ID/<short HEAD sha>` (HEAD at verification start; the verifier writes `round-N` subfolders inside). Confirm the path stays under `EVIDENCE_ROOT`; create it with `mkdir -p`; never overwrite an existing directory (append a numeric suffix). Evidence survives worktree removal; never delete it.

| Purpose | Command |
|---|---|
| Post verdict on spec | `gh issue comment SPEC_NUMBER --repo TRACKER_REPOSITORY --body-file VERDICT_FILE` |
| Read back | `gh api repos/TRACKER_REPOSITORY/issues/SPEC_NUMBER/comments/COMMENT_ID` |

Write `VERDICT_FILE` outside the repository and copy it to `EVIDENCE_DIR/verdict.md`. Terse content: final verdict, verified head commit, PR URL, table of check, result, detail, evidence path, fix rounds (fix commit, findings fixed or unfixed, each round's evidence dir), then skipped checks with errors and the absolute `EVIDENCE_DIR` paths noting they are local to the run host. Post exactly one comment per run, after the last round. Take `COMMENT_ID` from the `gh issue comment` output URL (`#issuecomment-ID`). The comment never closes or reopens anything.

## Publication verification

1. Confirm all implementation, chore, and fix work is verified, committed, and pushed; worktree clean.
2. Read back the draft PR: title/first-line `INITIATIVE_ID`, rationale bullets, `Closes` coverage for every implemented ticket, target/head branches, `isDraft` = `true`, and checks (pending/failed/absent/passed).
3. Preserve `SOURCE_ROOT`, PR URL, final pushed head, `RUN_DIR`, and `EVIDENCE_DIR` pointers outside the integration worktree.
4. Missing push, coverage, or metadata → fix and re-read, or report and keep the spec open.

## Closure gates

Recheck PR head, required checks, metadata, ticket coverage, and draft state. Close the spec only when all hold:

- Every in-scope ticket is integrated and closed; no `hitl` ticket is open.
- Chore result verified and pushed.
- Initiative verification passed; app verification is not `fail`/`partial`.
- Review completed at the current head; no unresolved bug/initiative findings or review blockers.
- Required checks are not pending/failed; publication and posting results are read back.

Keep the spec open for: failed/incomplete/skipped initiative review, review unavailable, posting failures, stale reviewed head (commits added after review, including by actualize), an unresolved `fail`/`partial` app verdict, or known unresolved earlier bug/initiative concerns. Report quality/smell suggestions separately; hand off review findings. Keep the branch and PR.
