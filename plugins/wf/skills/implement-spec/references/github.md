# GitHub

Use `gh` for GitHub I/O and Git for branches/worktrees.

## Prerequisites

- Confirm `gh --version` and `gh auth status`. Parse the spec URL `https://github.com/OWNER/REPO/issues/NUMBER` into `TRACKER_REPOSITORY` = `OWNER/REPO` and spec identity `OWNER/REPO#NUMBER` (e.g. `https://github.com/acme/specs/issues/1` → `acme/specs#1`). Otherwise use explicit context; otherwise use `gh repo view --json nameWithOwner --jq .nameWithOwner` at the caller's repository root.
- Read the spec's labels. Exactly one `repo:target:<owner/repo>` selects `SOURCE_REPOSITORY` (the integration repository, parsed from the label name after the `repo:target:` prefix, independent of `TRACKER_REPOSITORY`); exactly one `repo:base:<branch>` selects `BASE_BRANCH`. Confirm source identity/default branch with `gh repo view SOURCE_REPOSITORY --json nameWithOwner,defaultBranchRef` and verify the labeled base exists. Missing, empty, conflicting, or inaccessible routing requires explicit resolution before writing; older unlabeled specs may use a user-confirmed source/base.
- Set `HARNESS_ROOT` to the caller's repository root (`git rev-parse --show-toplevel` where the skill runs). **MUST** find `HARNESS_ROOT/workspace/`; when missing, stop and report. Set `REPO` to the name part of `SOURCE_REPOSITORY` (`repo:target:<owner>/<repo>` → `<repo>`) and `SOURCE_ROOT` to `HARNESS_ROOT/workspace/REPO`. Verify `SOURCE_ROOT` is the primary checkout (not a worktree) and its `origin` remote matches `SOURCE_REPOSITORY`; on mismatch or missing checkout, stop and report. Use `git worktree list --porcelain` to identify existing worktrees.
- Set `INITIATIVE_ID` to the spec title's prefix before the first `:`, trimmed (e.g. `PAY-12: Refunds` → `PAY-12`). Missing `:`, empty prefix, or a value that is not a safe single path component (no `/`, `\`, `..`, leading `.`, or whitespace-only) requires explicit resolution before writing.
- Track each issue as `OWNER/REPO#NUMBER`; resolve `ISSUE_REPOSITORY` from its URL, explicit qualifier, or native relationship response. Bare references inherit the containing issue's repository; only an unqualified initial spec uses the caller-repository fallback above. Stop on ambiguous ownership. `TRACKER_REPOSITORY` identifies the spec's repository, not necessarily every ticket's.
- Replace placeholders with resolved argument values; quote paths and branch names. Use `--repo ISSUE_REPOSITORY` on issue commands and `--repo SOURCE_REPOSITORY` on PR commands. Use the confirmed source checkout/remote for Git commands, even when issue repositories differ.
- Report authentication, permission, network, and validation failures. Preserve local commits and partial remote results; never claim publication, passing checks, or closure after a failed operation.

## Read the task graph

| Purpose | Command |
|---|---|
| Read spec/ticket | `gh issue view NUMBER --repo ISSUE_REPOSITORY --json number,title,body,labels,state,stateReason,url` |
| Read all comments | `gh api --paginate repos/ISSUE_REPOSITORY/issues/NUMBER/comments` |
| List child tickets | `gh api --paginate repos/ISSUE_REPOSITORY/issues/PARENT/sub_issues` |
| List blockers | `gh api --paginate repos/ISSUE_REPOSITORY/issues/NUMBER/dependencies/blocked_by` |
| Record integrated evidence | `gh issue comment NUMBER --repo ISSUE_REPOSITORY --body-file EVIDENCE_FILE` |
| Close implemented issue | `gh issue close NUMBER --repo ISSUE_REPOSITORY --reason completed --comment "Implemented in COMMIT_SHA on INTEGRATION_BRANCH (PR_URL)."` |

Read every page. Resolve explicit parent/blocker references in issue bodies too; honor explicit repository qualifiers for external issues. Tickets inherit the spec's source/base; conflicting ticket routing requires resolution. Use text relationships only when native capabilities are confirmed unavailable, and report that mode. A 404 alone can mean an inaccessible or incorrect resource; do not silently interpret it as an empty graph.

Maintain a run-local mapping of ticket, blockers, status, integrated commit, and validation evidence, with the single shared worktree/branch recorded once. Tickets are closed as completed once their implementation is integrated (see **Closure and cleanup**); a ticket closed by this run counts as satisfied. Schedule one ticket at a time; dependants require committed, validated blocker implementations on the integration branch. Do not use open-issue counts alone as the frontier.

## Single worktree lifecycle

