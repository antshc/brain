# Sequential Implementation

Load this reference only for `mode=sequential` (the default), after input preparation, ticket-graph validation, and integration-worktree creation. The main `SKILL.md` owns the later app-verification, chore, cleanup, review, and finalization phases.

## Preconditions

- Load the main [GitHub reference](./github.md) before any GitHub action. Resolve `SOURCE_ROOT`, `WORKTREE_PATH`, `INTEGRATION_BRANCH`, `BASE_BRANCH`, `BASE_COMMIT`, and `INITIATIVE_ID` through its guards.
- Use **one** clean integration worktree and branch for the entire sequential run. Never create per-ticket branches/worktrees or merger agents; never reset, discard existing work, or merge the PR.
- Keep a run-local map of every ticket's `OWNER/REPO#NUMBER`, owning repository, status, blockers, integrated commit, and evidence. Never infer the issue repository from the source checkout.
- Treat a closed blocker as satisfied only if its implementation is verified in `BASE_COMMIT` or already integrated in this run. Cancelled/duplicate issues and external blockers require explicit resolution.
- Re-read `hitl` labels on selection; skip those tickets without implementing, commenting, closing, or adding closing references. An open skipped ticket does not satisfy its dependants.
- If no fresh implementer subagent is available, stop and report. Never implement a ticket in the orchestrator context.

## Run

1. **Select one ticket.** Recompute the ready frontier from the run-local graph. Choose one in-scope, non-`hitl` ticket whose blockers are satisfied. If none is ready while unfinished tickets remain, run *Blocked frontier* below. Done when one eligible ticket is selected or the run stops.
2. **Record the integration tip.** Confirm `WORKTREE_PATH` is clean and on `INTEGRATION_BRANCH`; record `@prevHead` = `HEAD`. Do not start a second writer in this worktree. Done when the starting commit and branch are verified.
3. **Delegate one ticket.** Read its issue and all comments. Fill [implementer.md](../agents/implementer.md) with every placeholder:

   | Placeholder | Value |
   | --- | --- |
   | `{{worktreePath}}` | `WORKTREE_PATH` |
   | `{{featureBranch}}` | `INTEGRATION_BRANCH` |
   | `{{targetBranch}}` | `BASE_BRANCH` |
   | `{{ticketJson}}` | Issue JSON plus comments and explicit `OWNER/REPO#NUMBER` |
   | `{{initiativeCommits}}` | `git -C WORKTREE_PATH log --reverse --format='%H %s%n%n%b' BASE_COMMIT..HEAD`, or `None yet.` |
   | `{{commitSubjectPrefix}}` | `ccode(<INITIATIVE_ID> <OWNER/REPO#NUMBER>): ` |

   Return the selected ticket and filled prompt to `SKILL.md`; only that orchestrator launches a **fresh implementer subagent** with the absolute reference handoff and waits for its final JSON. The implementer uses TDD/test seams, makes exactly one commit, and never pushes, publishes, or closes issues. Done when its result is available.
4. **Verify its result.** For `status=completed`, require all of:
   - Worktree `HEAD` equals `result.commit` and exactly one commit follows `@prevHead`.
   - Commit subject begins with the required ticket-specific prefix.
   - Worktree is clean and remains on `INTEGRATION_BRANCH`.
   - `result.verification` names checks actually executed and their results, including skipped infrastructure checks and errors. Run cheap confirmations if evidence is thin.
5. **Rework or stop.** On invalid JSON, `failed`, missing evidence, or a mismatched commit, delegate rework to **the same ticket's subagent**, at most two rounds. Recheck step 4 after each round. If still invalid, stop advancing; preserve the branch/worktree and report the blocker. Never reuse that subagent for a different ticket. An infrastructure-only failure does not block when test-seam evidence is sufficient; code-caused failures do.
6. **Publish the integrated ticket.** Only after step 4 succeeds:
   - Mark the ticket integrated in the run-local map.
   - Push `INTEGRATION_BRANCH`; after the first integrated commit, create or reuse a matching **draft** PR against `BASE_BRANCH` before starting the next ticket.
   - Use PR title `<INITIATIVE_ID>: <summary>` and the bare `INITIATIVE_ID` as the first body line. Preserve user content on updates; give terse rationale bullets answering “Why?”.
   - Add `Closes OWNER/REPO#NUMBER` only for implemented tickets, never for skipped ones. Reference the spec without closing it until finalization gates pass.
   - Post ticket evidence and PR pointer to the ticket's owning repository, then close that ticket as completed. Read back push, PR body, comment, and closure before reporting success.
7. **Repeat.** Recompute the ready frontier after each verified, published ticket and return to step 1 with a **new** implementer subagent. Do not batch tickets, delegate the next before the previous result settles, or bypass dependencies.
8. **Return.** When all in-scope, non-deferred tickets are integrated, pushed, and closed, return control to the main skill's app-verification phase. Keep the PR draft.

## Blocked frontier

1. List unfinished tickets and why each is unready, including open `hitl` blockers and unresolved external dependencies.
2. Preserve all local work and the existing draft PR; keep the spec open.
3. Stop before app verification, chore, worktree cleanup, code review, or finalization. Do not force progress or declare completion.

## Invariants

- Exactly one integration branch/worktree, one ticket at a time, one fresh implementer per ticket, and one verified commit per integrated ticket.
- Each ticket's evidence, publication, and closure follow its own `OWNER/REPO#NUMBER` identity.
- PR remains a draft throughout; neither the ticket implementer nor this procedure merges or marks it ready.
- Environment/infrastructure failures receive at most one quick confirmation attempt, with skipped checks recorded; do not troubleshoot them during ticket implementation.
