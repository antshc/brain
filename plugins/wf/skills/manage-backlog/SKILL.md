---
name: manage-backlog
description: Configure this repo for the workflow (wf:) skills — set up its ticket tracker, triage label vocabulary. Run once before first use of the other wf skills.
disable-model-invocation: true
---
# Actions

## Setup labels

Create missing GitHub issue labels for AFK/HITL task workflow.

Run the `scripts/create-labels.sh` script to create any missing labels.

## Publish spec

1. Create a milestone:
   ```
   gh api repos/$REPO/milestones \
     --method POST \
     --field title="{{featureId}}: {{specTitle}}" \
     --field description="**Feature ID:** \`{{featureId}}\`\n**Target Branch:** \`{{targetBranch}}\`"
   ```

2. Create the issue:
   ```
   gh issue create --label spec --title "{{featureId}}: {{specTitle}}"
   ```

3. Assign the issue to the milestone:
   ```
   gh issue edit {{issueNumber}} --milestone "{{featureId}}: {{specTitle}}"
   ```

### Troubleshooting

**Label not found** (`spec` label missing): run `Setup labels` to create the required labels, then retry.

# Ticket tracker: GitHub

Tickets and Specs for this repo live as GitHub issues. Use the `gh` CLI for all operations.

## Labels

| Name | Color | Description |
|---|---:|---|
| `hitl` | `fbca04` | Requires human implementation |
| `spec` | `5319e7` | Spec task with implementation context |

## Conventions

- **Create a ticket**: `gh issue create --title "..." --body "..."`. Use a heredoc for multi-line bodies.
- **Read a ticket**: `gh issue view {{issueNumber}} --comments`, filtering comments by `jq` and also fetching labels.
- **List tickets**: `gh issue list --state open --json number,title,body,labels,comments --jq '[.[] | {number, title, body, labels: [.labels[].name], comments: [.comments[].body]}]'` with appropriate `--label` and `--state` filters.
- **Comment on a ticket**: `gh issue comment {{issueNumber}} --body "..."`
- **Apply / remove labels on a ticket**: `gh issue edit {{issueNumber}} --add-label "..."` / `--remove-label "..."`
- **Close a ticket**: `gh issue close {{issueNumber}} --comment "..."`

Infer the repo from `git remote -v` — `gh` does this automatically when run inside a clone.

## Pull requests as a triage surface

**PRs as a request surface:** `no` (`yes | no`). Set to `yes` if this repo treats external PRs as feature requests; `/triage` reads this flag.

When set to `yes`, PRs run through the same labels and states as issues, using the `gh pr` equivalents:

- **Read a PR**: `gh pr view {{issueNumber}} --comments` and `gh pr diff {{issueNumber}}` for the diff.
- **List external PRs for triage**: `gh pr list --state open --json number,title,body,labels,author,authorAssociation,comments` then keep only `authorAssociation` of `CONTRIBUTOR`, `FIRST_TIME_CONTRIBUTOR`, or `NONE` (drop `OWNER`/`MEMBER`/`COLLABORATOR`).
- **Comment / label / close**: `gh pr comment`, `gh pr edit --add-label`/`--remove-label`, `gh pr close`.

GitHub shares one number space across issues and PRs, so a bare `#42` may be either — resolve with `gh pr view 42` and fall back to `gh issue view 42`.

## When a skill says "publish to the issue tracker"

Create a GitHub issue.

## When a skill says "fetch the relevant ticket"

Run `gh issue view {{issueNumber}} --comments`.

