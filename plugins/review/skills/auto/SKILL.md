---
name: 'auto'
description: 'Perform a GitHub PR code review'
argument-hint: '<PR URL> (e.g., "https://github.com/owner/repo/pull/1245")'
---

# GitHub Code Review Instructions

<role> You are a **seasoned senior developer** performing a thorough code review.</role>

**Step 1 — Parse PR URL**
Parse the user input: `{{input}}`
Extract: <owner>, <repo>, and <pr_number> from <pr_url> in the format `https://github.com/{owner}/{repo}/pull/{number}`

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

**Step 5 — Run the shared LSP analysis pass**

**This is a hard gate — do not skip it.** `grep`, `view`, and `bash` are NOT substitutes for LSP. This runs **once, before the sub-agents**, and its result is shared with all of them.

Perform mandatory code analysis following `LSP Progressive Depth Code Analysis` framework from the `/lsp-depth-guidance` to inspect changed symbols before drawing review conclusions. Do not rely on the diff alone. 

**What to look for** — for every changed symbol, answer these fixed questions:
- **Contract** — what are the signature, return type, generics, nullability, and modifiers, and did the change alter the contract or only the body?
- **Dependents** — who calls or implements it, and does the change break any caller's assumptions?
- **Behavior** — do return/thrown/error paths, state transitions, or side effects change?
- **Polymorphism** — are overrides or interface implementations affected?

Go deeper (Level 2/3) using `LSP Progressive Depth Code Analysis` framework from the `/lsp-depth-guidance` on symbols that raise a **risk signal**: broken or narrowed caller contract, newly introduced nullability, changed thrown/returned/error behavior, wide cross-file fan-out, or shared-mutable/async state. Stay shallow (Level 1) where none of these apply.

Record the result as the **LSP summary** using the output contract in `<skill-directory>/references/lsp-summary.md` (per-symbol table + risk-flag list). It feeds the shared input payload in Step 6.

**Step 6 — Build the shared input payload and spawn the three axis agents in parallel**
Assemble one shared **input JSON payload** matching `<skill-directory>/references/io-schema.md` from:
- `pr` (owner, repo, number, url),
- `diff_dir` = `bin/review_diff/` and `changed_symbols` (Step 2/3),
- `existing_comments` (Step 3 — dedup context, do not restate),
- `lsp_summary` (Step 5),
- `spec` (Step 4; `null` if none found).

Send a single message with three `runSubagent` calls so the axes don't pollute each other's context. Pass `model` on each call matching your own model. Each sub-agent runs one of the axis skills in **spawned mode**, receiving the shared input JSON payload as its input:

- **quality-attributes** — run the `/quality-attributes` skill.
- **code-smells** — run the `/code-smells` skill.
- **requirements-coverage** — run the `/requirements-coverage` skill.

Each axis agent evaluates its own checklist, applies its own axis-specific review rules (which produce the two counts — total candidates vs. after-filter), and returns an **output JSON payload** with `violations`, `passed`, and `counts`. In spawned mode the agents return the payload only — they do **not** display or post.

**Step 7 — Aggregate the three output payloads**
Collect the three output JSON payloads and aggregate them following `<skill-directory>/references/aggregation.md`: keep axes separate, dedup violations against existing review comments (`file_path` + `line_number` + `label`), and roll up per-axis and total counts.

**Step 8 — Display both lists to the user**
Display the aggregated result to the user per `<skill-directory>/references/aggregation.md` — for each axis show its **violations** and its **passed** list, then the combined **counts** roll-up. The passed lists are display-only.

**Step 9 — Format violations**
For each carried-forward **violation**, map it to a comment body following the `/to-review-comment` skill. The `passed` lists are never posted.

**Step 10 — Post violations**
Post the violations as **inline pull-request review comments** by invoking the `/post-review-comment` skill with `{ pr, comments }` (one `comments` entry per violation: `file_path`, `line_number`, `body`).
