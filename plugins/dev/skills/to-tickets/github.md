# GitHub

Use `gh` for GitHub I/O; ticket storage is GitHub Issues.

## Prerequisites

- Confirm `gh --version` and `gh auth status`. Require the user-supplied `TRACKER_REPOSITORY` in `OWNER/REPO` format: exactly two nonempty GitHub owner/repository names separated by one slash, not a URL or issue reference. Ask and wait when absent or malformed; no inferred default. Verify access with `gh repo view TRACKER_REPOSITORY --json nameWithOwner`.
- Replace `OWNER/REPO`, `NUMBER`, `PARENT`, `CHILD`, and database-ID placeholders with resolved values. For ticket creation and labels, `OWNER/REPO` is `TRACKER_REPOSITORY`; for issue reads/comments and database-ID lookup, use that issue's owning repository. Resolve a parent from its URL or explicit qualifier; a bare issue number uses `TRACKER_REPOSITORY`. Pass `--repo OWNER/REPO` explicitly; never use the checkout as an implicit destination.
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

For sub-issue endpoints, `OWNER/REPO` is the parent's repository; for dependency endpoints, it is the blocked child's repository. Resolve each referenced issue's database ID in its own repository, even when parent and tickets differ. Preserve fully qualified identities in body references and read-back.

If native relationships are confirmed unavailable on this host/repository, explain the limitation and retain `Part of OWNER/REPO#PARENT` and `Blocked by: OWNER/REPO#NUMBER` references in each affected child body. A 404 alone does not prove unsupported capability: check repository/issue access and endpoint availability first. Never hide authentication, permission, or malformed-request failures behind a text fallback.

## Gotchas

- Parent/sub-issue links describe membership, not execution order; blockers are separate edges.
- Paginate relationship and comment queries so no ticket or blocker is silently omitted.
- Read-back must match the approved graph, not merely show successful issue creation. Fully qualify cross-repository references.
