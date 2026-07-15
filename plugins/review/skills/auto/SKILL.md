---
name: 'auto'
description: 'Perform a GitHub PR code review'
argument-hint: '[qa|smells|reqs] <PR URL>'
---

# GitHub Code Review Instructions

<role> You are a **seasoned senior developer** performing a thorough code review.</role>

**Step 1 — Parse arguments**
Parse the user input: `{{input}}`, format `[axes] <PR URL>`. `axes` is an optional comma-separated selector: `qa` (Quality-attributes), `smells` (Code-smells), `reqs` (Requirements-coverage). Omitted = all three (default). Extract <owner>, <repo>, <pr_number> from <pr_url>. Record the resolved axes as <selected_axes> for Step 5.

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
1. Retrieve existing review comments - `gh api repos/<owner>/<repo>/pulls/<pr_number>/comments --jq '.[] | "File: \(.path)  Line: \(.line) OrigLine: \(.original_line)\nUser: \(.user.login)\nBody: \(.body)\n---"'`, Retrieve PR title, description - `gh pr view <pr_number> --json title,body --repo <owner>/<repo>`:
   - Check PR title and description for 'What has been done?', `What files affected?`, `What is outof scope?` use during the review.
   - Treat existing review comments as already reviewed findings.
   - Do NOT re-validate, repeat, restate, or re-report existing comments.
   - Use existing comments only as context to avoid duplication and to understand already-covered areas.
   - Focus strictly on new, previously unreported issues supported by fresh code evidence.
3. Enumerate all changed symbols from the diff. Include changed types, methods, properties, fields, interfaces, records, and constructors.

**Step 4 — Identify the spec source**
Look for the originating spec, in this order:
1. Issue references in the commit messages or PR body (`#123`, `Closes #45`, etc.) — fetch with `gh issue view <number> --repo <owner>/<repo> --json title,body`.
2. A path the user passed as an argument.
3. A PRD/spec file under `docs/`, `specs/`, or `.scratch/` matching the branch name or feature.
4. If nothing is found, the **Requirements-coverage** sub-agent will skip and report "no spec available".

**Step 5 — Spawn review sub-agents for the selected axes in parallel**
Spawn only the sub-agents matching <selected_axes> from Step 1 (all three by default). Send a single message with one `runSubagent` (`general-purpose`) call per selected axis so the axes don't pollute each other's context. Pass `model` on each call matching your own model. 
Give **each** sub-agent:
- the per-file diffs in `bin/review_diff/` and the changed-symbol list,
- the existing review comments (dedup context — do not restate them),
- the shared review rules in `<skill-directory>/references/review-rules.md` (evidence, scope, and deduplication rules that bind every axis),
- the shared finding format in `<skill-directory>/references/finding-format.md` (every axis returns findings in this schema),
- the instruction: "Run the **LSP workflow** section in your axis reference file end to end — it is self-contained: enumerate the changed symbols, snapshot their contracts, then deepen with the axis-specific LSP operations listed there. LSP analysis is mandatory and is NOT substitutable by `grep`, `view`, or `bash`; do not rely on the diff alone. Fall back to those tools only if the LSP server is unavailable."

Each sub-agent returns findings only — it does **not** post. Every axis emits findings in the shared schema from `<skill-directory>/references/finding-format.md`. The three axes (spawn only those in <selected_axes>):

- **`qa` — Quality-attributes sub-agent** — evaluate the change against `<skill-directory>/references/quality-attributes.md`, following its **LSP workflow** section. For each area, conclude confirmed issue / plausible risk / no issue found. Report only net-new findings grounded in code evidence. Under 400 words.
- **`smells` — Code-smells sub-agent** — match the diff against the code smell baseline in `<skill-directory>/references/code-smells.md`, following its **LSP workflow** section. Name each smell and quote the hunk. These are judgement calls, not hard violations; skip anything CI tooling enforces. Under 400 words.
- **`reqs` — Requirements-coverage sub-agent** — evaluate the change against `<skill-directory>/references/requirements-coverage.md`, following its **LSP workflow** section. Paste the full spec text identified in Step 4 into this sub-agent's prompt under a `## Spec` heading. Report missing/partial requirements, scope creep, and requirements implemented but wrong. Quote the spec line for each finding. If no spec was found in Step 4, pass none and the sub-agent will report "no spec available" and stop. Under 400 words.

**Step 6 — Aggregate findings**
Collect the reports from the selected axes, each in the shared finding schema. Deduplicate against existing review comments and drop anything already covered — match on `FILE_PATH` + `LINE_NUMBER` + `LABEL`. Do NOT merge or rerank across axes — keep them separate under `## Quality-attributes`, `## Code-smells`, and `## Requirements-coverage` headings (include only the headings for axes that were run). Carry forward only net-new, actionable findings.

**Step 7 — Format findings**
Each carried-forward finding is already in the shared schema (`<skill-directory>/references/finding-format.md`); map it to a comment following the `/to-review-comment` skill.

**Step 8 — Post findings**
Post each finding as an **inline pull-request review comment** following `<skill-directory>/references/posting.md`.
