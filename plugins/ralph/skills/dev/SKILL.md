---
name: dev
description: AFK autonomous development loop — picks the next open issue, implements it, and commits the result.
argument-hint: '<milestone-title>'
---

# WORKTREE SETUP

Before entering the orchestrator loop, resolve the PRD and set up the worktree.

## 1. Resolve milestone

A `<milestone-title>` argument is **required**. If not provided, **exit** and report `Usage: /dev <milestone-title>`.

Fetch the milestone by title:

```bash
repo=$((git remote get-url board 2>/dev/null || git remote get-url origin) | sed -E 's#^git@[^:]+:##; s#^https?://[^/]+/##; s#\.git$##')
gh api "repos/$repo/milestones?per_page=100&state=all" | jq '.[] | select(.title == "<milestone-title>")'
```

If no milestone matches, **exit** and report "Milestone not found: `<milestone-title>`".

Extract from `milestone.description`:
- **Feature ID** — value inside backticks after `**Feature ID:**` (e.g. `PROJ-1234`)
- **Target Branch** — value inside backticks after `**Target Branch:**` (e.g. `release/1.3.10`)

If either field is missing, **exit** and report "Milestone is missing required metadata."

## 2. Compute feature branch name

Format: `<version_underscored>_<milestone-title-slug>`

Rules:
- Take the version from the target branch (e.g. `release/1.3.10` → `1.3.10`), replace dots with underscores → `1_3_10`
- Slugify the full milestone title: lowercase, replace spaces and special chars (including `:`) with hyphens, strip consecutive hyphens, max 50 chars

Example: milestone `PROJ-1234: Azure Storage Circuit Breaker`, target `release/1.3.10` → `1_3_10_proj-1234-azure-storage-circuit-breaker`

## 3. Create worktree

Invoke the `/worktree` skill:

```
/worktree <target-branch> <feature-branch>
```

Parse the output to capture `WORKTREE_PATH` and `BRANCH`. All subsequent commands run inside `WORKTREE_PATH`.

If the worktree skill exits with an error, **exit**.

---

# ORCHESTRATOR LOOP

Repeat the following loop until no tasks remain.

## 1. Read state

Run the following commands and print their output so it is available as context.

```bash
echo "=== COMMITS ==="; 
echo "$(git log -n 5 --format="%H%n%ad%n%B---" --date=short 2>/dev/null || echo "No commits found.")"; 
echo ""
echo "=== TASKS ==="; echo "$(gh issue list --repo $repo --state open --milestone "<milestone-title>" --json number,labels,title,body,comments 2>/dev/null | jq '[.[] | select(.labels | map(.name) | (contains(["hitl"]) or contains(["prd"])) | not)]' 2>/dev/null || echo "[]")" | jq 'if length == 0 then "No issues found." else . end'
```

Parse the `TASKS` json array. Review `COMMITS` to understand what work has already been done.

## 2. Exit conditions

- If no tasks are available, **exit**.
- If all tasks are complete, **exit**. The `prd`-labeled issue is owned by the user — do not close it.

> `prd`, `hitl`-labeled issues are intentionally excluded from the task list (see step 1 filter) and must never be selected for implementation.

## 3. Select next task

Pick the next task. Prioritize in this order (first match wins):

1. Critical bugfixes
2. Development infrastructure — tests, types, dev scripts are precursors to features
3. Tracer bullets — tiny end-to-end slices that validate the approach early
4. Polish and quick wins
5. Refactors

## 4. Invoke implementation agent

Invoke the `csdroid` agent (or `general-purpose` if unavailable) via `runSubagent` with the following prompt (substitute actual values):

```
## TASK
- Title: <title>
- Body: <body>
- Comments: <comments>

## RECENT CHANGES
<last 5 commits from step 1>
```

## 5. Distill

Distill the agent's SUMMARY into two outputs. Use both in step 6 (commit body) and step 7 (PRD update).

**Implementation Decisions** — 1–3 compressed technical bullets:
- Short, implementation-oriented statements.
- No file paths or code snippets.
- No filler — every word carries information.

**Behavior Rules** — observable external behavior statements:
- No implementation details — rules describe externally visible behavior, not internals.
- Plain words only — no backticks, type names, or code formatting.
- Single-responsibility — one scenario or transition per rule.
- Rule format (pick one per bullet):
  1. `<triggering condition>` → `<resulting behavior>`
  2. The system MUST/SHOULD `<behavior>` when `<condition>`
  3. `<subject>` `<behavior>`

## 6. Commit

Build the commit from the agent's report fields and the distilled outputs from step 5:
- **SUBJECT** → Use **dcode:** prefix, than one line commit summary
- **SUMMARY** → commit body (two labelled blocks: Behavior Rules, then Implementation Decisions)
- **FILES** → list of files changed
- **NOTES** → blockers or context for the next iteration

## 7. Update PRD

Using the Implementation Decisions and Behavior Rules from step 5, update both sections of the PRD issue.

1. Fetch the open PRD issue:
   ```bash
   gh issue list --repo $repo --milestone "<milestone-title>" --label "prd" --state open --json number,body --jq '.[0]'
   ```
2. If no PRD issue is found, skip this step and continue.
3. For each section — `## Implementation Decisions` and `## Behavior Rules` — apply the same merge logic:
   - Replace any entry that conflicts with or is superseded by a new decision/rule.
   - Append decisions/rules that are additive.
4. Write the updated body back:
   ```bash
   gh issue edit <prd-number> --body "<updated-body>"
   ```

## 8. Handle result

Read the agent's `STATUS` field:

- **complete**: Close the issue with `gh issue close <number>`, push the branch, and loop back to step 1.
- **partial**: Comment on the issue with the agent's SUMMARY using `gh issue comment <number> --body "..."`, push the branch, and loop back to step 1.
- **blocked**: Add `hitl` label to the issue with `gh issue edit <number> --add-label "hitl"`, then loop back to step 1 to pick the next task.

After **complete** or **partial**, push the feature branch:

```bash
git push -u origin "$branch" 2>/dev/null || git push
```

# CREATE PULL REQUEST

Once all tasks are complete and the loop exits, check whether a PR already exists for `$branch` targeting `<target-branch>`:

```bash
existing_pr=$(gh pr list \
  --head "$branch" \
  --base "<target-branch>" \
  --state open \
  --json url \
  --jq '.[0].url' 2>/dev/null)
```

**If `existing_pr` is non-empty**, a PR already exists — print `"PR already exists: $existing_pr"` and skip creation.

**Otherwise**, open a draft PR from inside `WORKTREE_PATH`:

```bash
gh pr create --draft \
  --title "[<feature-id>]: <prd-title>" \
  --body "**Feature ID:** \`<feature-id>\`" \
  --base "<target-branch>" \
  --head "$branch"
```

If the PR creation fails, **exit** and report the error.

# RULES

- ONE TASK AT A TIME. The agent handles one task per invocation.
- ALWAYS re-read state before selecting the next task — context changes after each commit.
- IF NO TASKS ARE AVAILABLE, EXIT.
- ALL WORK HAPPENS INSIDE THE WORKTREE. Never commit to the base branch directly.
- NEVER IMPLEMENT `prd`, `hitl`-LABELED ISSUES. They define the work; the user owns their lifecycle.
