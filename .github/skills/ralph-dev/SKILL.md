---
argument-hint: <milestone-title>
description: AFK autonomous development loop — picks the next open issue, implements it, and commits the result.
metadata:
    github-path: plugins/ralph/skills/ralph-dev
    github-ref: refs/tags/v0.1.0-479
    github-repo: https://github.com/antshc/brain
    github-tree-sha: 41da1b5b59246fbed10b570833722c285c1d0b31
name: ralph-dev
---
# WORKTREE SETUP

Before entering the orchestrator loop, resolve the spec and set up the worktree.

## 0. Set Harness Root

Set `HARNESS_ROOT` to the current directory.

Use `HARNESS_ROOT` for all Harness Root repository operations. Change to `HARNESS_ROOT` before invoking `/ralph-worktree`.

## 1. Resolve milestone

A `<milestone-title>` argument is **required**. If not provided, **exit** and report `Usage: /ralph-dev <milestone-title>`.

Fetch the milestone by title:

```bash
repo=$(git -C "$HARNESS_ROOT" remote get-url origin | sed -E 's#^git@[^:]+:##; s#^https?://[^/]+/##; s#\.git$##')
gh api "repos/$repo/milestones?per_page=100&state=all" | jq '.[] | select(.title == "<milestone-title>")'
```

Tasks live in the **harness repository**, so `repo` always resolves the `HARNESS_ROOT` `origin` remote. Run this before the worktree is created.

If no milestone matches, **exit** and report "Milestone not found: `<milestone-title>`".

Extract from `milestone.description`:
- **Feature ID** — value inside backticks after `**Feature ID:**` (e.g. `PROJ-1234`)
- **Target Branch** — value inside backticks after `**Target Branch:**` (e.g. `release/1.3.10`). This branch lives in the **Source Repository** the worktree is created from (the `workspace/` source repository when present, otherwise the Harness Root), not necessarily the Harness Root.

If either field is missing, **exit** and report "Milestone is missing required metadata."

## 2. Compute feature branch name

Format: `<version_underscored>_<milestone-title-slug>`

Rules:
- Take the version from the target branch (e.g. `release/1.3.10` → `1.3.10`), replace dots with underscores → `1_3_10`
- Slugify the full milestone title: lowercase, replace spaces and special chars (including `:`) with hyphens, strip consecutive hyphens, max 50 chars

Example: milestone `PROJ-1234: Azure Storage Circuit Breaker`, target `release/1.3.10` → `1_3_10_proj-1234-azure-storage-circuit-breaker`

## 3. Create worktree

Invoke the `/ralph-worktree` skill:

```
/ralph-worktree <target-branch> <feature-branch>
```

Parse the output to capture `SOURCE_REPO`, `WORKTREE_PATH`, and `BRANCH`. The `/ralph-worktree` skill runs the executable Source Repository contract: an absent `workspace/` selects Harness Root, while a present `workspace/` must contain exactly one direct-child Git repository. All subsequent code, Git, push, and PR commands run inside `WORKTREE_PATH`; only the milestone/issue commands target the Harness Root `repo`.

If the worktree skill exits with an error, **exit**.

---

# ORCHESTRATOR LOOP

Repeat the following loop until no tasks remain.

## 1. Read state

Run the following commands from the `WORKTREE_PATH` and print their output so it is available as context.

```bash
echo "=== COMMITS ==="; 
echo "$(git log -n 5 --format="%H%n%ad%n%B---" --date=short 2>/dev/null || echo "No commits found.")"; 
echo ""
echo "=== TASKS ==="; echo "$(gh issue list --repo $repo --state open --milestone "<milestone-title>" --json number,labels,title,body,comments 2>/dev/null | jq '[.[] | select(.labels | map(.name) | (contains(["hitl"]) or contains(["spec"])) | not)]' 2>/dev/null || echo "[]")" | jq 'if length == 0 then "No issues found." else . end'
```

Parse the `TASKS` json array. Review `COMMITS` to understand what work has already been done.

## 2. Exit conditions

- If all tasks are complete, **exit**. The `spec` -labeled issue is owned by the user — do not close it.

> `spec`, `hitl`-labeled issues are intentionally excluded from the task list (see step 1 filter) and must never be selected for implementation.

## 3. Select next task

Pick the next task. Prioritize in this order (first match wins):

1. Critical bugfixes
2. Development infrastructure — tests, types, dev scripts are precursors to features
3. Tracer bullets — tiny end-to-end slices that validate the approach early
4. Polish and quick wins
5. Refactors

## 4. Run Codey, then conditionally run Chorey

