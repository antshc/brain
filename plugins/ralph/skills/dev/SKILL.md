---
name: dev
description: AFK autonomous development loop — picks the next open issue, implements it, and commits the result.
argument-hint: '#<milestone-id>'
---

# WORKTREE SETUP

Before entering the orchestrator loop, resolve the PRD and set up the worktree.

## 1. Resolve milestone

A `<milestone>` argument is **required** in the format `#<id>` (e.g. `#1`, `#42`). If not provided, **exit** and report `Usage: /dev #<milestone-id>`.

Strip the `#` prefix and fetch the milestone directly:

```bash
gh api repos/{owner}/{repo}/milestones/<id>
```

If the milestone is not found, **exit** and report "Milestone not found: `<argument>`".

Store `milestone.title` for use in issue commands below.

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
echo "=== TASKS ==="; echo "$(gh issue list --state open --milestone "<milestone>" --json number,labels,title,body,comments 2>/dev/null | jq '[.[] | select(.labels | map(.name) | (contains(["hitl"]) or contains(["prd"])) | not)]' 2>/dev/null || echo "[]")" | jq 'if length == 0 then "No issues found." else . end'
```

Parse the `TASKS` json array. Review `COMMITS` to understand what work has already been done.

## 2. Exit conditions

- If no tasks are available, **exit**.
- If all tasks are complete, close the `prd`-labeled issue in the milestone and **exit**:
  ```bash
  gh issue list --milestone "<milestone>" --label "prd" --state open --json number --jq '.[0].number' | xargs gh issue close
  ```

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

## 5. Commit

After the agent reports back, use its status report to make a git commit. 
The commit message is composed from the agent's report fields:
- **dcode:** → commit subject (one line summary)
- **SUMMARY** → commit body (key technical decisions)
- **FILES** → list of files changed
- **NOTES** → blockers or context for the next iteration

## 6. Handle result

Read the agent's `STATUS` field:

- **complete**: Close the issue with `gh issue close <number>`, push the branch, and loop back to step 1.
- **partial**: Comment on the issue with the agent's SUMMARY using `gh issue comment <number> --body "..."`, push the branch, and loop back to step 1.
- **blocked**: Add `hitl` label to the issue with `gh issue edit <number> --add-label "hitl"`, then loop back to step 1 to pick the next task.

After **complete** or **partial**, push the feature branch:

```bash
git push -u origin "$branch" 2>/dev/null || git push
```

# CREATE PULL REQUEST

Once all tasks are complete and the loop exits, open a draft PR targeting the target branch from inside `WORKTREE_PATH`:

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
