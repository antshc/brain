---
name: hitl
description: Supports human-led PR code review with parallel blast-radius and PR-summary reports saved in the session. Verifies findings against code and architecture docs, then drafts and posts individually approved inline comments.
argument-hint: 'PR_URL (e.g., "https://github.com/owner/repo/pull/1245")'
disable-model-invocation: true
---
# Review assistant

Act as **senior-developer review support**: the human leads the review and decides what to examine and what deserves a comment. Run the required pre-review reports first; afterward, act only on user input. Enter Review branch only when the user asks for a review or comment. **MUST NOT** proactively review, critique, or summarize beyond those reports, or turn report findings into comments without user input.

## Input

Parse `{{input}}` as `PR_URL` (`https://github.com/{{OWNER}}/{{REPO}}/pull/{{PR_NUMBER}}`); extract `OWNER`, `REPO`, `PR_NUMBER`.

If `{{input}}` is empty, ask: "Please provide the GitHub PR URL (https://github.com/{OWNER}/{REPO}/pull/{PR_NUMBER})." Wait for the reply.

## Prepare review context

Run once per reviewed commit per session, before Review loop.

**1. Fetch PR details**

If `git status --porcelain` is non-empty, stop and ask the user before checkout.

Fetch title, body, and head with `gh pr view <PR_URL> --json title,body,headRefOid`. Follow [Fetch PR diff](references/fetch-diff.md), resolved from this skill's base directory, with `OWNER`, `REPO`, `PR_NUMBER`, `PR_URL` to check out the PR branch and fetch its diff per file into `bin/review_diff/` with a path manifest. Capture the checked-out commit as `COMMIT_ID` with `git rev-parse HEAD`; require it to match the fetched PR head, otherwise refresh acquisition. Done when the manifest exists and the reviewed commit and PR context are recorded.

**2. Load existing review comments**

Run `gh api --paginate repos/<OWNER>/<REPO>/pulls/<PR_NUMBER>/comments --jq '.[] | "File: \(.path)  Line: \(.line) OrigLine: \(.original_line)\nUser: \(.user.login)\nBody: \(.body)\n---"'`. Use results as dedup context only; report only new issues backed by fresh evidence.

**3. Load architecture documentation**

Locate existing architecture docs — overview, Crosscutting Concepts, ADRs — and read the overview and indexes into context.
- **Found:** keep loaded for the session; cross-reference every input against it.
- **Not found:** proceed on code evidence alone.

**4. Run parallel pre-review reports**

Set `SESSION_DIR` to `/memories/session/hitl-<OWNER>-<REPO>-<PR_NUMBER>/<COMMIT_ID>/`; create it before delegation. If session memory is unavailable, use the host's session artifact directory and retain its absolute path.

Spawn two fresh subagents in parallel, each with its own absolute instruction-reference path from this skill's base directory. Pass `PR_URL`, `OWNER/REPO#PR_NUMBER`, checkout root, `COMMIT_ID`, `bin/review_diff/` and manifest, PR title/body, existing comments, loaded architecture docs, and its absolute `OUTPUT_PATH`.

| Subagent | Instruction reference | Output in `SESSION_DIR` |
|---|---|---|
| Blast radius + unslop | [Blast-radius preparation](references/pre-review-blast-radius.md) | `blast-radius.md` |
| PR summary | [PR preparation](references/pre-review-pr.md) | `pr-summary.md` |

Both **MUST** start before waiting for either. Each reads its own reference and writes only its assigned report and temporary proof files; source edits, checkout changes, commits, pushes, PR edits, and comment posting are forbidden. Keep proof files in a task-specific temporary directory. Run only non-destructive local checks; report unavailable or unsafe execution as unproven. Subagents review the same recorded commit independently; neither consumes the other's output. If delegation is unavailable, report the blocker and stop preparation rather than substitute parent analysis.

Wait for both; verify each report exists, is nonempty, and identifies the PR and `COMMIT_ID`. On failure, save a failure report at that agent's output path with the blocker and label it failed, never clean. Reuse reports only for the same PR and commit. Recheck `git rev-parse HEAD` and `gh pr view <PR_URL> --json headRefOid`; if either differs from `COMMIT_ID`, refresh context and rerun both before review.

Show clickable Markdown links to both actual report files with completed/failed status before asking for review input. Use the host's file-link format, not bare paths; link files rather than instruction references. Retain reports for the session. A failed report stays visible while the human-led review proceeds on available evidence.

## Review loop

Repeat per user input: Get the input → Route → exactly one branch → back to Get the input.

### 1. Get the input

**STOP. Analyse no code yet.** Keep both pre-review report links available with their status. Ask: "Please paste the code change, feedback, context, or question you'd like reviewed." Wait for the reply; it is **the input** below.

### 2. Route

Classify the input, then follow exactly one branch:
- **Review branch** — user asks for a review or comment on a code change, or flags a suspected issue.
- **Inspect branch** — question on how something works, where it lives, who calls it, or other code research not yet a review finding.
- **Unclear** (incl. pasted code with no ask) — ask the user what they want; don't review.

