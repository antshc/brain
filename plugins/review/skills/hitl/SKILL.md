---
name: hitl
description: Interactive, human-approved PR code review — draft one comment at a time, get approval, queue it, then post all as inline PR comments.
argument-hint: '<PR URL> (e.g., "https://github.com/owner/repo/pull/1245")'
---
## Input
If `{{input}}` contains a GitHub PR URL <pr_url> in the format `https://github.com/{owner}/{repo}/pull/{number}`, extract `<owner>`, `<repo>`, and `<pr_number>` from it.
Otherwise, ask the user: *"Please provide the GitHub PR URL (https://github.com/{owner}/{repo}/pull/{number})."* and wait for the response before continuing.

## Fetch PR details
1. Run `gh pr checkout <pr_number> --repo <owner>/<repo>` to check out the PR branch locally.
2. Run the following command to fetch the diff per file into `bin/review_diff/` in the repository root.
```
rm -rf bin/review_diff && mkdir -p bin/review_diff &&
gh pr diff "<pr_url>" | awk -v outdir="bin/review_diff/" '
/^diff --git / {
  if (outfile) close(outfile)
  match($0, /b\/(.+)$/, arr)
  filepath = arr[1]
  gsub("/", "_", filepath)
  outfile = outdir "/" filepath
}
outfile { print > outfile }
'
```

**STOP. Do not analyse any code yet.**
Ask the user: *"Please paste the code change, feedback, or context you'd like reviewed."* and wait for the response before continuing.

## Review loop

Explore code using the `explore` agent in background if needed — to inspect related code, usages, or callers before commenting; otherwise rely on the provided snippet.

## Step 1. Analyse the input and suggest an improvement

1. Identify the issue — what is wrong, risky, or unclear? Be specific and factual.
2. Explain why it matters (<explanation>: { impact on correctness, readability, performance, maintainability, etc.}).
3. Suggest an improvement (<improvement>: { provide a concrete fix or direction. Format via `/to-review-comment`}).
4. Choose the label (<label>: { confirmed issue severe enough it must be fixed before merge → `blocking`; other confirmed correctness or compatibility issue → `bug`; improvement or likely risk worth fixing → `suggest`; minor note or polish → `nit`}).
5. Resolve the anchor for posting:
   - <FILE_PATH>: the changed file the snippet belongs to — match it against a file in `bin/review_diff/`; if ambiguous, ask the user.
   - <LINE_NUMBER>: the line on the PR's new side (`RIGHT`) the comment attaches to; if it cannot be determined from the diff, ask the user.
   - <REVIEW_COMMENT>: the posting body, composed as `<label>: <improvement>`.

## Step 2. Human approval — present the resulting comment with this menu and wait for the user to select:
- Show user for review using the format:

**Explanation:**
<explanation>

**Review comment:**
<label>: <improvement>

> Please review the comment above. What would you like to do?
> 1. Approve & review another code change
> 2. Approve & finish
> 3. Provide feedback to revise

## Step 3. Handle the reply
Do **NOT** post on approval of a single comment; accumulate a **pending queue** of approved review comments instead. Each queued item is `<review_comment>` with its `<file_path>` and `<line_number>`.
- If the user replied **1**, add the approved item to the pending queue **without posting**, then ask *"Please paste the next code change, feedback, or context you'd like reviewed."*, wait for the response, and return to Step 1.
- If the user replied **2** (or **done**), add the current approved item to the queue, then post **every** queued comment following the `/posting` skill (map `<file_path>` → `FILE_PATH`, `<line_number>` → `LINE_NUMBER`, `<review_comment>` → `REVIEW_COMMENT`), and end the session.
- If the user replied **3** or provides revision feedback, revise the **current** comment using the feedback and re-present it at Step 2.
