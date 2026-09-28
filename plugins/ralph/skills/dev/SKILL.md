---
name: dev
description: AFK autonomous development loop — picks the next open issue, implements it, and commits the result.
argument-hint: '<milestone-title>'
---

# WORKTREE SETUP

Before entering the orchestrator loop, resolve the spec and set up the worktree.

## 0. Resolve harness settings

1. Run `/resolve-harness` skill from cwd; retain the emitted `KEY=value` lines as `HARNESS_SETTINGS`. Use `HARNESS_REPO_PATH` for all harness-repo operations (milestones, issues) and `CODEBASE_REPO_PATH` for codebase/worktree operations.

2. Bring `HARNESS_REPO_PATH` up to date with its remote before any reads or the final push depend on it.
**GUARD**:  Run only when `/resolve-harness` found `.harness.env` and emitted a non-empty `HARNESS_REPO_PATH`.
```bash
git -C "$HARNESS_REPO_PATH" fetch --all --prune
git -C "$HARNESS_REPO_PATH" pull
```

If the pull exits non-zero (conflicts detected), discard local state in favor of the remote — the harness repo is only ever read from, so it is safe to reset:

```bash
git -C "$HARNESS_REPO_PATH" reset --hard "@{upstream}"
```

`/resolve-harness` unavailable or empty `HARNESS_REPO_PATH` → use cwd for both `HARNESS_REPO_PATH` and `CODEBASE_REPO_PATH`. Empty/unset `CODEBASE_REPO_PATH` (e.g. a `.harness.env` written before this key existed) → default it to `$HARNESS_REPO_PATH`. `/resolve-harness` exiting non-zero → **exit** and report.

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

Run `/ralph-build` skill with `$HARNESS_REPO_PATH $WORKTREE_PATH`:

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

Read the installed `codey-*.agent.md` descriptions in the crew plugin's `agents/` directory. Choose the agent whose description best fits the selected issue's title and body; if several fit, choose the one central to the requested outcome. No matching technology → `general-purpose`. **Emit**: "Primary agent: <agent>."

After changing to `WORKTREE_PATH`, run the selected agent (or `general-purpose` if unavailable) via `runSubagent`. Its invocation directory is the worktree. For a general-purpose fallback, instruct it to implement the task, run focused verification, and return the five-field Codey report (including honest verification results). Use the following prompt (substitute actual values):

```
## TASK
- Title: <title>
- Body: <body>
- Comments: <comments>

## RECENT CHANGES
<last 5 commits from step 1>
```

## 4. Distill

Distill Codey's SUMMARY into Implementation Decisions. Use this in **Commit & push** (commit body) and **Update Spec** (spec update).

**Implementation Decisions** — 1–3 compressed technical bullets:
- Short, implementation-oriented statements.
- No file paths or code snippets.
- No filler — every word carries information.

## 5. Stage Codey's changes (source repo)

Operate in `WORKTREE_PATH`. Stage Codey's changes regardless of `STATUS` (**complete**, **partial**, or **blocked**) so Chorey has a staged diff to review; this only updates the index, no commit yet:

```bash
git add -A
```

## 6. Review (Chorey)

Run only when Codey's `STATUS` is **complete** and `chorey` is available; otherwise continue directly to **Commit & push** — reviewing unverified or broken work cannot preserve behavior that was never established.

After changing to `WORKTREE_PATH` (same invocation directory as Codey), run the `chorey` agent via `runSubagent` with no arguments; it reviews the staged diff directly (`git diff --cached`). Retain Chorey's report for use in **Commit & push**. Chorey's `STATUS` is informational only — it never changes the `STATUS` recorded in **Handle task result**, which always reflects Codey's report from **Invoke implementation agent**.

## 7. Commit & push (source repo)

Operate in `WORKTREE_PATH`. Build a single commit:

- When **Review (Chorey)** ran and its `FILES` field is not "none": run `git add -A` again to stage Chorey's cleanup, then build the commit from both reports —
  - **SUBJECT** → Use **ccode:** prefix, then Codey's one-line commit summary
  - **SUMMARY** → commit body: Implementation Decisions block, plus Chorey's `SUMMARY` when it changed files
  - **FILES** → Codey's list of files changed, plus Chorey's
  - **NOTES** → Codey's `NOTES`, plus Chorey's findings not applied
- Otherwise (Chorey did not run, or ran and changed nothing): build the commit from Codey's report fields and the distilled outputs from **Distill** alone —
  - **SUBJECT** → Use **ccode:** prefix, then one line commit summary
  - **SUMMARY** → commit body (Implementation Decisions block)
  - **FILES** → list of files changed
  - **NOTES** → blockers or context for the next iteration

Commit and push regardless of Codey's `STATUS` (**complete**, **partial**, or **blocked**):

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
