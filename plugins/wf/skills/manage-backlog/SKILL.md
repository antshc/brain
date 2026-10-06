---
name: manage-backlog
description: Configure this repo for the workflow (wf:) skills — set up its ticket tracker, triage label vocabulary. Run once before first use of the other wf skills.
---
# Actions

An **Initiative** is a coordinated product change tracked as one planning effort and may encompass multiple Capabilities and Features.

Find the heading matching the requested operation and follow its steps exactly — do not skip steps or improvise an alternative command. Each action reads its inputs as `{{placeholder}}` variables already in the caller's context and states what it returns.


## Setup labels

Create missing GitHub issue labels for AFK/HITL task workflow.

Resolve `scripts/create_labels.py` relative to this installed `SKILL.md`'s folder and run it with `python3` to create any missing labels, including `tests` and `bug`.

**Returns:** nothing.

## Publish spec

Reads `{{initiativeId}}`, `{{specTitle}}`, `{{targetBranch}}`, `{{repository}}` (`owner/name`), `{{body}}` from context.

The spec is one Initiative developed against one repository. Its tickets are sub-issues of the spec issue. `repo:target:{{repository}}` marks the repository, `repo:base:{{targetBranch}}` the base branch; `{{initiativeId}}` lives only in the title prefix. A second Spec for the same Initiative and repository stops instead of publishing.

1. Look up an existing spec for this Initiative and repository:
   ```
   gh issue list --repo "$REPO" --state all --label spec --label "repo:target:{{repository}}" --search '"{{initiativeId}}:" in:title' --json number --jq '.[0].number'
   ```
   A number returned → **stop** and report: a spec for this Initiative and repository already exists; publish nothing.

2. Ensure the repository and base-branch labels exist:
   ```
   gh label create "repo:target:{{repository}}" --repo "$REPO" --color 0e8a16 --description "Source repository for this spec's tickets" --force
   gh label create "repo:base:{{targetBranch}}" --repo "$REPO" --color c5def5 --description "Base branch for this spec's feature branch" --force
   ```

3. Write `{{body}}` verbatim to a temporary UTF-8 file.

4. Create the issue:
   ```
   gh issue create --repo "$REPO" --label "spec,repo:target:{{repository}},repo:base:{{targetBranch}}" --title "{{initiativeId}}: {{specTitle}}" --body-file <file>
   ```

**Returns:** the spec ticket's number.

## Find spec ticket

Reads `{{issueNumber}}` from context. Use **Read ticket**; if no number is given, ask the user for it.

**Returns:** the spec ticket's number, title, body, labels, and comments.

## Create ticket

Reads `{{title}}`, `{{body}}`, `{{label}}` from context. `{{label}}` accepts comma-separated labels: `tests,hitl` for functional verification; `bug,hitl` for failed-test investigation; add `repo:target:{{repository}}` to tickets of a spec.

```bash
gh issue create --repo "$REPO" --label "{{label}}" --title "{{title}}" --body "{{body}}"
```

Write a multiline `{{body}}` to a temporary UTF-8 file and use `--body-file` instead of `--body`; preserve literal text without shell interpolation.

**Returns:** the new ticket's number.

## Create sub-ticket

Reads `{{title}}`, `{{body}}`, `{{label}}`, `{{parentIssueNumber}}` from context. Creates a ticket and links it to `{{parentIssueNumber}}` via GitHub's native sub-issue relationship, so it shows as a child on the parent issue — use this instead of **Create ticket** whenever the new ticket belongs under another ticket, such as a spec's tickets.

1. Create the ticket, same as **Create ticket**:
   ```bash
   gh issue create --repo "$REPO" --label "{{label}}" --title "{{title}}" --body "{{body}}"
   ```
   Set `{{childIssueNumber}}` to the number in the returned URL.

2. Resolve the internal `id` the sub-issues API needs for each side — distinct from the issue `number`:
   ```bash
   gh api repos/$REPO/issues/{{parentIssueNumber}} --jq .id
   gh api repos/$REPO/issues/{{childIssueNumber}} --jq .id
   ```

3. Link the child as a sub-issue of the parent, using `-F` (typed) so `sub_issue_id` is sent as a number, not a string:
   ```bash
   gh api repos/$REPO/issues/{{parentIssueNumber}}/sub_issues --method POST -F sub_issue_id={{childIssueId}}
   ```

**Returns:** the new ticket's number.

## Link blocking

Reads `{{issueNumber}}`, `{{blockedBy}}` from context. `{{blockedBy}}`: comma-separated numbers of tickets that must finish before `{{issueNumber}}`. Records native GitHub dependency links — the source of truth for which tickets can run in parallel.

