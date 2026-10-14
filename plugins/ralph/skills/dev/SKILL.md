---
name: dev
description: AFK development loop — implements approved sub-tickets of a spec issue, commits and pushes, then opens a draft pull request.
argument-hint: '<spec-issue-number-or-url>'
---

# WORKTREE SETUP

Before entering the orchestrator loop, resolve the spec and set up the worktree.

## 0. Resolve harness settings

1. Run `/harness` skill from cwd; retain its `harnessRepoPath` from the emitted JSON. Use it as `$HARNESS_REPO_PATH` for all harness-repo operations (specs, issues).

2. Bring `HARNESS_REPO_PATH` up to date with its remote before any reads or the final push depend on it.
**GUARD**:  Run only when `/harness` found its settings file and emitted a non-empty `harnessRepoPath`.
```bash
git -C "$HARNESS_REPO_PATH" fetch --all --prune
git -C "$HARNESS_REPO_PATH" pull
```

If the pull exits non-zero (conflicts detected), discard local state in favor of the remote — the harness repo is only ever read from, so it is safe to reset:

```bash
git -C "$HARNESS_REPO_PATH" reset --hard "@{upstream}"
```

`/harness` unavailable, or exits reporting `missing` → use cwd as `$HARNESS_REPO_PATH`. `/harness` exits reporting `invalid` → **exit** and report.

## 1. Resolve spec

A `<spec-issue-number-or-url>` argument is **required**. If not provided, **exit** and report `Usage: /dev <spec-issue-number-or-url>`.

Assign its issue number once and reuse everywhere as `$spec`:

```bash
spec="<spec-issue-number>"
```

Fetch the spec issue:

```bash
repo=$(git -C "$HARNESS_REPO_PATH" remote get-url origin | sed -E 's#^git@[^:]+:##; s#^https?://[^/]+/##; s#\.git$##')
gh issue view "$spec" --repo "$repo" --json number,title,body,labels,state
```

`repo` resolves the harness remote (tasks live there) and is reused for all harness-repo commands below. Run this before the worktree is created.

If the issue is missing or lacks the `spec` label, **exit** and report "Spec not found: `$spec`".

Read spec metadata from the title and labels only; never parse `spec.body`:
- `initiative_id` — `spec.title` prefix before the first `:`.
- `target_branch` — the single `repo:base:<branch>` label. This branch lives in the **source repository** the worktree is created from, not necessarily the harness repo.
- `repository` (`owner/name`) — the single `repo:target:<owner>/<name>` label.

Any field missing, or no/several `repo:base:` or `repo:target:` labels → **exit** before creating any worktree, leave ticket labels unchanged, and report "Spec is missing required metadata."

Derive the checkout for `repository`: equals `$HARNESS_REPO_PATH`'s own `origin` remote (`git -C "$HARNESS_REPO_PATH" remote get-url origin`, normalized the same way as a `repos` entry) → `CODEBASE_REPO_PATH := $HARNESS_REPO_PATH`. Otherwise → `CODEBASE_REPO_PATH := $HARNESS_REPO_PATH/workspace/<name>` (`<name>` is `repository`'s part after the slash). Confirm the checkout exists and its own `origin` normalizes to `repository` — missing or a clone of another repository → **exit** before creating any worktree, leave ticket labels unchanged, and report why. Never read `repos` to make this decision.

## 2. Compute feature branch name

Format: `<version_underscored>_<spec-title-slug>` — or just `<spec-title-slug>` when `target_branch` carries no version.

Rules:
- Take the version from the target branch (e.g. `release/1.3.10` → `1.3.10`), replace dots with underscores → `1_3_10`. No version segment found (e.g. `main`, `develop`) → the branch name is the slug alone, with no version prefix.
- Slugify the full spec title: lowercase, replace spaces and special chars (including `:`) with hyphens, strip consecutive hyphens, max 50 chars

Example: spec `PROJ-1234: Azure Storage Circuit Breaker`, target `release/1.3.10` → `1_3_10_proj-1234-azure-storage-circuit-breaker`

## 3. Create worktree

Run `/create-worktree` skill:

```
/create-worktree $CODEBASE_REPO_PATH <target-branch> <feature-branch>
```

Parse the output to capture `WORKTREE_PATH` and `BRANCH`; assign the latter to `branch` and reuse it as `$branch` for the rest of this skill. All subsequent code, git, and PR commands run inside `WORKTREE_PATH`; only the spec/issue commands target the harness `repo`.

## 4. Build

Run `/ralph-build` skill with `$HARNESS_REPO_PATH $WORKTREE_PATH`:

A non-pass build → **exit** and report. Never enter the orchestrator loop on a broken build.

---

# ORCHESTRATOR LOOP

Repeat the following loop until no eligible implementation tasks remain, then continue to **CREATE PULL REQUEST**. Coding agents run their focused repository/accessor/proxy integration verification before commit.

## 1. Read state

Resolve `DEV_SKILL_DIR` from this installed `SKILL.md`'s folder. From `WORKTREE_PATH`, read recent commits and run the hook-synced shared issue fetcher against the harness repository and spec:

