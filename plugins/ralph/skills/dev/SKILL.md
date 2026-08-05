---
name: dev
description: AFK autonomous development loop — picks the next open issue, implements it, and commits the result.
argument-hint: '<milestone-title>'
---

# WORKTREE SETUP

Before entering the orchestrator loop, resolve the spec and set up the worktree.

## 0. Resolve harness settings

Run `/resolve-harness` from cwd; retain the emitted `KEY=value` lines as `HARNESS_SETTINGS`. Use its `HARNESS_REPO_PATH` and `CODEBASE_REPO_PATH` values for all harness repository operations.

Unavailable or empty `HARNESS_REPO_PATH` → use cwd for both `HARNESS_REPO_PATH` and `CODEBASE_REPO_PATH`. Non-zero exit → **exit** and report.

## 1. Resolve milestone

A `<milestone-title>` argument is **required**. If not provided, **exit** and report `Usage: /dev <milestone-title>`.

Assign it once and reuse everywhere as `$milestone`:

```bash
milestone="<milestone-title>"
```

Fetch the milestone by title:

```bash
repo=$(git -C "$HARNESS_REPO_PATH" remote get-url origin | sed -E 's#^git@[^:]+:##; s#^https?://[^/]+/##; s#\.git$##')
gh api "repos/$repo/milestones?per_page=100&state=all" | jq --arg title "$milestone" '.[] | select(.title == $title)'
```

`repo` resolves the harness remote (tasks live there) and is reused for all harness-repo commands below. Run this before the worktree is created.

If no milestone matches, **exit** and report "Milestone not found: `$milestone`".

Extract from `milestone.description`:
- **Feature ID** — value inside backticks after `**Feature ID:**` (e.g. `PROJ-1234`)
- **Target Branch** — value inside backticks after `**Target Branch:**` (e.g. `release/1.3.10`). This branch lives in the **source repository** the worktree is created from (the `workspace/` source repo when present, otherwise the harness repo), not necessarily the harness repo.

If either field is missing, **exit** and report "Milestone is missing required metadata."

## 2. Compute feature branch name

Format: `<version_underscored>_<milestone-title-slug>`

Rules:
- Take the version from the target branch (e.g. `release/1.3.10` → `1.3.10`), replace dots with underscores → `1_3_10`
- Slugify the full milestone title: lowercase, replace spaces and special chars (including `:`) with hyphens, strip consecutive hyphens, max 50 chars

Example: milestone `PROJ-1234: Azure Storage Circuit Breaker`, target `release/1.3.10` → `1_3_10_proj-1234-azure-storage-circuit-breaker`

## 3. Create worktree

Run `/create-worktree` skill:

```
/create-worktree $CODEBASE_REPO_PATH <target-branch> <feature-branch>
```

Parse the output to capture `WORKTREE_PATH` and `BRANCH`; assign the latter to `branch` and reuse it as `$branch` for the rest of this skill. All subsequent code, git, and PR commands run inside `WORKTREE_PATH`; only the milestone/issue commands target the harness `repo`.

## 4. Build

Run `/ralph-build $HARNESS_REPO_PATH $WORKTREE_PATH` skill:

A non-pass build → **exit** and report. Never enter the orchestrator loop on a broken build.

---

# ORCHESTRATOR LOOP

Repeat the following loop until no tasks remain.

## 1. Read state

Run the following commands from the `WORKTREE_PATH` and print their output so it is available as context.

```bash
echo "=== COMMITS ==="; 
echo "$(git log -n 5 --format="%H%n%ad%n%B---" --date=short 2>/dev/null || echo "No commits found.")"; 
echo ""
echo "=== TASKS ==="; echo "$(gh issue list --repo "$repo" --state open --milestone "$milestone" --json number,labels,title,body,comments 2>/dev/null | jq '[.[] | select(.labels | map(.name) | (contains(["hitl"]) or contains(["spec"])) | not)]' 2>/dev/null || echo "[]")" | jq 'if length == 0 then "No issues found." else . end'
```

Parse the `TASKS` json array. Review `COMMITS` to understand what work has already been done.

> `spec`, `hitl`-labeled issues are intentionally excluded from the task list (see step 1 filter) and must never be selected for implementation.

## 2. Select next task

Pick the next task. Prioritize in this order (first match wins); break ties within a tier by lowest issue number:

1. Critical bugfixes
2. Development infrastructure — tests, types, dev scripts are precursors to features
3. Tracer bullets — tiny end-to-end slices that validate the approach early
4. Polish and quick wins
5. Refactors

**Emit** the selected `#<number> — <title>` before **Invoke implementation agent**.

## 3. Invoke implementation agent

After changing to `WORKTREE_PATH`, run the `codey` agent (or `general-purpose` if unavailable) via `runSubagent`. Its invocation directory is the worktree. Use the following prompt (substitute actual values):

```
## HARNESS
HARNESS_REPO_PATH=<$HARNESS_REPO_PATH>

## TASK
- Title: <title>
- Body: <body>
- Comments: <comments>

## RECENT CHANGES
<last 5 commits from step 1>
```

## 4. Distill

Distill Codey's SUMMARY into Implementation Decisions. Use this in **Commit & push Codey's checkpoint** (commit body) and **Update Spec** (spec update).

**Implementation Decisions** — 1–3 compressed technical bullets:
- Short, implementation-oriented statements.
- No file paths or code snippets.
- No filler — every word carries information.

## 5. Commit & push Codey's checkpoint (source repo)

