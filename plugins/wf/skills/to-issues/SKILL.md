---
name: to-issues
description: Breaks a PRD into tracer-bullet GitHub issues. Accepts an optional plan or plan.md to guide slicing.
argument-hint: "[<implementation details or path to plan.md>]"
---

# Implementation details to Issues

## Process

### 1. Gather inputs

**PRD (required)** — resolve in this order: Already in context (e.g. an open GitHub issue with the `prd` label, a prior message, or a URL). Ask the user for it if not found.

```bash
gh issue view <number> --json number,title,body,comments,milestone
```

Store `milestone.title` if present — used in step 5.

**Implementation details (optional)** — second argument, if provided:
- **File path** (e.g. `./plans/feature.md`, `/memories/session/plan.md`) — read the file.
- **Inline text** — use directly as implementation context.

If omitted, codebase exploration in step 2 supplies context instead.

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

For each approved slice, create a GitHub issue using `gh issue create --repo $((git remote get-url board 2>/dev/null || git remote get-url origin) | sed -E 's#^git@[^:]+:##; s#^https?://[^/]+/##; s#\.git$##')`.

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
