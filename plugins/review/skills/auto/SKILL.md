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

Record the result as the **LSP summary** using the output contract in `<skill-directory>/references/lsp-summary.md` (per-symbol table + risk-flag list). Pass this summary into every sub-agent in Step 6 to ground their change analysis.

**Step 6 — Spawn three review sub-agents in parallel**
Send a single message with three `runSubagent` (`general-purpose`) calls so the axes don't pollute each other's context. Pass `model` on each call matching your own model. Give **each** sub-agent:
- the per-file diffs in `bin/review_diff/` and the changed-symbol list,
- the existing review comments (dedup context — do not restate them),
- the shared **LSP summary** from Step 5,
- the shared review rules in `<skill-directory>/references/review-rules.md` (evidence, scope, and deduplication rules that bind every axis),
- the shared finding format in `<skill-directory>/references/finding-format.md` (every axis returns findings in this schema),
- the instruction: "Use `LSP Progressive Depth Code Analysis` framework from the `/lsp-depth-guidance` skill as your **preferred** way to navigate code; fall back to other tools (`grep`, `view`, `bash`) only if the LSP server is unavailable."

Each sub-agent returns findings only — it does **not** post. Every axis emits findings in the shared schema from `<skill-directory>/references/finding-format.md`. The three axes:

- **Quality-attributes sub-agent** — evaluate the change against `<skill-directory>/references/quality-attributes.md`. For each area, conclude confirmed issue / plausible risk / no issue found. Report only net-new findings grounded in code evidence. Under 400 words.
- **Code-smells sub-agent** — match the diff against the code smell baseline in `<skill-directory>/references/code-smells.md`. Name each smell and quote the hunk. These are judgement calls, not hard violations; skip anything CI tooling enforces. Under 400 words.
- **Requirements-coverage sub-agent** — using the spec from Step 4, report: (a) requirements that are missing or partial; (b) behavior in the diff that wasn't asked for (scope creep); (c) requirements that look implemented but wrong. Quote the spec line for each finding. If no spec was found, report "no spec available" and stop. Under 400 words.

**Step 7 — Aggregate findings**
Collect the three reports, each in the shared finding schema. Deduplicate against existing review comments and drop anything already covered — match on `FILE_PATH` + `LINE_NUMBER` + `LABEL`. Do NOT merge or rerank across axes — keep them separate under `## Quality-attributes`, `## Code-smells`, and `## Requirements-coverage`. Carry forward only net-new, actionable findings.

**Step 8 — Format findings**
Each carried-forward finding is already in the shared schema (`<skill-directory>/references/finding-format.md`); map it to a comment following the `/to-review-comment` skill.

**Step 9 — Post findings**
Post each finding as an **inline pull-request review comment** following `<skill-directory>/references/posting.md`.
