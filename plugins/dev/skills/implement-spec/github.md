# GitHub

Use `gh` for GitHub I/O and Git for branches/worktrees.

## Prerequisites

- Confirm `gh --version`, `gh auth status`, and repository identity/default branch with `gh repo view --json nameWithOwner,defaultBranchRef`. Confirm the integration base rather than assuming `main`.
- Replace `OWNER/REPO`, issue/PR numbers, branch names, and file placeholders with resolved values. Pass `--repo OWNER/REPO` explicitly on issue and PR commands.
- Report authentication, permission, network, and validation failures. Preserve local commits and partial remote results; never claim publication, passing checks, or closure after a failed operation.

## Read the task graph

| Purpose | Command |
|---|---|
| Read spec/ticket | `gh issue view NUMBER --repo OWNER/REPO --json number,title,body,labels,state,stateReason,url` |
| Read all comments | `gh api --paginate repos/OWNER/REPO/issues/NUMBER/comments` |
| List child tickets | `gh api --paginate repos/OWNER/REPO/issues/PARENT/sub_issues` |
| List blockers | `gh api --paginate repos/OWNER/REPO/issues/NUMBER/dependencies/blocked_by` |
| Record integrated evidence | `gh issue comment NUMBER --repo OWNER/REPO --body-file EVIDENCE_FILE` |

Read every page. Resolve explicit parent/blocker references in issue bodies too. Use text relationships only when native capabilities are confirmed unavailable, and report that mode. A 404 alone can mean an inaccessible or incorrect resource; do not silently interpret it as an empty graph.

Maintain a run-local mapping of ticket, blockers, worktree/branch, integrated commit, and validation evidence. GitHub issues can stay open while their implementation is integrated. Schedule dependants only after merged validation succeeds; do not use open-issue counts alone as the frontier.

## Pull request lifecycle

Push to the confirmed Git remote with `git push --set-upstream REMOTE INTEGRATION_BRANCH`; subsequent pushes must succeed before reporting the PR current.

| Purpose | Command |
|---|---|
| Find existing PR | `gh pr list --repo OWNER/REPO --head INTEGRATION_BRANCH --state open --json number,url,isDraft,baseRefName,headRefName` |
| Open draft | `gh pr create --repo OWNER/REPO --base BASE_BRANCH --head INTEGRATION_BRANCH --draft --title "TITLE" --body-file PR_FILE` |
| Update coverage | `gh pr edit PR_NUMBER --repo OWNER/REPO --body-file PR_FILE` |
| Read PR | `gh pr view PR_NUMBER --repo OWNER/REPO --json url,body,isDraft,baseRefName,headRefName,state` |
| Inspect checks | `gh pr checks PR_NUMBER --repo OWNER/REPO` |
| Mark ready | `gh pr ready PR_NUMBER --repo OWNER/REPO` |

Create the draft only after a verified integration commit exists ahead of the base. Reuse a matching PR rather than duplicating it; preserve user-authored PR content when updating coverage. Use separate `Closes OWNER/REPO#NUMBER` lines for the spec and each implemented ticket.

Read the final body, target/head branches, draft state, and check results back. Distinguish pending, failed, absent, and passed checks; required pending/failed checks block readiness. Do not claim a nonexistent check passed.

## Closure and cleanup

Closing keywords close issues only after merge into the default branch, not when the PR is created or marked ready. For other targets, explain the outstanding closure step. Do not merge or close issues without separate user authorization.

Use temporary Markdown body files outside the repository and remove only those created by this run. Remove only clean, integrated run-owned worktrees; retain dirty/unmerged work with an explicit report.

## Gotchas

- A closed issue may be cancelled or duplicate rather than implemented; verify the result exists in the integration base.
- A merged worker branch is not complete until the integrated result passes relevant checks.
- Treat external blockers separately from run-local integrated work; never bypass unresolved external dependencies.