```bash
git log -n 5 --format="%H%n%ad%n%B" --date=short
python3 "$DEV_SKILL_DIR/github/fetch_issues.py" "$repo" --spec "$spec"
```

Run the commands sequentially and check each exit code. Parse the fetcher's JSON output as the task array; review the commits as recent-change context. The shared fetcher owns pagination, spec sub-issue selection, issue/comment serialization, and `IssueFilter` selection. It excludes `spec` and `hitl` issues (case-insensitive). A failed fetch exits rather than becoming an empty queue; an empty array ends only the implementation loop. Edit shared code in `tools/src/modules/github/`; `.githooks/pre-commit` generates this skill's `github/` copy.

## 2. Select next task

First drop every task with an unfinished blocker. For each task, list its blockers via the REST dependencies API; any output means it is blocked:

```bash
gh api "repos/$repo/issues/<number>/dependencies/blocked_by?per_page=100" --jq '.[] | select(.state == "open" or .state_reason == "not_planned") | .number'
```

A check failure exits. No unblocked task remains → end the implementation loop and report the blocked tasks as pending dependencies.

Pick the next task from the unblocked ones. Prioritize in this order (first match wins); break ties within a tier by lowest issue number:

1. Critical bugfixes
2. Development infrastructure — tests, types, dev scripts are precursors to features
3. Tracer bullets — tiny end-to-end slices that validate the approach early
4. Polish and quick wins
5. Refactors

**Emit** the selected `#<number> — <title>` before **Invoke implementation agent**. Fetch its current body and comments with `gh issue view <number> --repo "$repo" --json number,title,body,comments,labels,state`; recheck eligibility before dispatch. Fetch the selected issue directly to refresh all comments beyond the shared fetcher's bounded comment preview.

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

## 5. Commit & push (source repo)

Operate in `WORKTREE_PATH`. Build a single commit from Codey's report fields and the distilled outputs from **Distill**:

- **SUBJECT** → Use **ccode:** prefix, then one line commit summary
- **SUMMARY** → commit body (Implementation Decisions block)
- **FILES** → list of files changed
- **NOTES** → blockers or context for the next iteration

Commit and push regardless of Codey's `STATUS` (**complete**, **partial**, or **blocked**). Skip an empty commit when no staged changes exist, but still push. Check each command separately; a failed commit or push exits:

```bash
git add -A
git commit -m "<SUBJECT>" -m "<SUMMARY>" -m "<FILES>" -m "<NOTES>"
git push -u origin "$branch"
```

## 6. Handle task result

Maintain a per-issue attempt counter for this session, keyed by issue number.

Read Codey's `STATUS` field from **Invoke implementation agent**:

- **complete**: Close the issue with `gh issue close <number> --repo "$repo"`.
- **partial**: Increment the issue's attempt counter. If this is the 2nd consecutive `partial` for the issue, add `hitl` with `gh issue edit <number> --repo "$repo" --add-label "hitl"`; otherwise comment with the agent's SUMMARY using `gh issue comment <number> --repo "$repo" --body "..."`.
- **blocked**: Add `hitl` label with `gh issue edit <number> --repo "$repo" --add-label "hitl"`.


## 7. Update Spec

Using the Implementation Decisions from **Distill**, update the spec issue.

1. Fetch the open spec issue:
   ```bash
   gh issue view "$spec" --repo "$repo" --json number,body
   ```
2. If the spec is closed or unreadable, skip steps 3-4 below.
3. For the `Implementation Decisions` section, apply the merge logic, keeping the leading `metadata` block untouched:
   - If the section is absent from the spec body, append it.
   - Replace any entry that conflicts with or is superseded by a new decision.
   - Append decisions that are additive.
4. Write the updated body back:
   ```bash
   gh issue edit "$spec" --repo "$repo" --body "<updated-body>"
   ```

Return to **Read state**.

# CREATE PULL REQUEST

Run once, after the implementation loop ends (an empty implementation queue, or the iteration cap). Check whether a PR already exists for `$branch` targeting `<target-branch>`. Run from inside `WORKTREE_PATH` so the command targets the source repository's remote:

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
  --title "[<initiative-id>]: <spec-title>" \
  --body "**Initiative ID:** \`<initiative-id>\`" \
  --base "<target-branch>" \
  --head "$branch"
```

# COMMIT & PUSH HARNESS REPO

Run **once**, after **CREATE PULL REQUEST** completes. Operate in `$HARNESS_REPO_PATH` (resolved in **Resolve harness settings**) — never the worktree.

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

- ONE TASK AT A TIME. Each Codey invocation handles one ticket; Ralph processes tickets sequentially.
- ALWAYS re-read state before selecting the next task — context changes after each commit.
- An empty implementation queue proceeds to **CREATE PULL REQUEST**. Report unresolved implementation dependencies honestly; the `spec`-labeled issue is owned by the user and stays open.
- IMPLEMENTATION ITERATION CAP: after 2x the initial eligible implementation-task count, stop the implementation loop and continue to **CREATE PULL REQUEST**; incomplete dependencies remain pending.
- Failed skill invocations, commits, `git push`, or `gh` calls exit with the error; never claim a label was saved when its tracker write failed.
