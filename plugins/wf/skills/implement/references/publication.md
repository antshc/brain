# Publication

Both modes use the same publication checkpoints after the orchestrator validates a ticket commit on the integration branch. Every GitHub call uses `GH_TOOL`. Read back every write before claiming success.

## Publication checkpoint

The orchestrator is the sole writer. Keep `RUN_DIR/publication-checkpoint.json` outside the integration worktree. Save it atomically with `GH_TOOL run checkpoint --run-dir RUN_DIR --input FILE` using a separate input file. Remove only temporary input files this run owns.

- `run` holds a generated stable `id` (UUID or alphanumeric segments separated by hyphens), `specRef`, `sourceRepository`, `baseBranch`, `baseCommit`, `integrationBranch`, `worktreePath`, `mode`, and `maxParallel`. Save before the first worker launch and preserve the identity on resume.
- `tickets` is an object keyed by the effective graph ticket's `key`. Each entry holds `ref`, the reserved worker `branch` and `worktreePath` in parallel mode, and records verified state as it advances: `commit`, `verifiedAt`, `evidence` paths, `pushedHead`, `prNumber` and `prUrl`, `evidenceCommentId`, and `closure`. Use null for unknown publication fields. Omit worker branch and path before reservation and in sequential mode. Persist the exact body file and publication inputs before sending a write. Record the launch base and worktree/branch when preserving unfinished work.
- Record no-change evidence under the same ticket key, with a null commit and the exact checked SHA. No-change has no remote publication checkpoints. Record verified chore evidence and the SHA before its push so that an interrupted push can also be reconciled.

## Ticket publication

1. **Validated locally.** Record the exact integration SHA and evidence. Require a clean integration worktree, the expected branch and ancestry, and the approved result. Refresh the ticket labels/state before advancing. HITL or closed without completion → preserve and block the affected ticket.
2. **Pushed.** Inspect the remote head and push `GIT_TOOL branch push --checkout WORKTREE_PATH --repo SOURCE_REPOSITORY --remote REMOTE --name INTEGRATION_BRANCH --expected INTEGRATION_SHA --previous PRIOR_SHA_OR_ABSENT --set-upstream` only when the remote is absent or at the expected prior head and the update is a fast-forward. If it already equals the verified integration SHA, record it without pushing. Confirm the remote head and record it. Unexpected head → preserve and block.
3. **Draft PR verified.** Use *Pull request* with the pushed SHA. Record the verified PR number and URL.
4. **Evidence verified.** Use `GH_TOOL issue comment REF --body-file F --run-id ID` in the ticket's owning repository. The body records the integration SHA, validation, and PR URL. Keep its exact text for retries. The helper reuses the matching marked comment and reads back new comments. Duplicate markers or changed text require reconciliation. Record the comment ID.
5. **Closure verified.** Apply *Closure*. Update the checkpoint and make the verified completion available to the frontier. In sequential mode finish publication before starting another ticket. In parallel mode retain the reservation until integration and publication settle. If publication fails, preserve the checkpoint and withhold further integration writes while the remote state is uncertain.

## Pull request

Use `GH_TOOL pr publish` only with a verified commit ahead of the base and confirmed pushed head. It creates or updates a matching open draft and preserves user-authored text.

- *Run `github` skill for platform pull requests using Pull requests* with the canonical initiative ID, verified head/base, intent, rationale, actual changes, observed verification, and plain references. Pass the title and the three section bodies via `--title`, `--rationale-file` (terse `- ` bullets grounded in the spec/tickets), `--changes-file`, and `--evidence-file`. Include the spec and every verified integrated ticket via `--refs`. Track deferred or no-change status separately from implemented coverage. The helper converts legacy managed closing references to plain references on update.
- **Read back.** Use `GH_TOOL pr read --source-repository R --head H --initiative-id I --expect-refs REF…`. Compare draft state, base, branch, pushed SHA, rationale, and coverage. Report checks as `pending`, `failed`, `absent`, or `passed`. Required pending or failed checks block spec closure.

## Closure

After the integration SHA, pushed head, PR and evidence comment are verified, run `GH_TOOL issue close REF --run-id ID --evidence-comment N`. The helper verifies the marked comment belongs to this ticket and run, closes as completed, and reads back the state. It reuses a completed closure only with matching evidence. Keep the spec open. No-change, skipped, deferred, or cancelled tickets retain their observed tracker state.

## Resume publication

1. Read the recorded checkpoint from the explicit `RUN_DIR`. Match its spec and routing to current read-only preflight. Use the recorded mode and reconcile the recorded branch against Git state. Verify the pinned SHA is locally available and the recorded worktree is registered on the recorded branch. A verified run suffix is part of that identity. Use the recorded worker cap. Do not repin the base. A legacy run may resume only when the same facts can be reconstructed from existing handoff, Git, and tracker evidence. Validate legacy snapshot refs and branch/worktree ownership before reusing a legacy path. Preserve and report legacy worktrees at cleanup when a managed ownership record is absent.
2. Reconcile the local and remote integration heads against the recorded base and verified SHAs. Inspect every unsettled result and its evidence before counting it as done. Unexpected commits, dirty or ambiguous state, or missing proof → preserve work and return the exact blocker. Reconcile pending publications before new launches. Resume unfinished local work only when its identity and recorded starting state can be established. For a managed worktree, *run `git` skill for verified worktree lifecycle and reuse using Worktrees* with `RUN_DIR/worktrees/integration.json` and the reconciled expected HEAD before launching workers. A missing caller record with a managed ownership marker blocks reuse.
3. Resume *Ticket publication* from the first step without verified read-back. After a lost push response, compare the remote head before retrying. After a lost PR response, query by recorded number or qualified source/head and validate metadata before any retry. For evidence or closure, reuse the same run ID, input body, and comment ID. Read back the exact evidence body again before retrying closure. Checkpoint each recovered step. Recheck ticket labels and terminal state before writes. If a previously verified closure changed, preserve tracker state and report the mismatch.
4. Refresh graph and recompute completion evidence. Retain the checkpoint, worktree, and all evidence on a blocked exit. Resume chore only from verified recorded state; preserve any unverified local changes.

## Publication verification

1. Confirm implementation and chore changes are verified, committed, and pushed with a clean worktree. Distinguish verified chore no-change from missing evidence.
2. Use `GH_TOOL pr read` with `--initiative-id` and `--expect-refs` for every integrated ticket. Confirm the draft PR points to the exact pushed head and covers the spec and implemented tickets.
3. Refresh `GH_TOOL graph read`. Preserve each qualified ticket identity, validation and evidence pointers, observed closure, and blocker in the handoff. Mixed runs report verified no-change separately. Keep an open no-change ticket visible for the caller's spec closure gate.
4. Preserve the source, PR, final pushed SHA, worktree, checkpoint, and run/evidence pointers. Missing push, coverage, metadata, or unreadable evidence → fix and read back, or return a blocked handoff with spec open.
