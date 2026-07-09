---
name: to-issue
description: Publish the session plan as a GitHub issue. Use when the user wants to create a GitHub issue from the current session plan, submit a plan to the repo, or turn a session plan into a trackable issue.
---

# Session Plan to GitHub Issue

Publish the session `plan.md` from memory as a GitHub issue formatted to match the `to-tickets` template.

## Process

### 1. Read the session plan

Read `/memories/session/plan.md` using the memory tool.

If the file does not exist, stop and tell the user:
> No session plan found. Run the planning skill first to create `/memories/session/plan.md`.

### 2. Ask for the parent PRD issue number and fetch its milestone

Ask the user:
> What is the parent PRD issue number? (e.g. `42`)

Then fetch the PRD:

```bash
gh issue view <number> --json number,title,milestone
```

Store `milestone.title` if present — it will be used when creating the issue.

### 3. Reformat the plan into the issue template

Map the plan's sections into the following issue body structure:

<issue-template>
## Parent PRD

#<prd-issue-number>

## What to build

<plan's opening summary — the TL;DR or description paragraph(s) before the first section heading>

## Acceptance criteria

<plan's Verification section, each item converted to a `- [ ]` checkbox>

## Blocked by

<plan's Decisions section dependencies, listed as `- Blocked by #<n>` entries>

Or "None - can start immediately" if there are no blocking dependencies.

## Implementation notes

<plan's Steps section and Relevant files section, preserved verbatim>
</issue-template>

Extract the **issue title** from the plan's first top-level heading (`# ...`), stripping the leading `#`.

### 4. Create the GitHub issue

Detect the repo:

```bash
repo=$((git remote get-url board 2>/dev/null || git remote get-url origin) | sed -E 's#^git@[^:]+:##; s#^https?://[^/]+/##; s#\.git$##')
```

Create the issue immediately:

```bash
gh issue create \
  --repo "$repo" \
  --title "<title>" \
  --body "<body>"
```

If `milestone.title` was found in step 2, append `--milestone "<milestone-title>"`.

### 5. Report the result

Show the user the URL of the created issue.
