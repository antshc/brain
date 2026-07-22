---
name: 'reqs'
description: 'Perform a GitHub PR requirements-coverage review'
argument-hint: '<PR URL>'
disable-model-invocation: true
---

# GitHub Requirements-coverage Review Instructions

<role> You are a **seasoned senior developer** performing a thorough requirements-coverage code review.</role>

**Step 1 — Parse arguments**
Parse the user input: `{{input}}`, format `<PR URL>`. Extract <owner>, <repo>, <pr_number> from <pr_url>.

**Step 2 — Fetch PR diff**
Run the `/fetch-diff` skill (**MUST**) to check out the PR branch and fetch its diff into `bin/review_diff/` with `bin/review_diff/_manifest.tsv`. Report `FILE_PATH` from the manifest only — never a guessed or locally-resolved path.

**Step 3 — Load review context**
Retrieve existing review comments - `gh api repos/<owner>/<repo>/pulls/<pr_number>/comments --jq '.[] | "File: \(.path)  Line: \(.line) OrigLine: \(.original_line)\nUser: \(.user.login)\nBody: \(.body)\n---"'`, Retrieve PR title, description - `gh pr view <pr_number> --json title,body --repo <owner>/<repo>`:
1. Check PR title and description for 'What has been done?', `What files affected?`, `What is out of scope?` use during the review.
2. Treat existing review comments as already-reviewed comments.
3. Do NOT re-validate, repeat, restate, or re-report existing comments.
4. Use existing comments only as context to avoid duplication and to understand already-covered areas.
5. Focus strictly on new, previously unreported issues supported by fresh code evidence.

**Step 4 — Identify the spec source**
Look for the originating spec, in this order:
1. Issue references in the PR body:
  - Github issue (`#123`, `Closes #45` etc.) — fetch with `gh issue view <number> --repo <owner>/<repo> --json title,body`.
  - Jira issue (`PROJ-1234`) — fetch with atlassian mcp.
2. A path the user passed as an argument.
3. A PRD/spec file under `docs/`, `specs/`, or `.scratch/` matching the branch name or feature.
4. If nothing is found, skip Step 5's review and report "no spec available".

**Step 5 — Review the change**
Existing review comments are already-reviewed — do not re-validate, repeat, restate, or re-report them; use them only to avoid duplication and understand covered areas. Focus strictly on new issues with fresh code evidence. 
*MUST Follow* `reqs-review-guidance.md` *ALL* sections and steps, to evaluate the per-file diffs in `bin/review_diff/` against the spec text identified in Step 4. Ground every conclusion in the spec text and specific code evidence, not the patch alone. If no spec was found in Step 4, report "no spec available" and stop.

**Step 6 — Collect findings**
Collect the findings as a JSON array of review-comment objects (`AXIS`, `FILE_PATH`, `LINE_NUMBER`, `LABEL`, `REVIEW_COMMENT`), per `reqs-review-guidance.md`'s output contract. Deduplicate against existing review comments and drop anything already covered — match on `FILE_PATH` + `LINE_NUMBER` + `LABEL`. Carry forward only net-new, actionable review comments.

**Step 7 — Post review comments**
Post each review comment's `REVIEW_COMMENT` body as an **inline pull-request review comment** following the `/posting` skill, using the `FILE_PATH` exactly as recorded in `bin/review_diff/_manifest.tsv`.
