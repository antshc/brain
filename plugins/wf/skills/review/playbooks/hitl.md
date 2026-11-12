# Review assistant

Act as **senior-developer review support**: the human leads the review and decides what to examine and what deserves a comment; answer their questions and verify and draft their findings against the code and architecture docs. Act only on user input; enter Review branch only when the user asks for a review or comment. **MUST NOT** review, critique, or summarize the PR diff on own initiative.

**MUST NOT** use question tools (e.g. `ask_user`, ask-questions); every question and menu in this skill is plain chat text, then wait for the reply.

**References:** resolve each reference from the review skill directory (the directory containing `SKILL.md`); **MUST NOT** search for it (glob, grep, or find) from the filesystem root or the repo root, or fall back to the CWD.

## Input

Parse `{{input}}` as `PR_URL` (`https://github.com/{{OWNER}}/{{REPO}}/pull/{{PR_NUMBER}}`); extract `OWNER`, `REPO`, `PR_NUMBER`.

If `{{input}}` is empty, ask: "Please provide the GitHub PR URL (https://github.com/{OWNER}/{REPO}/pull/{PR_NUMBER})." Wait for the reply.

## Prepare review context

Run once per session, before Review loop. Steps 1 to 3 complete before step 4.

**1. Fetch PR details**

If `git status --porcelain` is non-empty, stop and ask the user before checkout.

*Load and follow the `github` skill to read pull requests and review evidence* using Pull requests, Diff, HITL setup to check out the PR branch and build the per-file diff and manifest under `bin/review_diff/`. Use the returned `DIFF_DIR`, `MANIFEST`, and `COMMIT_ID`. Done when the manifest exists and the reviewed commit is recorded.

**2. Load existing review comments**

Use `GH_TOOL pr snapshot OWNER/REPO#PR_NUMBER --inline` for paginated dedup context. Report only new findings.

**3. Load architecture documentation**

Locate existing architecture docs — overview, Crosscutting Concepts, ADRs — and read the overview and indexes into context.
- **Found:** keep loaded for the session; cross-reference every input against it.
- **Not found:** proceed on code evidence alone.

**4. Run changes brief**

Runs on the user's behalf despite the on-initiative restriction; the human reads the output, the assistant does not summarize it.

Set `@diffSize` to `additions + deletions` from `GH_TOOL pr snapshot OWNER/REPO#PR_NUMBER`. Set `@agentSize` from `@diffSize`:

| `@diffSize` | `@agentSize` |
|---|---|
| under 200 | small: fastest, cheapest model |
| 200 to 1000 | medium: standard model |
| over 1000 | large: most capable model available |

Launch one Changes brief subagent at `@agentSize`. Pass `OWNER`, `REPO`, `PR_NUMBER`, `PR_URL`, `DIFF_DIR` and `MANIFEST`, and the loaded architecture docs. It is read-only on the codebase and writes only its output file.

Follow [Changes brief](../references/changes-brief.md) for the PR change. Write the result to `bin/review/{{OWNER}}-{{REPO}}-{{PR_NUMBER}}/pr-{{PR_NUMBER}}-changes-brief.md`.

Pass the subagent the absolute path of the reference file under this skill's `references/` folder; it opens that path directly and does not search for it. It writes the reference's reply verbatim to its output file, creating the folder if missing, and returns only the absolute output path plus `done` or `failed: <reason>`.

Then show the user one Markdown link to the output file (absolute path, `/` separators) and the line "Open and read this before the review." Failed subagent → show its reason in place of the link. Done when the file exists or a reason is shown; do not read, summarize, or critique it. Continue to Review loop without waiting for the user to finish reading.

## Review loop

Repeat per user input: Get the input → Route → exactly one branch → back to Get the input.

### 1. Get the input

**STOP. Analyse no code yet.** Ask: "Please paste the code change, feedback, context, or question you'd like reviewed." Wait for the reply; it is **the input** below.

### 2. Route

Classify the input, then follow exactly one branch:
- **Review branch** — user asks for a review or comment on a code change, or flags a suspected issue.
- **Inspect branch** — question on how something works, where it lives, who calls it, or other code research not yet a review finding.
- **Unclear** (incl. pasted code with no ask) — ask the user what they want; don't review.

### 3a. Review branch

Drafts, approves, and posts one review comment.

**1. Analyse**

1.1 **Anchor** — resolve from the input:
   - `FILE_PATH`: match the input to a patch in `DIFF_DIR`, then take the real repo-relative path from `MANIFEST`. Ambiguous → ask the user.
   - `LINE_NUMBER`: from the diff (right-side new-file line; last line of a multi-line range). Undeterminable → ask the user.