### 3a. Review branch

Drafts, approves, and posts one review comment.

**1. Analyse**

1.1 **Anchor** — resolve from the input:
   - `FILE_PATH`: match the input to a file in `bin/review_diff/`, then take the real repo-relative path from `bin/review_diff/_manifest.tsv`; never derive it from the flattened filename. Ambiguous → ask the user.
   - `LINE_NUMBER`: from the diff (right-side new-file line; last line of a multi-line range). Undeterminable → ask the user.

1.2 **Evidence** — gather definitions, usages, callers; confirm the issue is real in actual code. **Default to an `Explore` subagent; reserve direct reads for anchor-precision.** `Explore` returns a condensed verdict, keeping raw tool output out of main context.
   - **Reuse findings:** check the pre-review reports for `COMMIT_ID` and `/memories/session/hitl-findings-<OWNER>-<REPO>-<PR_NUMBER>.md` first; reuse matching facts only when valid for the reviewed commit. Report findings remain candidates until this branch's evidence and dedup gates pass.
   - **Default — broad sweep → `Explore`:** wide or throwaway checks (pattern/exception/route elsewhere? who calls this? concern real across files?). Pass the input and `FILE_PATH`; consume only its summary — don't re-`view`/`grep` files it reported.
   - **Exception — anchor-precision → direct reads:** targeted `view` with `view_range`, or `grep`, only for exact lines/signatures/type hierarchy to quote or anchor the comment, evidence in a small known file set, or iteration on those files across turns. Read ranges, not whole files.
   - **Architecture lens** (docs loaded; input-scoped, never proactive): flag documented-rule violations (e.g., layering direction, module isolation, folder placement).
   - **Concepts and ADRs lens** (docs loaded; input-scoped, never proactive): open only Crosscutting Concepts and ADRs relevant to the touched surface; flag violations of their rules or decisions.

1.3 **Gate** — decide whether to draft:
   - No evidence → don't draft; report it couldn't be confirmed.
   - Already raised in an existing review comment → don't draft; cite that comment.
   - Architecture/Concept/ADR-only concern and change conforms → don't draft; report "conforms to the documented architecture — nothing to flag"; let the user decide. Correctness concerns pass on evidence alone.

**2. Draft**

2.1 `EXPLANATION` — why it matters (correctness, readability, performance, maintainability, etc.).

2.2 `IMPROVEMENT` — concrete fix or direction. Follow [Comment format](references/review-comment.md), resolved from this skill's base directory.

2.3 `REVIEW_COMMENT` — complete formatted posting body from `IMPROVEMENT`, without classification labels or prefixes.

**3. Human approval**

Show the comment and menu in this format; wait for the user's selection:

**Explanation:**
<EXPLANATION>

**Review comment:**
<REVIEW_COMMENT>

> Please review the comment above. What would you like to do?
> 1. Approve & review another code change
> 2. Approve & finish
> 3. Discard & review another code change
> 4. Discard & finish
>
> Or just type your feedback to revise the comment.

**4. Handle the reply**

On approval (1 or 2): follow [Posting](references/posting.md), resolved from this skill's base directory, with `FILE_PATH`, `LINE_NUMBER`, `REVIEW_COMMENT`, and the reviewed `COMMIT_ID` to post the inline PR comment. Capture the returned `COMMENT_ID`; add `{FILE_PATH, LINE_NUMBER, REVIEW_COMMENT, COMMENT_ID}` to the **posted queue**. Then, by reply:
- **1:** display the posted queue as a numbered list (`FILE_PATH:LINE_NUMBER — REVIEW_COMMENT (COMMENT_ID)` per item), then return to Get the input.
- **2:** clear the posted queue and end the session.
- **3:** drop the draft without posting; return to Get the input.
- **4** (or **done** with no selection): drop the draft without posting; clear the posted queue and end the session.
- **Otherwise** (revision feedback): wording-only → revise the **current** comment from Draft; disputes facts, line, or file → revise from Analyse. Re-present at Human approval.

### 3b. Inspect branch

Answers a code question; never drafts or posts.

1. **Explore:** delegate to a read-only `Explore` subagent. Pass the question, `OWNER/REPO#PR_NUMBER`, `bin/review_diff/`, and relevant architecture docs when loaded. Require `path:line` evidence per fact; list unverified items as unconfirmed. Thoroughness by question complexity:
   - `quick` — single symbol/file lookup (where is X, what does Y return).
   - `medium` — one flow or caller chain within one component.
   - `thorough` — cross-component flow, multiple call paths, or design/why questions.
2. **Record:** append to `/memories/session/hitl-findings-<OWNER>-<REPO>-<PR_NUMBER>.md` (create if missing):
```
## <question>
- <fact> — <path>:<line>
Unconfirmed: <item>  (omit when none)
```
3. **Present:** show the question and facts with evidence; return to Get the input.
4. **Escalate:** user asks to turn a finding into a comment → go to Review branch Analyse with the finding as input; use recorded facts as evidence.
