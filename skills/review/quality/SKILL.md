---
name: 'quality'
description: 'Perform a GitHub PR quality-attributes code review — correctness, reliability, compatibility, performance, testability.'
argument-hint: '<PR_URL>'
disable-model-invocation: true
---

# GitHub Quality-attributes Review Instructions

<role> You are a **seasoned senior developer** performing a thorough code review.</role>

**Concepts**
- **Review comment** — the improvement this review discovered and returns, anchored to the change (`AXIS`, `FILE_PATH`, `LINE_NUMBER`, `LABEL`), with its body in `REVIEW_COMMENT` phrased `issue → impact → fix`.

**Step 1 — Parse arguments**
Parse the user input: `{{input}}`, format `<PR_URL>`. Extract <OWNER>, <REPO>, <PR_NUMBER> from <PR_URL>.

**Step 2 — Fetch PR diff**
Run `/fetch-diff` skill (**MUST**) to check out the PR branch and fetch its diff into `bin/review_diff/` with `bin/review_diff/_manifest.tsv`. Report `FILE_PATH` from the manifest only — never a guessed or locally-resolved path.

**Step 3 — Load review context**
Retrieve existing review comments - `gh api repos/<OWNER>/<REPO>/pulls/<PR_NUMBER>/comments --jq '.[] | "File: \(.path)  Line: \(.line) OrigLine: \(.original_line)\nUser: \(.user.login)\nBody: \(.body)\n---"'`, Retrieve PR title, description - `gh pr view <PR_NUMBER> --json title,body --repo <OWNER>/<REPO>`.
Check PR title and description for 'What has been done?', `What files affected?`, `What is out of scope?` use during the review.

**Step 4 — Review the change**
Existing review comments are already-reviewed — do not re-validate, repeat, restate, or re-report them; use them only to avoid duplication and understand covered areas. Focus strictly on new issues with fresh code evidence.
*MUST Follow* `quality-review-guidance.md` *ALL* sections and steps to review the per-file diffs in `bin/review_diff/` against the quality-attributes checklist and its LSP workflow. Ground every conclusion in LSP analysis and code evidence, not the patch alone. Consider cross-symbol behavior and design intent.

**Step 5 — Collect findings**
Collect the findings as a JSON array of review-comment objects (`AXIS`, `FILE_PATH`, `LINE_NUMBER`, `LABEL`, `REVIEW_COMMENT`), per `quality-review-guidance.md`'s output contract. Deduplicate against existing review comments and drop anything already covered — match on `FILE_PATH` + `LINE_NUMBER` + `LABEL`. Carry forward only net-new, actionable review comments.

**Step 6 — Post review comments**
Post each review comment's `REVIEW_COMMENT` body as an **inline pull-request review comment** following the `/posting` skill, using the `FILE_PATH` exactly as recorded in `bin/review_diff/_manifest.tsv`.
