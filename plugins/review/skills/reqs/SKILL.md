---
name: 'reqs'
description: 'Perform a GitHub PR requirements-coverage review'
argument-hint: '<PR URL>'
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
2. Treat existing review comments as already reviewed findings.
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

**Step 5 — Check LSP availability**
Confirm LSP responds (try "hover over the symbol to inspect its type and documentation" or "list all symbols defined in the document" on a changed file). If it fails, build the project (see `Readme.md` / `ARCHITECTURE.md`) and retry. Record the outcome as <lsp_status>: `available`, or `unavailable — fall back to grep, view, and bash` if it still fails after the retry.

**Step 6 — Spawn the requirements-coverage sub-agent**
Invoke the `requirements-coverage` agent via `runSubagent` (or `general-purpose` if the named agent is unavailable), passing `model` matching your own model. The agent owns its own analysis checklist, LSP workflow, review rules, and output contract (findings only, no posting, under 400 words); do not restate those here.

Give the agent its per-run context:
- the per-file diffs in `bin/review_diff/` (the agent enumerates changed symbols itself via its LSP workflow),
- the existing review comments (dedup context — do not restate them),
- the <lsp_status> recorded in Step 5,
- the full spec text identified in Step 4 under a `## Spec` heading. If no spec was found in Step 4, pass none and the agent will report "no spec available" and stop.

**Step 7 — Aggregate findings**
Collect the report in the shared finding schema. Deduplicate against existing review comments and drop anything already covered — match on `FILE_PATH` + `LINE_NUMBER` + `LABEL`. Present the report under a `## Requirements-coverage` heading. Carry forward only net-new, actionable findings.

**Step 8 — Post findings**
Post each finding's `FINDING_BODY` as an **inline pull-request review comment** following the `/posting` skill.
