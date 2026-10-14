# GitHub functional-testing results

Bind `{{trackerRepository}}` to the resolved harness `$repo`, never the worktree remote. The actions below serve **FUNCTIONAL TESTING** only; preserve the phase's approval, retry, and escalation rules.

Use literal UTF-8 temporary files with `--body-file <file>` for multiline evidence. Remove them after use. Report failed writes and already-created issue URLs; never claim evidence or escalation was saved after a failed command.

## Comment on ticket

**Reads:** `{{issueNumber}}`, `{{body}}`.

```
gh issue comment {{issueNumber}} --repo {{trackerRepository}} --body-file <file>
```

**Returns:** comment URL. Use for execution evidence and the investigation backlink.

## Close ticket

**Reads:** `{{issueNumber}}`, `{{comment}}` (short summary after the evidence comment).

```
gh issue close {{issueNumber}} --repo {{trackerRepository}} --comment "{{comment}}"
```

**Returns:** closed state, confirmed with `gh issue view {{issueNumber}} --repo {{trackerRepository}} --json state`.

## Label ticket

**Reads:** `{{issueNumber}}`, `{{addLabels}}` (comma-separated).

```
gh issue edit {{issueNumber}} --repo {{trackerRepository}} --add-label "{{addLabels}}"
```

**Returns:** labels confirmed with `gh issue view {{issueNumber}} --repo {{trackerRepository}} --json labels`. Confirm `hitl` before creating an investigation.

## Create sub-ticket

**Reads:** `{{title}}`, `{{body}}`, `{{label}}`, `{{parentIssueNumber}}` (the resolved `$spec`).

List existing children first:

```
gh api --paginate repos/{{trackerRepository}}/issues/{{parentIssueNumber}}/sub_issues?per_page=100
```

Reuse/update an open investigation covering the same testing ticket and findings; inspect its body and backlinks. Update its evidence using **Comment on ticket**. Ensure the phase's required labels exist before creating; missing labels are an explicit setup error.

Otherwise create and attach:

```
gh issue create --repo {{trackerRepository}} --label "{{label}}" --title "{{title}}" --body-file <file>
gh api repos/{{trackerRepository}}/issues/{{childIssueNumber}} --jq .id
gh api repos/{{trackerRepository}}/issues/{{parentIssueNumber}}/sub_issues --method POST -F sub_issue_id={{childIssueId}}
```

Set `{{childIssueNumber}}` from the returned URL before linking. Confirm the issue's labels/body and presence in the parent's sub-issue list.

**Returns:** investigation number and URL. After a partial failure, retain the created number and repair the missing link; if the create response was lost, reconcile matching unlinked issues before retrying.

## Gotchas

`sub_issue_id` is the internal numeric ID, not the issue number. Use `-F` rather than `-f` for numeric fields. A failed read is not evidence of absence. Never write results to the code PR or switch the tracker to the worktree repository.
