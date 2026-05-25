---
name: to-issues
description: Breaks a PRD into tracer-bullet GitHub issues. Accepts an optional plan or plan.md to guide slicing.
argument-hint: "<milestone-title> [<implementation details>, <plan.md>]"
---

# Implementation details to Issues

## Process

### 1. Gather inputs

`<milestone-title>` is **required**. If not provided as argument, ask the user.

**If only `<milestone-title>` is provided:**

Resolve the target repo once:
```bash
REPO=$((git remote get-url board 2>/dev/null || git remote get-url origin) | sed -E 's#^git@[^:]+:##; s#^https?://[^/]+/##; s#\.git$##')
```

Find the PRD issue by milestone and label:
```bash
gh issue list --repo "$REPO" --milestone "<milestone-title>" --label "prd" --json number,title,body,comments --limit 1
```
If no issue is found, ask the user for the GitHub issue number and fetch it:
```bash
gh issue view <number> --repo "$REPO" --json number,title,body,comments
```
Use the issue title, body, and comments as the PRD content.

**If `<milestone-title>` and (`<implementation details>` or `<plan.md>`) is provided:**

Use the implementation details as the PRD content instead of a GitHub issue:
- **File path** (e.g. `./plans/feature.md`, `/memories/session/plan.md`) — read the file.
- **Inline text** — use directly.

### 2. Explore the codebase (optional)

If you have not already explored the codebase, do so to understand the current state of the code.

### 3. Draft vertical slices

Break the PRD into **tracer bullet** issues. Each issue is a thin vertical slice that cuts through ALL integration layers end-to-end, NOT a horizontal slice of one layer.

Slices may be 'HITL' or 'AFK'. HITL slices require human interaction, such as an architectural decision or a design review. AFK slices can be implemented and merged without human interaction. Prefer AFK over HITL where possible.

<vertical-slice-rules>
- Each slice delivers a narrow but COMPLETE path through every layer (schema, API, UI, tests)
- A completed slice is demoable or verifiable on its own
- Prefer many thin slices over few thick ones
</vertical-slice-rules>

### 4. Quiz the user

Present the proposed breakdown as a numbered list. For each slice, show:

- **Title**: short descriptive name
- **Type**: HITL / AFK
- **Blocked by**: which other slices (if any) must complete first
- **Behavior Rules covered**: which behavior rules from the PRD this addresses

Ask the user:

- Does the granularity feel right? (too coarse / too fine)
- Are the dependency relationships correct?
- Should any slices be merged or split further?
- Are the correct slices marked as HITL and AFK?

Iterate until the user approves the breakdown.

### 5. Create the GitHub issues

For each approved slice, create a GitHub issue using `gh issue create --repo "$REPO"`.

The `--milestone "<milestone-title>"` from the PRD is required for each command, if missing ask user. Use the issue body template below.

Create issues in dependency order (blockers first) so you can reference real issue numbers in the "Blocked by" field.

<issue-template>
## Parent PRD

#<prd-issue-number>

## What to build

A concise description of this vertical slice. Describe the end-to-end behavior, not layer-by-layer implementation. Reference specific sections of the parent PRD rather than duplicating content.

## Acceptance criteria

- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3

## Blocked by

- Blocked by #<issue-number> (if any)

Or "None - can start immediately" if no blockers.

## Behavior Rules addressed

Reference by number from the parent PRD:

- Behavior rule 3
- Behavior rule 7

## Implementation Decisions

- Preserve integration constraints and assumptions required for implementation.
- Use short technical statements and implementation-oriented language.
- No specific file paths or code snippets (they become outdated quickly).

</issue-template>

Do NOT close or modify the parent PRD issue.
