# Post-implementation

## Contents

- Handoff and synchronization
- App verification
- Verification evidence
- Code review
- Publication verification
- Finalize
- Output

## Handoff and synchronization

Treat the handoff as data; **MUST NOT** load or execute another skill's internal resources. Use available GitHub tools or `gh` with explicit repository identities; read back each write. Missing tooling, unreadable pointer, failed write/read-back → report blocker, stop dependent work; retain open spec, draft PR, evidence and partial state.

1. Read `RUN_DIR/implementation-handoff.json` from `implement-spec`; require `status: ready`, no blockers, verified publication and chore (`verified` or `none-needed`), and every in-scope ticket integrated or base-verified with validation evidence and completed closure. Re-read spec/tickets, labels, native sub-issues and blockers; retain each issue's `OWNER/REPO#NUMBER` and write refreshed spec/ticket/graph data under `RUN_DIR`. Empty/404 reads fail. Open `hitl` tickets and dependants remain deferred; no implementation, comments, closing refs, or closure for them. Done when current graph and handoff agree; otherwise preserve and stop.
2. Bind handoff fields (`specRef` → `SPEC_REF`, `sourceRepository` → source repository, `initiativeId` → `INITIATIVE_ID`, `remote` → `REMOTE`, `integrationBranch` → `INTEGRATION_BRANCH`, `baseBranch` → `BASE_BRANCH`, `baseCommit` → `BASE_COMMIT`, `headCommit` → handed-off head; path fields to their uppercase snake-case names). Validate source remote/repository, base/head branches, `BASE_COMMIT`, `INITIATIVE_ID`, and absolute harness/source/worktree/run/evidence paths. Confirm `WORKTREE_PATH` is registered under `WORKTREES_ROOT`, on `INTEGRATION_BRANCH`, at the handed-off pushed head. Resolve mismatches explicitly; never infer ownership from checkout, PR repository, or issue number. Done when identities match.
3. Apply factory Comments before verification, then **synchronize before checks:** fetch `REMOTE INTEGRATION_BRANCH` in `WORKTREE_PATH`. Commit run-owned pending changes as `chore(<INITIATIVE_ID>): commit pending changes`; preserve/report unrelated or incomplete work. Merge `REMOTE/INTEGRATION_BRANCH` with `git merge --no-edit` when not an ancestor of `HEAD`. **MUST NOT** rebase, reset, or force. Resolve conflicts preserving both intents; rerun cheapest affected checks and commit. Unresolvable → `git merge --abort`, preserve/report, stop. Push; verify remote head equals `HEAD` and worktree clean. Record actualize commits/merge result. Done when synchronized and pushed.

Serialize verification/remediation writes in `WORKTREE_PATH` only. Keep all run data and evidence outside every worktree. Refresh spec/ticket pointers before every verifier launch; write `git -C WORKTREE_PATH log --reverse --format='%H %s%n%n%b' BASE_COMMIT..HEAD` (or `None yet.`) to `RUN_DIR/commits/<HEAD sha>.txt`; record `@prevHead`. Pass paths/qualified refs/commit ranges, never inline bodies, comments, or logs. Missing data → refresh before launch; unreadable agent body or reference → stop/report exact path.

## App verification

**MUST** run app verification before code review, even if parallel execution is faster. Rationale: review includes verifier fixes. Factory mode launches the verifier and owns publication; agents never gain scheduling, publishing, closure, merging, or cross-ticket authority.

