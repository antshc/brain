---
name: manage-backlog
description: Configure this repo for the workflow (wf:) skills — set up its ticket tracker, triage label vocabulary. Run once before first use of the other wf skills.
---
# Actions

Find the heading matching the requested operation and follow its steps exactly — do not skip steps or improvise an alternative command. Each action reads its inputs as `{{placeholder}}` variables already in the caller's context and states what it returns.


## Setup labels

Create missing GitHub issue labels for AFK/HITL task workflow.

Run the `scripts/create-labels.sh` script to create any missing labels.

**Returns:** nothing.

## Publish spec

Reads `{{featureId}}`, `{{specTitle}}`, `{{targetBranch}}` from context.

The milestone represents the capability behind `{{featureId}}` and may be reused by many specs. Its title is set only once, on first creation — never renamed by a later spec.

1. Look up an existing milestone for this capability:
   ```
   gh api repos/$REPO/milestones --jq '.[] | select(.title | startswith("{{featureId}}")) | .title' | head -1
   ```
   Set `{{milestoneTitle}}` to the matched title if found.

2. If no milestone was found, create one and set `{{milestoneTitle}}` to the title just created:
   ```
   gh api repos/$REPO/milestones \
     --method POST \
     --field title="{{featureId}}: {{specTitle}}" \
     --field description="**Feature ID:** \`{{featureId}}\`\n**Target Branch:** \`{{targetBranch}}\`"
   ```
   If a milestone was already found in step 1, skip this step — do not create or rename it, even if `{{specTitle}}` differs.

3. Create the issue:
   ```
   gh issue create --label spec --title "{{featureId}}: {{specTitle}}"
   ```

4. Assign the issue to the milestone, using the resolved `{{milestoneTitle}}` (not a newly derived title):
   ```
   gh issue edit {{issueNumber}} --milestone "{{milestoneTitle}}"
   ```

**Returns:** the spec ticket's number.

## Find spec ticket

Reads `{{milestoneTitle}}` from context.

```bash
gh issue list --repo "$REPO" --milestone "{{milestoneTitle}}" --label "spec" --json number,title,body,comments --limit 1
```

If no issue is found, ask the user for the GitHub issue number and fetch it with **Read ticket**.

**Returns:** the spec ticket's number, title, body, and comments.

## Create ticket

Reads `{{title}}`, `{{body}}`, `{{milestoneTitle}}`, `{{label}}` from context.

```bash
gh issue create --repo "$REPO" --milestone "{{milestoneTitle}}" --label "{{label}}" --title "{{title}}" --body "{{body}}"
```

Use a heredoc for a multi-line `{{body}}`.

**Returns:** the new ticket's number.

## Read ticket

Reads `{{issueNumber}}` from context.

```bash
gh issue view {{issueNumber}} --repo "$REPO" --json number,title,body,labels,comments
```

**Returns:** the ticket's `number`, `title`, `body`, `labels`, and `comments`.

## List tickets

Reads `{{state}}`, `{{label}}` from context.

```bash
gh issue list --repo "$REPO" --state {{state}} --label "{{label}}" --json number,title,body,labels,comments --jq '[.[] | {number, title, body, labels: [.labels[].name], comments: [.comments[].body]}]'
```

**Returns:** an array of tickets, each with number, title, body, labels, and comments.

## Comment on ticket

Reads `{{issueNumber}}`, `{{body}}` from context.

```bash
gh issue comment {{issueNumber}} --repo "$REPO" --body "{{body}}"
```

**Returns:** nothing.

## Label ticket

Reads `{{issueNumber}}`, `{{addLabels}}`, `{{removeLabels}}` from context. Either may be empty.

```bash
gh issue edit {{issueNumber}} --repo "$REPO" --add-label "{{addLabels}}" --remove-label "{{removeLabels}}"
```

**Returns:** nothing.

## Close ticket

Reads `{{issueNumber}}`, `{{comment}}` from context.

```bash
gh issue close {{issueNumber}} --repo "$REPO" --comment "{{comment}}"
```

**Returns:** nothing.

## Troubleshooting (all actions)

**Label not found** (`hitl` or `spec` label missing when any other action runs): via `/manage-backlog` **Setup labels** first, then retry the other action.

---

# Ticket tracker: GitHub

Tickets and Specs for this repo live as GitHub issues. Use the `gh` CLI for all operations. This section holds the vendor-specific knowledge (labels, repo resolution) the actions above rely on — callers should invoke the actions above, not this section's commands, directly.

## Labels

| Name | Color | Description |
|---|---:|---|
| `hitl` | `fbca04` | Requires human implementation |
| `spec` | `5319e7` | Spec task with implementation context |

Infer the repo (`$REPO`) from `git remote -v` — `gh` does this automatically when run inside a clone.

## Pull requests as a triage surface

**PRs as a request surface:** `no` (`yes | no`). Set to `yes` if this repo treats external PRs as feature requests; `/triage` reads this flag.

When set to `yes`, PRs run through the same labels and states as issues, using the `gh pr` equivalents:

- **Read a PR**: `gh pr view {{issueNumber}} --comments` and `gh pr diff {{issueNumber}}` for the diff.
- **List external PRs for triage**: `gh pr list --state open --json number,title,body,labels,author,authorAssociation,comments` then keep only `authorAssociation` of `CONTRIBUTOR`, `FIRST_TIME_CONTRIBUTOR`, or `NONE` (drop `OWNER`/`MEMBER`/`COLLABORATOR`).
- **Comment / label / close**: `gh pr comment`, `gh pr edit --add-label`/`--remove-label`, `gh pr close`.

GitHub shares one number space across issues and PRs, so a bare `#42` may be either — resolve with `gh pr view 42` and fall back to `gh issue view 42`.

