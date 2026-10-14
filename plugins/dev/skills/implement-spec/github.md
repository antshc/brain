# GitHub

Use `gh` for GitHub I/O and Git for branches/worktrees.

## Prerequisites

- Confirm `gh --version` and `gh auth status`. Resolve `TRACKER_REPOSITORY` from the spec URL or explicit context; otherwise use `gh repo view --json nameWithOwner --jq .nameWithOwner` at the caller's repository root.
- Read the spec's labels. Exactly one `repo:target:<owner/repo>` selects `SOURCE_REPOSITORY`; exactly one `repo:base:<branch>` selects `BASE_BRANCH`. Confirm source identity/default branch with `gh repo view SOURCE_REPOSITORY --json nameWithOwner,defaultBranchRef` and verify the labeled base exists. Missing, empty, conflicting, or inaccessible routing requires explicit resolution before writing; older unlabeled specs may use a user-confirmed source/base.
- Locate the source checkout and verify its remote matches `SOURCE_REPOSITORY`. Ask when no checkout or multiple candidates exist. Resolve `SOURCE_ROOT` to that repository's primary checkout, not a nested worktree; use `git worktree list --porcelain` to identify existing worktrees.
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

Read every page. Resolve explicit parent/blocker references in issue bodies too; honor explicit repository qualifiers for external issues. Tickets inherit the spec's source/base; conflicting ticket routing requires resolution. Use text relationships only when native capabilities are confirmed unavailable, and report that mode. A 404 alone can mean an inaccessible or incorrect resource; do not silently interpret it as an empty graph.

Maintain a run-local mapping of ticket, blockers, status, integrated commit, and validation evidence, with the single shared worktree/branch recorded once. GitHub issues can stay open while their implementation is integrated. Schedule one ticket at a time; dependants require committed, validated blocker implementations on the integration branch. Do not use open-issue counts alone as the frontier.

## Single worktree lifecycle

1. Resolve `SPEC_ID` to a safe single path component, such as `spec-123` from the tracker issue number. Set `WORKTREE_PATH` to `SOURCE_ROOT/.fake/worktrees/SPEC_ID`. Confirm it stays under the primary source checkout's `.fake/worktrees/`; never derive a second nested root from the current worktree.
2. Inspect `git worktree list --porcelain`, branch refs, and the destination. Create only the missing parent directories. If the path or proposed integration branch exists, stop for explicit resume or selection of a unique run suffix; never overwrite, reset, or reuse unrelated work.
3. Ensure `/.fake/worktrees/` is ignored in the primary checkout before creating the nested worktree. Preserve tracked ignore configuration; when needed, add only this exclusion to the repository-local exclude file resolved by `git rev-parse --git-path info/exclude`. Verify with `git check-ignore` and report conflicts, including tracked worktree content.
4. Fetch the confirmed source remote/base and record its resolved commit as `BASE_COMMIT`; report fetch failures rather than using a stale base. Run `git -C SOURCE_ROOT worktree add -b INTEGRATION_BRANCH WORKTREE_PATH BASE_COMMIT`. Verify the worktree is clean and `HEAD` is on the new integration branch at that commit.
5. Run all ticket implementation, commits, checks, and review fixes in `WORKTREE_PATH`. A delegated implementer receives that exact path/branch and one ticket; wait for completion and verify its result before another writer starts. Commit each verified ticket directly on the integration branch; no ticket-branch merge is needed. Preserve failed/incomplete changes and stop advancement.
6. After final validation and a successful push, confirm the worktree is clean, the run is complete, and all local commits are present on the remote PR branch. Remove only that run-owned worktree with `git -C SOURCE_ROOT worktree remove WORKTREE_PATH`, without force. Preserve dirty, unpushed, or incomplete work and report its exact path/branch. Keep the integration branch; do not delete `.fake/` or the shared worktree parent.

## Pull request lifecycle

Push to the confirmed Git remote with `git push --set-upstream REMOTE INTEGRATION_BRANCH`; subsequent pushes must succeed before reporting the PR current.

| Purpose | Command |
|---|---|
| Find existing PR | `gh pr list --repo SOURCE_REPOSITORY --head INTEGRATION_BRANCH --state open --json number,url,isDraft,baseRefName,headRefName` |
| Open draft | `gh pr create --repo SOURCE_REPOSITORY --base BASE_BRANCH --head INTEGRATION_BRANCH --draft --title "TITLE" --body-file PR_FILE` |
| Update coverage | `gh pr edit PR_NUMBER --repo SOURCE_REPOSITORY --body-file PR_FILE` |
| Read PR | `gh pr view PR_NUMBER --repo SOURCE_REPOSITORY --json url,body,isDraft,baseRefName,headRefName,state` |
| Inspect checks | `gh pr checks PR_NUMBER --repo SOURCE_REPOSITORY` |
| Mark ready | `gh pr ready PR_NUMBER --repo SOURCE_REPOSITORY` |

Create the draft only after a verified ticket commit exists ahead of the base. Reuse a matching PR rather than duplicating it; preserve user-authored PR content when updating coverage. Use separate `Closes OWNER/REPO#NUMBER` lines with each issue's owning repository for the spec and each implemented ticket, including when tracker and source differ.

Read the final body, target/head branches, draft state, and check results back. Distinguish pending, failed, absent, and passed checks; required pending/failed checks block readiness. Do not claim a nonexistent check passed.

## Closure and cleanup

Closing keywords close issues only after merge into the default branch, not when the PR is created or marked ready. For other targets, explain the outstanding closure step. Do not merge or close issues without separate user authorization.

Use temporary Markdown body files outside the repository and remove only those created by this run. Follow **Single worktree lifecycle** for cleanup; retain dirty, unpushed, or incomplete work with an explicit report.

## Gotchas

- A closed issue may be cancelled or duplicate rather than implemented; verify the result exists in the integration base.
- A ticket commit is not complete until the cumulative integration result passes relevant checks.
- Treat external blockers separately from run-local integrated work; never bypass unresolved external dependencies.
