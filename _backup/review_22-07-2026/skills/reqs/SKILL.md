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

**Step 2 — Fetch PR details**
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
4. If nothing is found, the **Requirements-coverage** sub-agent will skip and report "no spec available".

**Step 5 — Spawn the requirements-coverage sub-agent**
Invoke the `requirements-coverage` agent via `runSubagent` (or `general-purpose` if the named agent is unavailable), passing `model` matching your own model. The agent owns its own analysis checklist, LSP workflow, review rules, and output contract (review comments only, no posting, under 400 words); do not restate those here.

Give the agent its per-run context:
- the per-file diffs in `bin/review_diff/` (the agent enumerates changed symbols itself via its LSP workflow),
- the existing review comments (dedup context — do not restate them),
- the full spec text identified in Step 4 under a `## Spec` heading. If no spec was found in Step 4, pass none and the agent will report "no spec available" and stop.

**Step 6 — Aggregate review comments**
Collect the report in the shared review-comment schema. Deduplicate against existing review comments and drop anything already covered — match on `FILE_PATH` + `LINE_NUMBER` + `LABEL`. Present the report under a `## Requirements-coverage` heading. Carry forward only net-new, actionable review comments.

**Step 7 — Post review comments**
Post each review comment's `REVIEW_COMMENT` body as an **inline pull-request review comment** following the `/posting` skill.