Operate in `WORKTREE_PATH`. This commit is the safe baseline **Review (Chorey)** reviews and reverts against, so it must land before Chorey touches anything. Build it from Codey's report fields and the distilled outputs from **Distill**:
- **SUBJECT** → Use **ccode:** prefix, than one line commit summary
- **SUMMARY** → commit body (Implementation Decisions block)
- **FILES** → list of files changed
- **NOTES** → blockers or context for the next iteration

Stage and commit:

```bash
git add -A
git commit -m "<SUBJECT>" -m "<SUMMARY>" -m "<FILES>" -m "<NOTES>"
checkpoint_sha=$(git rev-parse HEAD)
```

Retain `$checkpoint_sha` for use in **Review (Chorey)**.

Push the feature branch regardless of Codey's `STATUS` (**complete**, **partial**, or **blocked**):

```bash
git push -u origin "$branch"
```

## 6. Review (Chorey)

Run only when Codey's `STATUS` is **complete** and `chorey` is available; otherwise continue to **Handle task result** — reviewing unverified or broken work cannot preserve behavior that was never established.

After changing to `WORKTREE_PATH` (same invocation directory as Codey), run the `chorey` agent via `runSubagent`. Use the following prompt (substitute actual values):

```
## HARNESS
HARNESS_REPO_PATH=<$HARNESS_REPO_PATH>

## BASELINE_COMMIT
<$checkpoint_sha>
```

`$checkpoint_sha` is the commit **Commit & push Codey's checkpoint** just made — Chorey reviews the change it introduced and, if its own edits fail verification, reverts against it. Retain Chorey's report for use in **Commit & push Chorey's cleanup**. Chorey's `STATUS` is informational only — it never changes the `STATUS` recorded in **Handle task result**, which always reflects Codey's report from **Invoke implementation agent**.

## 7. Commit & push Chorey's cleanup (source repo)

Run only when **Review (Chorey)** ran and its `FILES` field is not "none" — otherwise Codey's checkpoint already stands as the final result.

Operate in `WORKTREE_PATH`. Build a second commit from Chorey's own report fields:
- **SUBJECT** → Use **ccode: review —** prefix, then one line summary of what Chorey cleaned up
- **SUMMARY** → commit body (Chorey's SUMMARY)
- **FILES** → Chorey's list of files changed
- **NOTES** → Chorey's findings not applied, or blockers

Stage, commit, and push:

```bash
git add -A
git commit -m "<SUBJECT>" -m "<SUMMARY>" -m "<FILES>" -m "<NOTES>"
git push -u origin "$branch"
```

## 8. Handle task result

Maintain a per-issue attempt counter for this session, keyed by issue number.

Read Codey's `STATUS` field from **Invoke implementation agent** — never Chorey's:

- **complete**: Close the issue with `gh issue close <number> --repo "$repo"`.
- **partial**: Increment the issue's attempt counter. If this is the 2nd consecutive `partial` for the issue, add `hitl` with `gh issue edit <number> --repo "$repo" --add-label "hitl"`; otherwise comment with the agent's SUMMARY using `gh issue comment <number> --repo "$repo" --body "..."`.
- **blocked**: Add `hitl` label with `gh issue edit <number> --repo "$repo" --add-label "hitl"`.


## 9. Update Spec

Using the Implementation Decisions from **Distill**, update the spec issue.

1. Fetch the open spec issue:
   ```bash
   gh issue list --repo "$repo" --milestone "$milestone" --label "spec" --state open --json number,body --jq '.[0]'
   ```
2. If no spec issue is found, skip steps 3-4 below.
3. For the `Implementation Decisions` section, apply the merge logic:
   - If the section is absent from the spec body, append it.
   - Replace any entry that conflicts with or is superseded by a new decision.
   - Append decisions that are additive.
4. Write the updated body back:
   ```bash
   gh issue edit <spec-number> --repo "$repo" --body "<updated-body>"
   ```

Return to **Read state**.

# CREATE PULL REQUEST

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
  --title "[<feature-id>]: <milestone-title>" \
  --body "**Feature ID:** \`<feature-id>\`" \
  --base "<target-branch>" \
  --head "$branch"
```

# COMMIT & PUSH HARNESS REPO

Run **once**, after **Create Pull Request** completes. Operate in `$HARNESS_REPO_PATH` (resolved in **Resolve harness settings**) — never the worktree.

- Stage **any change** in the harness root (`git add -A`), on top of whatever is already staged.
- If nothing is staged, skip the commit (no empty commits).
- **Emit** the commit SHA, or "nothing to commit".

Stage all changes, commit if anything is staged, and push — using the appropriate shell syntax for the current platform.

# CLEANUP WORKTREE

Run **once**, after **Commit & Push Harness Repo** completes — development on `$branch` is finished for this invocation.

```
/delete-worktree $CODEBASE_REPO_PATH $WORKTREE_PATH $branch
```

# RULES

- ONE TASK AT A TIME. The agent handles one task per invocation.
- ALWAYS re-read state before selecting the next task — context changes after each commit.
- IF NO TASKS ARE AVAILABLE, EXIT. IF ALL TASKS ARE COMPLETE, EXIT — the `spec`-labeled issue is owned by the user; do not close it.
- ITERATION CAP: exit after 2x the initial open-task count if tasks still remain, to guard against a stuck loop.
- ANY FAILED SKILL INVOCATION, `git push`, OR `gh` CALL: **exit** and report the error.
