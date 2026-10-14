# GitHub

Use `gh` for GitHub I/O; ticket storage is GitHub Issues.

## Prerequisites

- Confirm `gh --version`, `gh auth status`, and the target with `gh repo view --json nameWithOwner,defaultBranchRef`. Resolve ambiguous remotes before writing.
- Replace `OWNER/REPO`, `NUMBER`, `PARENT`, `CHILD`, and database-ID placeholders with resolved values. Pass `--repo OWNER/REPO` on issue and label commands.
- Report authentication, permission, network, and validation failures explicitly. Stop dependent writes on failure; retain created URLs to resume without duplicates.

## Issues and labels

| Purpose | Command |
|---|---|
| Read issue | `gh issue view NUMBER --repo OWNER/REPO --json number,title,body,labels,state,url` |
| Read all comments | `gh api --paginate repos/OWNER/REPO/issues/NUMBER/comments` |
| List labels | `gh api --paginate repos/OWNER/REPO/labels --jq '.[].name'` |
| Create missing label | `gh label create ready-for-agent --repo OWNER/REPO --color 0E8A16 --description "Fully specified and ready for agent implementation"` |
| Create ticket | `gh issue create --repo OWNER/REPO --title "TITLE" --body-file TICKET_FILE --label ready-for-agent` |
| Update ticket body | `gh issue edit CHILD --repo OWNER/REPO --body-file TICKET_FILE` |
| Resolve database ID | `gh api repos/OWNER/REPO/issues/NUMBER --jq .id` |

Create the label only when absent; preserve existing metadata. Use one temporary Markdown body file per ticket outside the repository; remove run-owned files after publication/read-back. Record each returned URL before the next write. On ambiguous creation failure, inspect recent issues before retrying.

## Parent and blocking edges

| Purpose | Command |
|---|---|
| Attach child | `gh api --method POST repos/OWNER/REPO/issues/PARENT/sub_issues -F sub_issue_id=CHILD_DATABASE_ID` |
| List children | `gh api --paginate repos/OWNER/REPO/issues/PARENT/sub_issues` |
| Add blocker | `gh api --method POST repos/OWNER/REPO/issues/CHILD/dependencies/blocked_by -F issue_id=BLOCKER_DATABASE_ID` |
| List blockers | `gh api --paginate repos/OWNER/REPO/issues/CHILD/dependencies/blocked_by` |

Native relationship writes require numeric **database IDs**, not issue numbers or `node_id`. Create blockers before dependants, attach child issues without editing parent content, and read relationships back after writing.

If native relationships are confirmed unavailable on this host/repository, explain the limitation and retain `Part of OWNER/REPO#PARENT` and `Blocked by: OWNER/REPO#NUMBER` references in each affected child body. A 404 alone does not prove unsupported capability: check repository/issue access and endpoint availability first. Never hide authentication, permission, or malformed-request failures behind a text fallback.

## Gotchas

- Parent/sub-issue links describe membership, not execution order; blockers are separate edges.
- Paginate relationship and comment queries so no ticket or blocker is silently omitted.
- Read-back must match the approved graph, not merely show successful issue creation. Fully qualify cross-repository references.