1. Set `WORKTREES_ROOT` to `HARNESS_ROOT/workspace/REPO.worktrees` (sibling of `SOURCE_ROOT`) and `WORKTREE_PATH` to `WORKTREES_ROOT/INITIATIVE_ID`. Confirm the resolved path stays under `WORKTREES_ROOT`; never derive a root from the current worktree.
2. Inspect `git worktree list --porcelain`, branch refs, and the destination. Create only the missing parent directories. If the path or proposed integration branch exists, stop for explicit resume or selection of a unique run suffix; never overwrite, reset, or reuse unrelated work.
3. Verify `workspace/` is ignored by the harness repository with `git -C HARNESS_ROOT check-ignore -q workspace/`; when not ignored, stop and report rather than editing harness ignore files.
4. Fetch the confirmed source remote/base and record its resolved commit as `BASE_COMMIT`; report fetch failures rather than using a stale base. Run `git -C SOURCE_ROOT worktree add -b INTEGRATION_BRANCH WORKTREE_PATH BASE_COMMIT`. Verify the worktree is clean and `HEAD` is on the new integration branch at that commit.
5. Run all ticket implementation, commits, checks, and the chore pass in `WORKTREE_PATH`. A delegated implementer receives that exact path/branch and one ticket; wait for completion and verify its result before another writer starts. Commit each verified ticket directly on the integration branch; no ticket-branch merge is needed. Preserve failed/incomplete changes and stop advancement.
6. After final validation and a successful push, confirm the worktree is clean, implementation/chore work is complete, and all local commits are present on the remote PR branch. Remove only that run-owned worktree with `git -C SOURCE_ROOT worktree remove WORKTREE_PATH`, without force. Preserve dirty, unpushed, or incomplete work and report its exact path/branch. Keep the integration branch; do not delete `WORKTREES_ROOT`.

## Pull request lifecycle

Push to the confirmed Git remote with `git push --set-upstream REMOTE INTEGRATION_BRANCH`; subsequent pushes must succeed before reporting the PR current.

| Purpose | Command |
|---|---|
| Find existing PR | `gh pr list --repo SOURCE_REPOSITORY --head INTEGRATION_BRANCH --state open --json number,url,isDraft,baseRefName,headRefName` |
| Open draft | `gh pr create --repo SOURCE_REPOSITORY --base BASE_BRANCH --head INTEGRATION_BRANCH --draft --title "TITLE" --body-file PR_FILE` |
| Update coverage | `gh pr edit PR_NUMBER --repo SOURCE_REPOSITORY --body-file PR_FILE` |
| Read PR | `gh pr view PR_NUMBER --repo SOURCE_REPOSITORY --json url,title,body,headRefOid,isDraft,baseRefName,headRefName,state` |
| Inspect checks | `gh pr checks PR_NUMBER --repo SOURCE_REPOSITORY` |
| Mark ready | `gh pr ready PR_NUMBER --repo SOURCE_REPOSITORY` |

Create the draft only after a verified ticket commit exists ahead of the base. Reuse a matching PR rather than duplicating it; preserve user-authored PR content when updating coverage. Use separate `Closes OWNER/REPO#NUMBER` lines for implemented tickets with their owning repositories. Reference the spec without a closing keyword until finalization gates pass; then add its closing reference. Never add closing references for skipped tickets.

Use title `INITIATIVE_ID: <summary>`. Body must retain exactly one `Initiative: INITIATIVE_ID` and `Initiative source: <authoritative issue URL>`. Default source is the input GitHub spec URL; use an explicitly designated Jira source when supplied, verifying its key matches INITIATIVE_ID. Do not guess Jira from the ID shape. Preserve user text and these fields on every update; read title/body back and verify identity/source before cleanup.

After confirmed worktree removal, invoke code review from SOURCE_ROOT. Review uses a temporary clone, not the removed worktree. Keep draft/spec open for review failure, unavailable initiative verification, posting failure, stale head or unresolved bug/initiative findings. Do not auto-fix during review.

Read the final body, target/head branches, draft state, and check results back. Distinguish pending, failed, absent, and passed checks; required pending/failed checks block readiness. Do not claim a nonexistent check passed.

## Closure and cleanup

Close each ticket with `gh issue close --reason completed` right after its commit and validation evidence are verified on the integration branch and the evidence comment is posted. Close the spec issue the same way only after all in-scope tickets are integrated and closed and the chore result is verified/pushed and post-cleanup code review completed at the current head without unresolved bug/initiative findings or review blockers. Verify each closure with `gh issue view NUMBER --repo ISSUE_REPOSITORY --json state,stateReason`; if closing fails, report it and never claim closure. Never close an issue whose commit or validation is missing, or that was skipped, cancelled, or deferred. Closing keywords in the PR stay as a merge-time backstop. Do not merge the PR without separate user authorization.

Use temporary Markdown body files outside the repository and remove only those created by this run. Follow **Single worktree lifecycle** for cleanup; retain dirty, unpushed, or incomplete work with an explicit report.

## Gotchas

- A closed issue may be cancelled or duplicate rather than implemented; verify the result exists in the integration base or integration branch. On resume, a ticket closed by an earlier run is satisfied only if its commit is on the integration branch.
- A ticket commit is not complete until the cumulative integration result passes relevant checks.
- Treat external blockers separately from run-local integrated work; never bypass unresolved external dependencies.