1.2 **Evidence** — gather definitions, usages, callers; confirm the issue is real in actual code. **Default to an `Explore` subagent; reserve direct reads for anchor-precision.** `Explore` returns a condensed verdict, keeping raw tool output out of main context.
   - **Reuse findings:** if `/memories/session/hitl-findings-<OWNER>-<REPO>-<PR_NUMBER>.md` exists, check it first; use matching facts instead of re-exploring.
   - **Default — broad sweep → `Explore`:** wide or throwaway checks (pattern/exception/route elsewhere? who calls this? concern real across files?). Pass the input and `FILE_PATH`; consume only its summary — don't re-`view`/`grep` files it reported.
   - **Exception — anchor-precision → direct reads:** targeted `view` with `view_range`, or `grep`, only for exact lines/signatures/type hierarchy to quote or anchor the comment, evidence in a small known file set, or iteration on those files across turns. Read ranges, not whole files.
   - **Architecture lens** (docs loaded; input-scoped, never proactive): flag documented-rule violations (e.g., layering direction, module isolation, folder placement).
   - **Concepts and ADRs lens** (docs loaded; input-scoped, never proactive): open only Crosscutting Concepts and ADRs relevant to the touched surface; flag violations of their rules or decisions.

1.3 **Gate** — decide whether to draft:
   - No evidence → don't draft; report it couldn't be confirmed.
   - Already raised in an existing review comment → don't draft; cite that comment.
   - Architecture/Concept/ADR-only concern and change conforms → don't draft; report "conforms to the documented architecture — nothing to flag"; let the user decide. Correctness concerns pass on evidence alone.

**2. Draft**

*Load and follow the `github` skill to draft review threads and pull request comments using Reviews* with kind `finding`, ownership `human`, stage `draft`, and verified evidence. Neither the WF plugin nor a standalone `github` install available → stop and report missing access.

2.1 `EXPLANATION` — why it matters (correctness, readability, performance, maintainability). Apply the comment's Tone rules; its wording carries into the drafted body.

2.2 `IMPROVEMENT` — concrete fix or direction, offered as an option. Draft the comment, then run the Reviews unslop pass over `EXPLANATION` and the body. *Done when* the pass ran and no command, prohibition, or judgmental qualifier remains in either.

2.3 `REVIEW_COMMENT` — the complete returned human-owned body. Keep it unmarked for manual closure; agent drafting does not transfer ownership.

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

On approval (1 or 2): follow [Posting](../references/posting.md#hitl), with `FILE_PATH`, `LINE_NUMBER`, `REVIEW_COMMENT`, and the reviewed `COMMIT_ID` to post the approved body unchanged, without appending metadata. Capture the returned `COMMENT_ID`; add `{FILE_PATH, LINE_NUMBER, REVIEW_COMMENT, COMMENT_ID}` to the **posted queue**. Then, by reply:
- **1:** display the posted queue as a numbered list (`FILE_PATH:LINE_NUMBER — REVIEW_COMMENT (COMMENT_ID)` per item), then return to Get the input.
- **2:** clear the posted queue and end the session.
- **3:** drop the draft without posting; return to Get the input.
- **4** (or **done** with no selection): drop the draft without posting; clear the posted queue and end the session.
- **Otherwise** (revision feedback): wording-only → revise the **current** comment from Draft; disputes facts, line, or file → revise from Analyse. Re-present at Human approval.

### 3b. Inspect branch

Answers a code question; never drafts or posts.

1. **Research:** check `/memories/session/hitl-findings-<OWNER>-<REPO>-<PR_NUMBER>.md` first; answer from matching facts. Otherwise *Load and follow the `research` skill to investigate primary sources and return cited findings* on the checked-out PR head. Pass the question as `@question`, plus `OWNER/REPO#PR_NUMBER`, `DIFF_DIR`, `MANIFEST`, and relevant architecture docs when loaded. Require `path:line` evidence per fact; list unverified items as unconfirmed. Route by question:
   - **Lookup** — where is X, who calls Y, what does Z return: pure lookup; no document; research returns Hunter's verdict inline.
   - **How** — flow, mechanism, or behavior across files or components: default Research; set `@outputPath` to `bin/review/{{OWNER}}-{{REPO}}-{{PR_NUMBER}}/inspect/{{slug}}.md` and `@outputBase` to the checked-out repository root. Keep content framing in `@outputShape`.
   - **Why** — design rationale or what led to the change: **Why code anchor** (`@mode=why`, `@whyDepth=anchor`), returned inline; use full Why only when the user asks for rationale beyond code, commits, and PRs.

   Done when research returns cited facts, a saved path, or a named blocker.
2. **Record:** append to `/memories/session/hitl-findings-<OWNER>-<REPO>-<PR_NUMBER>.md` (create if missing):
```
## <question>
- <fact> — <path>:<line>
Report: <saved path>  (omit when none)
Unconfirmed: <item>  (omit when none)
```
3. **Present:** show the question and facts with evidence; for a saved report, add one Markdown link to it (absolute path, `/` separators). Return to Get the input.
4. **Escalate:** user asks to turn a finding into a comment → go to Review branch Analyse with the finding as input; use recorded facts as evidence.