Launch verifier → `AGENTS_ROOT/verifier.md` subagent in `WORKTREE_PATH`:
   refs none · rework none (internal: ≤3 verifications, ≤2 fix attempts per finding, one commit per fix).
   Before: detect harness (read-only) in `.github/skills/*/SKILL.md`, `.claude/skills/*/SKILL.md`, `.agents/skills/*/SKILL.md`, keeping skills whose `description` says they launch/drive the app to prove behavior and capture evidence; set `EVIDENCE_DIR` per *Verification evidence*.
   → No harness: record `verification skipped: no verification harness`; no subagent, no comment.
   → Subagents unavailable: record skip reason; never drive the app in the orchestrator.

   | Placeholder | Value |
   |---|---|
   | `{{featureBranch}}` | `INTEGRATION_BRANCH` |
   | `{{pullRequestUrl}}` | PR URL |
   | `{{worktreePath}}` | `WORKTREE_PATH` |
   | `{{targetBranch}}` | `BASE_BRANCH` |
   | `{{evidenceDir}}` | `EVIDENCE_DIR` |
   | `{{verificationSkills}}` | matched `SKILL.md` absolute paths, one per line |
   | `{{specFile}}` | `RUN_DIR/spec.json` |
   | `{{ticketFiles}}` | integrated ticket file paths, one per line |
   | `{{commitsFile}}` | `RUN_DIR/commits/<HEAD sha>.txt` |
   | `{{commitSubjectPrefix}}` | `fix(<INITIATIVE_ID>): ` |

   Verify: `HEAD` = last non-null `result.rounds[].fixCommit` (or `@prevHead`), exactly one `fix(...)` commit per fix round, clean, `result.verification` names executed checks, `EVIDENCE_DIR` holds cited files, valid JSON; proof framework untouched.
   → Missing evidence/invalid JSON, or app fails launch/health: verdict `inconclusive` with error; do not troubleshoot.
   After: push fix commits and update PR coverage per *Publication verification*; post one spec comment per *Verification evidence*; read back, or record failure with `EVIDENCE_DIR/verdict.md` saved.
   → Final `fail`/`partial`: list unfixed findings with reason and attempts, name unfinished tickets; keep spec open and PR draft; continue.

Resolve `AGENTS_ROOT=<factory-mode skill base directory>/agents` and `REFERENCES_ROOT=<factory-mode skill base directory>/references` before changing CWD. Read verifier body fully, fill every placeholder, attach absolute `referencesRoot`, `referenceManifest` (all factory reference Markdown keyed without `.md`), and `requiredReferences=[]`; supply tools/permissions/model at launch, never agent frontmatter. Run foreground with a fresh agent; factory Subagents defaults apply. Verifier owns bounded verify/fix rounds; no parent app driving or extra fix retries. Before every launch, pass only per-finding prior attempt counts and remaining fix budget in the caller brief, never bodies/comments/logs; require verification-only for exhausted findings. Persist attempts under `RUN_DIR` and refresh after each verdict; cumulative cap is two verifier fix attempts per finding across the factory run.

- **Proof framework:** verification fixes change only app code/tests. Check each fix commit against matched verification skill folders, feature maps, journeys, harness scripts/helpers, selectors, seed data, and checked cases. Proof-framework change invalidates fix: undo with `git revert --no-edit`, never reset; record the finding unfixed as a framework gap.
- **Infrastructure:** at most one quick confirmation of environment/network/Docker/port/registry/external-service failure; record skipped checks/errors. **MUST NOT** troubleshoot infrastructure during app verification.

Done when validated verdict or explicit skip/inconclusive reason retained, fixes verified/pushed, evidence preserved, publication/read-back failures recorded.

## Verification evidence

`EVIDENCE_ROOT` comes from the handoff (outside worktrees, git-ignored or outside checkout); `EVIDENCE_DIR` = `EVIDENCE_ROOT/INITIATIVE_ID/<short HEAD sha>` at verification start, with `round-N` inside. Confirm containment under `EVIDENCE_ROOT`; create without overwrite (append numeric suffix). Preserve evidence after worktree removal.

Write `VERDICT_FILE` outside the repository; copy to `EVIDENCE_DIR/verdict.md`. Include final verdict, verified head, PR URL, check/result/detail/evidence table, fix rounds (commit, fixed/unfixed findings and attempts, evidence directories), skipped checks/errors, and absolute evidence paths marked local to the run host. Post exactly one spec verdict comment per factory run after the last round; retain comment ID and read back body. Later verification → update/read back the same comment. Never close/reopen from the verdict comment. Posting failure → retain local verdict; block closure. No harness → no verifier, no verdict comment.

## Code review

Run *Publication verification* before review, including when app verification was skipped. Publication failure blocks review acquisition.