For each number `{{blockerNumber}}` in `{{blockedBy}}`, resolve the blocker's internal `id` (distinct from its issue `number`) and link it via the REST dependencies API, using `-F` (typed) so `issue_id` is sent as a number:

```bash
gh api repos/$REPO/issues/{{blockerNumber}} --jq .id
gh api repos/$REPO/issues/{{issueNumber}}/dependencies/blocked_by --method POST -F issue_id={{blockerId}}
```

A failure on an already-linked blocker is safe to ignore on rerun.

**Returns:** nothing.

## Read ticket

Reads `{{issueNumber}}` from context.

```bash
gh issue view {{issueNumber}} --repo "$REPO" --json number,title,body,labels,comments
```

**Returns:** the ticket's `number`, `title`, `body`, `labels`, and `comments`.

## List tickets

Reads `{{state}}`, `{{label}}` from context. To list a parent's children, use **List sub-tickets**.

```bash
gh issue list --repo "$REPO" --state {{state}} --label "{{label}}" --json number,title,body,labels,comments,assignees --jq '[.[] | {number, title, body, labels: [.labels[].name], comments: [.comments[].body], assignees: [.assignees[].login]}]'
```

**Returns:** an array of tickets, each with number, title, body, labels, comments, and assignees.

## List sub-tickets

Reads `{{issueNumber}}` from context.

```bash
gh api --paginate "repos/$REPO/issues/{{issueNumber}}/sub_issues?per_page=100" --jq '.[] | {number, title, body, state, labels: [.labels[].name], assignees: [.assignees[].login]}'
```

**Returns:** one object per sub-ticket, each with number, title, body, state, labels, and assignees.

## Assign ticket

Reads `{{issueNumber}}` from context. Claims the ticket for the current session.

```bash
gh issue edit {{issueNumber}} --repo "$REPO" --add-assignee "@me"
```

**Returns:** nothing.

## Comment on ticket

Reads `{{issueNumber}}`, `{{body}}` from context.

For multiline evidence, write `{{body}}` to a temporary UTF-8 file and replace `--body` with `--body-file`; preserve logs literally without shell interpolation.

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

**Label not found** (a workflow label missing when any other action runs): via `/manage-backlog` **Setup labels** first, then retry the other action.

---

# Ticket tracker: GitHub

Tickets and Specs for this repo live as GitHub issues. Use the `gh` CLI for all operations. This section holds the vendor-specific knowledge (labels, repo resolution) the actions above rely on — callers should invoke the actions above, not this section's commands, directly.

## Labels

| Name | Color | Description |
|---|---:|---|
| `hitl` | `fbca04` | Requires human implementation |
| `spec` | `5319e7` | Spec task with implementation context |
| `tests` | `1d76db` | Spec-wide functional-test execution; combine with `hitl` until approved |
| `bug` | `d73a4a` | Failure requiring investigation |
| `wayfinder:map` | `0e8a16` | Marks the map issue itself |
| `wayfinder:research` | `1d76db` | Research-type decision ticket |
| `wayfinder:experiment` | `5319e7` | Experiment-type decision ticket |
| `wayfinder:grilling` | `fbca04` | Grilling-type decision ticket (default case, drives `/grill-design`) |
| `wayfinder:task` | `d93f0b` | Manual-work decision ticket |

Infer the repo (`$REPO`) from `git remote -v` — `gh` does this automatically when run inside a clone.

## Gotchas

Installed `gh` lacks `issue edit --add-blocked-by`; **Link blocking** uses the REST dependencies API instead.

## Pull requests as a triage surface

**PRs as a request surface:** `no` (`yes | no`). Set to `yes` if this repo treats external PRs as feature requests.

When set to `yes`, PRs run through the same labels and states as issues, using the `gh pr` equivalents:

- **Read a PR**: `gh pr view {{issueNumber}} --comments` and `gh pr diff {{issueNumber}}` for the diff.
- **List external PRs for triage**: `gh pr list --state open --json number,title,body,labels,author,authorAssociation,comments` then keep only `authorAssociation` of `CONTRIBUTOR`, `FIRST_TIME_CONTRIBUTOR`, or `NONE` (drop `OWNER`/`MEMBER`/`COLLABORATOR`).
- **Comment / label / close**: `gh pr comment`, `gh pr edit --add-label`/`--remove-label`, `gh pr close`.

GitHub shares one number space across issues and PRs, so a bare `#42` may be either — resolve with `gh pr view 42` and fall back to `gh issue view 42`.