After changing to `WORKTREE_PATH`, invoke the `codey` agent directly via `runSubagent`. Its invocation directory is the Worktree Path; do not provide a workspace-path argument. Codey uses its invocation directory as its workspace. If Codey is unavailable, report `STATUS: blocked` naming Codey; do not substitute another agent. Use the following prompt (substitute actual values):

```
## TASK
- Title: <title>
- Body: <body>
- Comments: <comments>

## RECENT CHANGES
<last 5 commits from step 1>
```

Capture Codey's complete five-field report as `CODEY_OUTCOME`. If Codey is unavailable, synthesize its blocked five-field report and continue to step 5 so the selected issue receives human attention.

Only when `CODEY_OUTCOME` contains `STATUS: complete`, invoke the `chorey` agent directly via `runSubagent` in the same Worktree Path. Do not provide a workspace-path argument. Chorey reads the live uncommitted Git state itself. Pass the original task and the complete Codey outcome:

```
## TASK
- Title: <title>
- Body: <body>
- Comments: <comments>

## CODEY OUTCOME
<CODEY_OUTCOME>
```

If Chorey is unavailable, synthesize a blocked five-field report naming Chorey. If Codey is partial or blocked, do not invoke Chorey; use `CODEY_OUTCOME` as the final agent outcome.

## 5. Combine outcomes and derive changed files

When Chorey ran, combine its report with Codey's report: Chorey's `STATUS` controls the final status, their `SUMMARY` and `NOTES` are combined, and Codey's `GOTCHAS UPDATED` is preserved. Otherwise, the Codey report is the final outcome.

Derive `FINAL_FILES` from the current worktree's staged, unstaged, and untracked Git changes. This Git-derived list is authoritative over either agent's `FILES` field and must be retained for the final report before any commit is created.

Distill the combined summaries into Implementation Decisions for the history entry and spec update.

**Implementation Decisions** — 1–3 compressed technical bullets:
- Short, implementation-oriented statements.
- No file paths or code snippets.
- No filler — every word carries information.

## 6. Publish non-empty progress

Before any issue handling, inspect `FINAL_FILES`:

- When non-empty, stage the complete worktree change with `git add -A`, commit it with an `rcode:` subject and the Implementation Decisions block as its body, then push the feature branch.
- When empty, do not create or push an empty commit.

This applies to complete, partial, and blocked final outcomes alike; preserving non-empty work takes precedence over issue handling.

## 7. Update spec

Using the Implementation Decisions from step 5, update the spec issue.

1. Fetch the open spec issue:
   ```bash
   gh issue list --repo $repo --milestone "<milestone-title>" --label "spec" --state open --json number,body --jq '.[0]'
   ```
2. If no spec issue is found, skip this step and continue.
3. For the `## Implementation Decisions` section, apply the merge logic:
   - Replace any entry that conflicts with or is superseded by a new decision.
   - Append decisions that are additive.
4. Write the updated body back:
   ```bash
   gh issue edit <spec-number> --body "<updated-body>"
   ```

## 8. Handle result

Read the final combined `STATUS` field:

- **complete**: Close the selected task with `gh issue close <number>`.
- **partial**: Comment on the selected task with the combined summary using `gh issue comment <number> --body "..."`.
- **blocked**: Add the `hitl` label to the selected task with `gh issue edit <number> --add-label "hitl"`.

Never close the `spec`-labeled issue.

## 9. Commit harness root

Run **once** per iteration, after Handle result and after the agent has recorded any gotchas to `.droid/GOTCHAS.md`. Operate in `$HARNESS_ROOT` (resolved in step 0) — never the worktree.

- Stage **any change** in the harness root (`git add -A`), on top of whatever is already staged.
- If nothing is staged, skip the commit (no empty commits).
- **Emit** the commit SHA, or "nothing to commit".

Stage all changes, commit if anything is staged, and push — using the appropriate shell syntax for the current platform.

## CREATE PULL REQUEST

Once all tasks are complete and the loop exits, check whether a PR already exists for `$branch` targeting `<target-branch>`. Run from inside `WORKTREE_PATH` so the command targets the source repository's remote:

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
  --title "[<feature-id>]: <spec-title>" \
  --body "**Feature ID:** \`<feature-id>\`" \
  --base "<target-branch>" \
  --head "$branch"
```

If the PR creation fails, **exit** and report the error.

# RULES

- ONE TASK ONLY. The agent handles one selected task per invocation.
- IF NO TASKS ARE AVAILABLE, EXIT.
- ALL WORK HAPPENS INSIDE THE WORKTREE. Never commit to the base branch directly.
- PUBLISH NON-EMPTY WORKTREE PROGRESS BEFORE ISSUE HANDLING. Never create an empty commit.
- NEVER IMPLEMENT `spec`, `hitl`-LABELED ISSUES. They define the work; the user owns their lifecycle.
