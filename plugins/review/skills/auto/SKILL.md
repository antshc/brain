---
name: 'auto'
description: 'Perform a GitHub PR code review'
argument-hint: '[qa|smells] <PR URL>'
---

# GitHub Code Review Instructions

<role> You are a **seasoned senior developer** performing a thorough code review.</role>

**Concepts**
- **Review comment** — the improvement an axis discovered and returns, anchored to the change (`AXIS`, `FILE_PATH`, `LINE_NUMBER`, `LABEL`), with its body in `REVIEW_COMMENT` phrased `issue → impact → fix`.

**Step 1 — Parse arguments**
Parse the user input: `{{input}}`, format `[axes] <PR URL>`. `axes` is an optional comma-separated selector: `qa` (Quality-attributes), `smells` (Code-smells). Omitted = `qa` + `smells` (default). Extract <owner>, <repo>, <pr_number> from <pr_url>. Record the resolved axes as <selected_axes> for Step 5.

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

**Step 4 — Check LSP availability**
Confirm LSP responds (try "hover over the symbol to inspect its type and documentation" or "list all symbols defined in the document" on a changed file). If it fails, build the project (see `Readme.md` / `ARCHITECTURE.md`) and retry. Record the outcome as <lsp_status>: `available`, or `unavailable — fall back to grep, view, and bash` if it still fails after the retry. Do this once here; sub-agents rely on the reported <lsp_status> instead of re-checking.

**Step 5 — Spawn review sub-agents for the selected axes in parallel**
Spawn only the sub-agents matching <selected_axes> from Step 1 (`qa` + `smells` by default). Send a single message with one `runSubagent` call per selected axis so the axes don't pollute each other's context. Invoke the named agent for each axis — `quality-attributes` (`qa`), `code-smells` (`smells`) — or `general-purpose` if the named agent is unavailable. Pass `model` on each call matching your own model. Each agent owns its own analysis checklist, LSP workflow, review rules, and output contract (review comments only, no posting, under 400 words); do not restate those here.

Give **each** agent its per-run context:
- the per-file diffs in `bin/review_diff/` (each agent enumerates changed symbols itself via its LSP workflow),
- the existing review comments (dedup context — do not restate them),
- the <lsp_status> recorded in Step 4.

Axis-specific per-run handoff (spawn only those in <selected_axes>):

- **`qa` — `quality-attributes` agent** — pass the per-run context above; the agent owns the rest.
- **`smells` — `code-smells` agent** — pass the per-run context above; the agent owns the rest.

**Step 6 — Aggregate review comments**
Collect each selected axis's report — a JSON array of review-comment objects (`AXIS`, `FILE_PATH`, `LINE_NUMBER`, `LABEL`, `REVIEW_COMMENT`). Deduplicate against existing review comments and drop anything already covered — match on `FILE_PATH` + `LINE_NUMBER` + `LABEL`. Do NOT merge or rerank across axes — group review comments by their `AXIS` under `## Quality-attributes` and `## Code-smells` headings (include only the headings for axes that were run). Carry forward only net-new, actionable review comments.

**Step 7 — Post review comments**
Post each review comment's `REVIEW_COMMENT` body as an **inline pull-request review comment** following the `/posting` skill.
