# Publication

Per-ticket publication, PR, verification evidence, read-back, and closure. Every GitHub call is a `GH_TOOL` command (see *GitHub operations*); `0` exit = read back and verified.

## Pull request

Push with `git push --set-upstream REMOTE INTEGRATION_BRANCH`; later pushes must succeed before reporting the PR current. Publish and update with `GH_TOOL pr publish`, only after a verified ticket commit exists ahead of the base. It always creates a draft, reuses a matching PR, preserves user-authored body text, and accumulates `Closes` lines.

- **Initiative ID:** title `{{initiative-id}}: <summary>` with the resolved `INITIATIVE_ID` substituted literally (e.g. `PAY-12`). The tool puts that ID alone on the body's first line (code review takes the first ID as the initiative) and replaces legacy `[#ID]`, `Initiative:` and `Initiative source:` markers. **MUST NOT** add an initiative-source URL.
- **Rationale file (`--rationale-file`):** terse `- ` bullets; each answers "Why?" (why the work is needed, which problem or risk it addresses) from spec/ticket evidence. **MUST NOT** describe code changes, list files or symbols, or reproduce a commit log. One bullet per reason. No reason in the source → report the missing rationale; never invent one. Good: `- Prevent duplicate charges when customers retry timed-out payments.` Bad: `- Add an idempotency check to PaymentService.`
- **Links:** `--closes` only implemented tickets, never skipped ones. The spec goes in `--refs` until closure gates pass, then in `--closes`. Verification or blocker text goes in `--evidence-file`, never in the bullets.
- **Read back:** `GH_TOOL pr read ... --expect-closes <implemented tickets>`; confirm each bullet answers "Why?". Exit `3` or a wrong first line, base/head, or `is_draft` ≠ `true` blocks success. Report `checks.status` accurately (`pending`, `failed`, `absent`, `passed`); required pending/failed checks block spec closure; never claim a nonexistent check passed.

## Ticket publication

After each verified integration:

1. Mark the ticket integrated in the run-local map.
2. Push `INTEGRATION_BRANCH`; after the first integrated commit, publish the draft PR; sequential mode does so before starting the next ticket.
3. Post ticket evidence and PR pointer with `issue comment` in the ticket's owning repository, then close it per *Closure*.
4. Read back push, PR body, comment, and closure before reporting success.

## Closure

Close each ticket with `GH_TOOL issue close REF --commit SHA --branch INTEGRATION_BRANCH --pr PR_URL` right after its commit and validation evidence are verified on the integration branch and the evidence comment is posted; the tool closes as `completed`, verifies the state, and refuses `hitl` issues. Close the spec the same way (`--comment`) only per *Closure gates*. Never close an issue whose commit or validation is missing, or that was skipped, cancelled, or deferred. PR closing keywords stay as a merge-time backstop.

## Verification evidence

`EVIDENCE_ROOT` = `HARNESS_ROOT/workspace/REPO.evidence` (sibling of `SOURCE_ROOT`, git-ignored with `workspace/`); `EVIDENCE_DIR` = `EVIDENCE_ROOT/INITIATIVE_ID/<short HEAD sha>` (HEAD at verification start; the verifier writes `round-N` inside). Confirm the path stays under `EVIDENCE_ROOT`; `mkdir -p`; never overwrite (append a numeric suffix). Evidence survives worktree removal; never delete it.

Write `VERDICT_FILE` outside the repository and copy it to `EVIDENCE_DIR/verdict.md`. Terse content: final verdict, verified head commit, PR URL, table of check, result, detail, evidence path, fix rounds (fix commit, findings fixed or unfixed, each round's evidence dir), then skipped checks with errors and the absolute `EVIDENCE_DIR` paths noting they are local to the run host. Post exactly one comment per run, after the last round: `GH_TOOL issue comment SPEC_REF --body-file VERDICT_FILE`; record the returned comment ID. The comment never closes or reopens anything.

## Publication verification

1. Confirm all implementation, chore, and fix work is verified, committed, and pushed; worktree clean.
2. `GH_TOOL pr read` with `--initiative-id` and `--expect-closes` for every implemented ticket: title/first-line ID, rationale bullets, coverage, target/head branches, draft state, checks.
3. Preserve `SOURCE_ROOT`, PR URL, final pushed head, `RUN_DIR`, and `EVIDENCE_DIR` pointers outside the integration worktree.
4. Missing push, coverage, or metadata → fix and re-read, or report and keep the spec open.

## Closure gates

Recheck PR head, required checks, metadata, ticket coverage, and draft state. Close the spec only when all hold:

- Every in-scope ticket is integrated and closed; no `hitl` ticket is open.
- Chore result verified and pushed.
- Initiative verification passed; app verification is not `fail`/`partial`.
- Review completed at the current head; no unresolved bug/initiative findings or review blockers.
- Required checks are not pending/failed; publication and posting results are read back.

Keep the spec open for: failed/incomplete/skipped initiative review, review unavailable, posting failures, stale reviewed head (commits added after review, including by actualize), an unresolved `fail`/`partial` app verdict, or known unresolved earlier bug/initiative concerns. Report quality/smell suggestions separately; hand off review findings. Keep the branch and PR. Worktree cleanup follows worktrees *Actualize and cleanup*; retain dirty, unpushed, or incomplete work with an explicit report. Keep `RUN_DIR` and `EVIDENCE_DIR` after the run.
