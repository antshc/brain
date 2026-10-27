# GitHub map operations

## Repository and errors

Resolve `{{trackerRepository}}` using `gh repo view --json nameWithOwner --jq .nameWithOwner` from the docs/harness root or current single repository. An issue URL must belong to this tracker; resolve conflicting targets before acting. Use the explicit repository in every command.

Missing workflow labels → *run `init-wf` skill for wf setup and GitHub issue labels, using labels-only mode*. Missing tools, authentication, permissions, or failed writes → stop and report the operation and known remote changes. Do not claim a map/claim/resolution exists until confirmed; no Jira/local tracker fallback.

Use `--body-file <file>` with a temporary UTF-8 file for literal multiline bodies, evidence, and comments. Remove temporary files after use. Placeholder values are arguments, not shell expressions.

## Create ticket

**Reads:** `{{title}}`, `{{body}}`, `{{label}}` (`wayfinder:map` for the map).

```
gh issue create --repo {{trackerRepository}} --label "{{label}}" --title "{{title}}" --body-file <file>
```

**Returns:** issue number and URL. Record both immediately. On an interrupted response, inspect matching issues before retrying; a failed response is not proof that no issue was created.

## Create sub-ticket

**Reads:** `{{title}}`, `{{body}}`, `{{label}}` (`wayfinder:<type>`), `{{parentIssueNumber}}` (map or narrower parent ticket).

1. List the parent's children with **List sub-tickets**; reuse an unambiguous existing match instead of duplicating a decision. On a partial earlier create, also reconcile unlinked issues by title and their **Part of** map link.
2. Follow **Create ticket**, retaining `{{childIssueNumber}}`.
3. Resolve the child's internal ID and attach it:
   ```
   gh api repos/{{trackerRepository}}/issues/{{childIssueNumber}} --jq .id
   gh api repos/{{trackerRepository}}/issues/{{parentIssueNumber}}/sub_issues --method POST -F sub_issue_id={{childIssueId}}
   ```
4. Confirm the child appears in the parent's sub-issue list. A link failure leaves a created issue: report it and retry only the missing link.

**Returns:** verified child number and URL.

## Read ticket

**Reads:** `{{issueNumber}}`.

```
gh issue view {{issueNumber}} --repo {{trackerRepository}} --json number,url,title,body,state,labels,comments,assignees
```

**Returns:** those fields. Fetch blockers by number to confirm they are closed; inaccessible blockers keep a ticket off the frontier.

## List sub-tickets

**Reads:** `{{issueNumber}}`.

```
gh api --paginate repos/{{trackerRepository}}/issues/{{issueNumber}}/sub_issues?per_page=100
```

**Returns:** every child's number, title, body, state, labels, assignees. Recurse through open children when finding the frontier. Use the body's **Blocked by** convention, not native dependency links, for Wayfinder decisions.

## Assign ticket

**Reads:** `{{issueNumber}}`. Refresh the ticket first; an assigned or closed ticket is not claimable.

```
gh issue edit {{issueNumber}} --repo {{trackerRepository}} --add-assignee "@me"
```

Read again to confirm the current user is the sole claimant before work. A conflicting claim requires choosing another ticket or resolving ownership; assignment is not atomic locking.

**Returns:** confirmed assignment.

## Unassign ticket

**Reads:** `{{issueNumber}}`.

```
gh issue edit {{issueNumber}} --repo {{trackerRepository}} --remove-assignee "@me"
```

**Returns:** confirmed no current-user assignee after **Read ticket**; the open ticket returns to the frontier.

## Comment on ticket

**Reads:** `{{issueNumber}}`, `{{body}}` (resolution/evidence).

```
gh issue comment {{issueNumber}} --repo {{trackerRepository}} --body-file <file>
```

**Returns:** resolution comment URL. Confirm it exists before closing.

## Close ticket

**Reads:** `{{issueNumber}}`, `{{comment}}` (short closing summary, after the detailed resolution comment).

```
gh issue close {{issueNumber}} --repo {{trackerRepository}} --comment "{{comment}}"
```

**Returns:** confirmed closed state after **Read ticket**. Out-of-scope closures go in the map's **Out of scope**, not **Decisions so far**.

## Update map or ticket

**Reads:** `{{issueNumber}}`, revised `{{body}}`.

Read the latest body first; preserve concurrent edits, existing decisions, fog, and scope boundaries. Apply the intended section change to a temporary UTF-8 file:

```
gh issue edit {{issueNumber}} --repo {{trackerRepository}} --body-file <file>
```

**Returns:** verified updated body. Reconcile partial comment/close/map-update failures before retrying so evidence and index entries are not duplicated.

## Gotchas

Native sub-issues require the internal numeric `id`, not issue `number`; `-F` sends a number. Body links do not create parent/child relationships. Wayfinder's body-based blockers are intentionally distinct from implementation tickets' native blockers.