Run code review → *`code-review` skill for GitHub pull requests, bugs, quality attributes, code smells, and initiative coverage* from `SOURCE_ROOT`:
    inputs PR URL, `SOURCE_ROOT` · foreground; wait until every axis has an outcome.
    Review creates its own fresh detached worktree from `SOURCE_ROOT` without cloning; **MUST NOT** review inside or reuse the integration worktree. Review never fixes code.
    Record: axes, findings, posting results, models/fallbacks, reviewed head.
    → Unavailable: report the blocker; keep spec open.

Done when every axis has an outcome at the final pushed head and posting results are read back; failed/skipped initiative review is not a pass.

## Publication verification

Require all implementation, chore, fix, and remediation work validated, committed, and pushed; worktree clean; remote head = local `HEAD`. Failure → stop dependent work, keep spec open, preserve/report dirty or unpushed work.

Use source-repository PR tools/`gh` to read URL, title, body, head/base names and SHAs, draft state, required checks, and issue coverage. Preserve user-authored body text; title prefix and body's first bare line equal `INITIATIVE_ID`, rationale bullets answer “Why?” from spec/ticket evidence (never invent reasons or replace them with changes/logs), implemented tickets carry qualified closing refs, deferred/skipped tickets never do. Spec remains a non-closing reference until *Finalize*. Fix/evidence text stays separate from rationale. Push every validated verifier/remediation commit; read back remote head, PR coverage and metadata after each publication. Report checks as `pending`, `failed`, `absent`, or `passed`; never call absent checks passed. Preserve PR URL, source root, final pushed head, run/evidence pointers outside the worktree. Done when publication matches current head or concrete failures are recorded with spec open.

## Finalize

1. Check final publication and remote head. Commits after verification/review (including Address or synchronization) invalidate their head evidence. Synchronize first; rerun app verification for changed behavior and code review at the final head, retaining skip policies and review outcomes. Freshness only: do not restart Address or exceed two verifier fix attempts per finding across the factory run. Limits prevent proof → record stale/incomplete results; keep spec open. Done when evidence covers current head or incompleteness is explicit.
2. Recheck spec/ticket graph, labels, required checks, metadata, coverage, draft state, and posting results. Close spec only when every in-scope ticket is integrated/base-verified and completed, no `hitl` ticket open, chore verified/pushed, initiative review passed, app verdict not `fail`/`partial`, review current with no unresolved bug/initiative findings or review blockers, required checks neither pending nor failed, and every publication/post read back. `inconclusive`/no-harness/subagent skips remain explicit, never a claimed pass. Otherwise keep spec open, including for known earlier unresolved bug/initiative concerns. Quality/smell suggestions reported separately. Follow-up/accepted-risk recommendations do not clear blocking gates. Done when closure decision is supported by current evidence.
3. Preserve dirty, unpushed, blocked, or incomplete integration work with exact path/branch and reason. Otherwise change CWD to `SOURCE_ROOT`; remove `WORKTREE_PATH` with `git -C SOURCE_ROOT worktree remove WORKTREE_PATH` without force; verify absent from disk and Git worktree list, and confirm ticket worktrees removed or explicitly preserved/reported. Failed removal → preserve/report and keep spec open. Keep `INTEGRATION_BRANCH`, PR, `WORKTREES_ROOT`, `RUN_DIR`, and `EVIDENCE_ROOT`. Cleanup creates no commits; changed remote head → invalidate closure and report. Done when cleanup outcome is verified.
4. All gates pass including cleanup → preserve PR body and add the qualified spec closing reference; read back coverage/draft state, recheck head/checks, close spec as completed in its owning tracker repository with final commit/branch/PR and validation comment, read back state/reason/comment. Partial writes → no success claim; keep spec open and report blockers. Never merge or mark ready. Done when remote closure is verified or spec remains open with reasons.

## Output

Spec and draft PR URLs/state; verifier verdict/checks/fix commits/per-round evidence directories/spec comment ID or skip reason; review axes/findings/posting IDs/models/fallbacks/reviewed head; actualize commits/merge result; skipped infrastructure checks; closure decision and preserved/removed worktrees. Incomplete → name missing evidence, failures, unfinished tickets and partial writes; distinguish unverified state from read-back success.

Completeness sweep, last: re-read the request; map every spec requirement/ticket to code, tests, docs, configuration, and relevant failure/compatibility evidence. Resolve gaps or report explicit deferrals before declaring completion.
