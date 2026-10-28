# GitHub setup

Prerequisites, spec creation, and task-graph reads.

## Prerequisites

Use `gh` for GitHub I/O and Git for branches/worktrees.

- Confirm `gh --version` and `gh auth status`. Parse the spec URL `https://github.com/OWNER/REPO/issues/NUMBER` into `TRACKER_REPOSITORY` = `OWNER/REPO` and spec identity `OWNER/REPO#NUMBER` (e.g. `https://github.com/acme/specs/issues/1` → `acme/specs#1`). Otherwise use explicit context; otherwise `gh repo view --json nameWithOwner --jq .nameWithOwner` at the caller's repository root.
- Read the spec's labels. Exactly one `repo:target:<owner/repo>` selects `SOURCE_REPOSITORY` (the integration repository, the label name after `repo:target:`, independent of `TRACKER_REPOSITORY`); exactly one `repo:base:<branch>` selects `BASE_BRANCH`. Confirm source identity/default branch with `gh repo view SOURCE_REPOSITORY --json nameWithOwner,defaultBranchRef` and verify the labeled base exists. Missing, empty, conflicting, or inaccessible routing requires explicit resolution before writing; older unlabeled specs may use a user-confirmed source/base.
- Set `HARNESS_ROOT` to the caller's repository root (`git rev-parse --show-toplevel` where the skill runs). **MUST** find `HARNESS_ROOT/workspace/`; missing → stop and report. Set `REPO` to the name part of `SOURCE_REPOSITORY` and `SOURCE_ROOT` to `HARNESS_ROOT/workspace/REPO`. Verify `SOURCE_ROOT` is the primary checkout (not a worktree) and its `origin` matches `SOURCE_REPOSITORY`; mismatch or missing checkout → stop and report. Identify existing worktrees with `git worktree list --porcelain`.
- Set `INITIATIVE_ID` to the spec title's prefix before the first `:`, trimmed (e.g. `PAY-12: Refunds` → `PAY-12`). Missing `:`, empty prefix, or a value that is not a safe single path component (no `/`, `\`, `..`, leading `.`, or whitespace-only) requires explicit resolution before writing.
- Track each issue as `OWNER/REPO#NUMBER`; resolve `ISSUE_REPOSITORY` from its URL, explicit qualifier, or native relationship response. Bare references inherit the containing issue's repository; only an unqualified initial spec uses the caller-repository fallback above. Stop on ambiguous ownership. `TRACKER_REPOSITORY` is the spec's repository, not necessarily every ticket's.
- Replace placeholders with resolved values; quote paths and branch names. Use `--repo ISSUE_REPOSITORY` on issue commands, `--repo SOURCE_REPOSITORY` on PR commands, and the confirmed source checkout/remote for Git commands.
- Report authentication, permission, network, and validation failures. Preserve local commits and partial remote results; never claim publication, passing checks, or closure after a failed operation.

## Create spec

Only for plan.md or description input. Run after the `gh` checks in *Prerequisites* and before its label routing.

1. `TRACKER_REPOSITORY` = `gh repo view --json nameWithOwner --jq .nameWithOwner` at `HARNESS_ROOT`. `@summary` = plan.md first heading, else first description sentence, trimmed to one line.
2. **Ask the user** once, in one question/input form, for target repository `owner/repo`, target/base branch, and initiative ID. Suggest the single source checkout's origin when available; **MUST NOT** guess any answer or silently select the repository default branch. Require all three; validate `INITIATIVE_ID` per *Prerequisites*, repository identity/access with `gh repo view SOURCE_REPOSITORY --json nameWithOwner`, and the branch with `gh api repos/SOURCE_REPOSITORY/branches/BASE_BRANCH` (URL-encode branch names in API path segments). Validate the source checkout and origin per *Prerequisites* before writes. Fetch that exact remote branch and resolve `BASE_COMMIT`; failure stops creation. Set `SOURCE_REPOSITORY`, `BASE_BRANCH`, and `INITIATIVE_ID` from validated answers; re-ask on invalid input.
3. Ensure labels `spec`, `repo:target:SOURCE_REPOSITORY` and `repo:base:BASE_BRANCH` exist: `gh label list --repo TRACKER_REPOSITORY --search NAME`; missing → `gh label create NAME --repo TRACKER_REPOSITORY`.
4. Body file (outside the repo) = full plan.md or description text verbatim, then a `Source: <plan.md path | inline description>` line. `gh issue create --repo TRACKER_REPOSITORY --title "INITIATIVE_ID: @summary" --body-file BODY_FILE --label "spec,repo:target:SOURCE_REPOSITORY,repo:base:BASE_BRANCH"`.
5. Read back title, labels, body; verify `spec`, exactly one target label, exactly one base label matching the chosen branch, and the initiative prefix. Done when the spec URL resolves; it becomes the run's spec input.

## Read the task graph

| Purpose | Command |
|---|---|
| Read spec/ticket | `gh issue view NUMBER --repo ISSUE_REPOSITORY --json number,title,body,labels,state,stateReason,url` |
| Read all comments | `gh api --paginate repos/ISSUE_REPOSITORY/issues/NUMBER/comments` |
| List child tickets | `gh api --paginate repos/ISSUE_REPOSITORY/issues/PARENT/sub_issues` |
| List blockers | `gh api --paginate repos/ISSUE_REPOSITORY/issues/NUMBER/dependencies/blocked_by` |
| Record integrated evidence | `gh issue comment NUMBER --repo ISSUE_REPOSITORY --body-file EVIDENCE_FILE` |
| Close implemented issue | `gh issue close NUMBER --repo ISSUE_REPOSITORY --reason completed --comment "Implemented in COMMIT_SHA on INTEGRATION_BRANCH (PR_URL)."` |

Read every page. Resolve explicit parent/blocker references in issue bodies too; honor repository qualifiers for external issues. Tickets inherit the spec's source/base; conflicting ticket routing requires resolution. Use text relationships only when native capabilities are confirmed unavailable, and report that mode. A 404 may mean an inaccessible or incorrect resource, never an empty graph.

Maintain a run-local map of each ticket's identity, owning repository, blockers, status, integrated commit, and validation evidence; record the integration worktree/branch once and, in parallel mode, each ticket's worktree/branch. A ticket closed by this run counts as satisfied. Dependants require committed, validated blocker implementations on the integration branch. Never use open-issue counts alone as the frontier.

Save reusable reads for subagent pointers: spec + comments → `RUN_DIR/spec.json`; each ticket + comments + explicit `OWNER/REPO#NUMBER` → `RUN_DIR/tickets/<OWNER>_<REPO>_<NUMBER>.json`. `RUN_DIR` = `HARNESS_ROOT/workspace/REPO.runs/<spec NUMBER>`; confirm it stays under `HARNESS_ROOT/workspace/`; never overwrite another run's directory (append a numeric suffix).
