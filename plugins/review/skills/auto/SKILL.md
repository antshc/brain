---
name: 'auto'
description: 'Perform a GitHub PR code review'
argument-hint: '[qa|smells|reqs] <PR URL>'
---

# GitHub Code Review Instructions

<role> You are a **seasoned senior developer** performing a thorough code review.</role>

**Step 1 — Parse arguments**
Parse the user input: `{{input}}`, format `[axes] <PR URL>`. `axes` is an optional comma-separated selector: `qa` (Quality-attributes), `smells` (Code-smells), `reqs` (Requirements-coverage). Omitted = `qa` + `smells` (default); `reqs` runs only when explicitly requested. Extract <owner>, <repo>, <pr_number> from <pr_url>. Record the resolved axes as <selected_axes> for Step 5.

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

**Step 4 — Identify the spec source** *(only when `reqs` is in <selected_axes>; otherwise skip this step)*
Look for the originating spec, in this order:
1. Issue references in the commit messages or PR body (`#123`, `Closes #45`, etc.) — fetch with `gh issue view <number> --repo <owner>/<repo> --json title,body`.
2. A path the user passed as an argument.
3. A PRD/spec file under `docs/`, `specs/`, or `.scratch/` matching the branch name or feature.
4. If nothing is found, the **Requirements-coverage** sub-agent will skip and report "no spec available".

**Step 5 — Spawn review sub-agents for the selected axes in parallel**
Spawn only the sub-agents matching <selected_axes> from Step 1 (`qa` + `smells` by default). Send a single message with one `runSubagent` call per selected axis so the axes don't pollute each other's context. Invoke the named agent for each axis — `quality-attributes` (`qa`), `code-smells` (`smells`), `requirements-coverage` (`reqs`) — or `general-purpose` if the named agent is unavailable. Pass `model` on each call matching your own model. Each agent owns its own analysis checklist, LSP workflow, review rules, and output contract (findings only, no posting, under 400 words); do not restate those here.

Give **each** agent its per-run context:
- the per-file diffs in `bin/review_diff/` (each agent enumerates changed symbols itself via its LSP workflow),
- the existing review comments (dedup context — do not restate them).

Axis-specific per-run handoff (spawn only those in <selected_axes>):

- **`qa` — `quality-attributes` agent** — pass the per-run context above; the agent owns the rest.
- **`smells` — `code-smells` agent** — pass the per-run context above; the agent owns the rest.
- **`reqs` — `requirements-coverage` agent** — pass the per-run context above, plus the full spec text identified in Step 4 under a `## Spec` heading. If no spec was found in Step 4, pass none and the agent will report "no spec available" and stop.

**Step 6 — Aggregate findings**
Collect the reports from the selected axes, each in the shared finding schema. Deduplicate against existing review comments and drop anything already covered — match on `FILE_PATH` + `LINE_NUMBER` + `LABEL`. Do NOT merge or rerank across axes — keep them separate under `## Quality-attributes`, `## Code-smells`, and `## Requirements-coverage` headings (include only the headings for axes that were run). Carry forward only net-new, actionable findings.

**Step 7 — Post findings**
Post each finding's `FINDING_BODY` as an **inline pull-request review comment** following the `/posting` skill.
