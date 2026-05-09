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

**Step 3 — Perform a deep code review**
You MUST use the C# LSP / code analysis tools before drawing conclusions. Do not rely on the diff alone.

  **Workflow**
  1. Load existing review context
    - Retrieve existing review comments `gh api repos/<owner>/<repo>/pulls/<pr_number>/comments --jq '.[] | "File: \(.path)  Line: \(.line) OrigLine: \(.original_line)\nUser: \(.user.login)\nBody: \(.body)\n---"'`
    - Check PR title, description for context `gh pr view <pr_number> --json title,body --repo <owner>/<repo>`
    - Treat existing review comments as already reviewed findings.
    - Do NOT re-validate, repeat, restate, or re-report existing comments.
    - Use existing comments only as context to avoid duplication and to understand already-covered areas.
    - Focus strictly on new, previously unreported issues supported by fresh code evidence.

  2. First, enumerate all changed symbols from the diff. Include changed types, methods, properties, fields, interfaces, records, and constructors.

  3. For every changed symbol, perform mandatory code analysis following `<skill-directory>/references/lsp-analysis.md`.

     **This is a hard gate — do not skip it.** `grep`, `view`, and `bash` are NOT substitutes for LSP. You must make actual LSP tool calls for each changed symbol before forming any conclusions. If the LSP server is unavailable, state that explicitly; do not silently fall back to text search.

     After completing LSP analysis for all symbols, write a brief internal summary of what the LSP calls revealed (types, nullability, caller shape) before moving on.

  4. Only after the LSP analysis is complete for all changed symbols, evaluate the change for:
    - correctness, bugs, and business logic
    - edge cases, invalid state, nullability, and missing guards
    - exception handling, silent failures, fallback behavior, retries, cancellation, and error propagation
    - broken callers, contracts, interfaces, overrides, and assumptions
    - serialized shapes and backward compatibility for existing callers or consumers
    - async correctness, task handling, cancellation propagation, and synchronization
    - thread-safety, race conditions, and shared mutable state
    - cross-symbol invariants, state transitions, and partial-failure behavior
    - DI/config/runtime wiring only when activation or runtime behavior may break
    - performance only when the change may materially affect hot paths, I/O patterns, allocations, query shape, or work amplification
    - which existing tests cover the changed behavior, and whether any uncovered high-risk scenario matters to correctness or compatibility
    - for each area, conclude one of: confirmed issue, plausible risk, or no issue found

    **Review rules**
    - Ground conclusions on sufficient and relevant repository-wide `<skill-directory>/references/lsp-analysis.md`, not on the patch alone and not on exhaustive exploration.
    - Review the changes as a whole, including cross-symbol behavior and the likely design intent.
    - Do not report speculative issues. Report only findings supported by specific code evidence.
    - Treat existing review comments as already-covered review context for deduplication. Do not restate or rephrase them.
    - Do not re-open the same finding unless the current diff introduces materially new evidence, a different root cause, or a broader impact that was not previously reported.
    - Report only net-new, actionable findings that are not already covered by existing review comments.
    - For each evaluated area, conclude one of: confirmed issue, plausible risk, or no issue found.

**Step 4 — Format findings**
Format each finding following `<skill-directory>/references/comment-template.md`.

**Step 5 — Post findings**
Post each finding as an **inline pull-request review comment** following `<skill-directory>/references/posting.md`.
