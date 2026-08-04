---
name: manage-backlog
description: Configure this repo for the workflow (wf:) skills — set up its ticket tracker, triage label vocabulary. Run once before first use of the other wf skills.
---
# Actions

Find the heading matching the requested operation and follow its steps exactly — do not skip steps or improvise an alternative command. Each action reads its inputs as `{{placeholder}}` variables already in the caller's context and states what it returns.

`<skill-directory>` is the directory containing this SKILL.md file: take the absolute path you used to read this file and strip the trailing `/SKILL.md`. Never derive it any other way, and never search the filesystem for it.

Every action below runs a `python <skill-directory>/scripts/<name>.py <args>` script. Each script resolves the target repo itself (`gh repo view --json nameWithOwner`) — never pass or rely on a `$REPO` shell variable.

## Setup labels

Create missing GitHub issue labels for AFK/HITL task workflow.

```bash
python <skill-directory>/scripts/setup_labels.py
```

Prints one `exists:  <name>` or `created: <name>` line per label.

**Returns:** nothing.

## Publish spec

Reads `{{featureId}}`, `{{specTitle}}`, `{{targetBranch}}` from context.

The milestone represents the capability behind `{{featureId}}` and may be reused by many specs. Its title is set only once, on first creation — never renamed by a later spec.

```bash
python <skill-directory>/scripts/publish_spec.py "{{featureId}}" "{{specTitle}}" "{{targetBranch}}"
```

This looks up an existing milestone whose title starts with `{{featureId}}` and reuses it unchanged if found; otherwise it creates one titled `{{featureId}}: {{specTitle}}`. It then creates the spec issue (labeled `spec`, titled `{{featureId}}: {{specTitle}}`) and assigns it to the resolved milestone.

**Returns:** the spec ticket's number, printed to stdout.

## Find spec ticket

Reads `{{milestoneTitle}}` from context.

```bash
python <skill-directory>/scripts/find_spec_ticket.py "{{milestoneTitle}}"
```

Prints a JSON object (`number`, `title`, `body`, `comments`) if a matching open `spec`-labeled issue is found, else prints `null`.

If no issue is found, ask the user for the GitHub issue number and fetch it with **Read ticket**.

**Returns:** the spec ticket's number, title, body, and comments.

## Create ticket

Reads `{{title}}`, `{{body}}`, `{{milestoneTitle}}`, `{{label}}` from context.

```bash
python <skill-directory>/scripts/create_ticket.py "{{title}}" "{{body}}" "{{milestoneTitle}}" "{{label}}"
```

Pass a multi-line `{{body}}` as a single quoted argument (e.g. `"$(cat <<'EOF' ... EOF)"`).

**Returns:** the new ticket's number, printed to stdout.

## Read ticket

Reads `{{issueNumber}}` from context.

```bash
python <skill-directory>/scripts/read_ticket.py {{issueNumber}}
```

Prints a JSON object with the ticket's `number`, `title`, `body`, `labels`, and `comments`.

**Returns:** the ticket's `number`, `title`, `body`, `labels`, and `comments`.

## List tickets

Reads `{{state}}`, `{{label}}` from context.

```bash
python <skill-directory>/scripts/list_tickets.py "{{state}}" "{{label}}"
```

Prints a JSON array of tickets, each with `number`, `title`, `body`, `labels`, and `comments`.

**Returns:** an array of tickets, each with number, title, body, labels, and comments.

## Comment on ticket

Reads `{{issueNumber}}`, `{{body}}` from context.

```bash
python <skill-directory>/scripts/comment_ticket.py {{issueNumber}} "{{body}}"
```

**Returns:** nothing.

## Label ticket

Reads `{{issueNumber}}`, `{{addLabels}}`, `{{removeLabels}}` from context. Either may be empty.

```bash
python <skill-directory>/scripts/label_ticket.py {{issueNumber}} "{{addLabels}}" "{{removeLabels}}"
```

**Returns:** nothing.

## Close ticket

Reads `{{issueNumber}}`, `{{comment}}` from context.

```bash
python <skill-directory>/scripts/close_ticket.py {{issueNumber}} "{{comment}}"
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

Resolve the repo via `gh repo view --json nameWithOwner` — `gh` infers it from the clone's remote automatically.

## Pull requests as a triage surface

**PRs as a request surface:** `no` (`yes | no`). Set to `yes` if this repo treats external PRs as feature requests; `/triage` reads this flag.

When set to `yes`, PRs run through the same labels and states as issues, using the `gh pr` equivalents:

- **Read a PR**: `gh pr view {{issueNumber}} --comments` and `gh pr diff {{issueNumber}}` for the diff.
- **List external PRs for triage**: `gh pr list --state open --json number,title,body,labels,author,authorAssociation,comments` then keep only `authorAssociation` of `CONTRIBUTOR`, `FIRST_TIME_CONTRIBUTOR`, or `NONE` (drop `OWNER`/`MEMBER`/`COLLABORATOR`).
- **Comment / label / close**: `gh pr comment`, `gh pr edit --add-label`/`--remove-label`, `gh pr close`.

GitHub shares one number space across issues and PRs, so a bare `#42` may be either — resolve with `gh pr view 42` and fall back to `gh issue view 42`.

