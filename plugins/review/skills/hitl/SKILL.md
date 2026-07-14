---
name: hitl
description: Draft a clear, actionable code review comment.
argument-hint: '<PR URL> (e.g., "https://github.com/owner/repo/pull/1245")'
---
**Step 1 — PR URL**
If `{{input}}` contains a GitHub PR URL <pr_url> in the format `https://github.com/{owner}/{repo}/pull/{number}`, extract `<owner>`, `<repo>`, and `<pr_number>` from it.
Otherwise, ask the user: *"Please provide the GitHub PR URL (https://github.com/{owner}/{repo}/pull/{number})."* and wait for the response before continuing.

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

**Step 3 — Review loop**
**STOP. Do not analyse any code yet.**
Ask the user: *"Please paste the code change, feedback, or context you'd like reviewed."* and wait for the response before continuing.

**Step 3a. Review process** — analyse the input:
1. Identify the issue — what is wrong, risky, or unclear? Be specific and factual.
2. Explain why it matters — impact on correctness, readability, performance, or maintainability.
3. Suggest improvement — provide a concrete fix or direction. Keep it practical.
4. Keep it concise — short, direct sentences, no unnecessary wording.
5. Explore code if needed — if the issue depends on external context, run `/lsp-navigation` skill to inspect related code, usages, or callers before commenting; otherwise rely on the provided snippet.

**Step 3b. Human approval** — draft the comment following `<skill-directory>/references/comment-template.md`, then present it with this menu and wait for the user to select:

> Please review the comment above. What would you like to do?
> 1. Approve & review another code change
> 2. Approve & finish
> 3. Provide feedback to revise

- If the user replies **3** or provides revision feedback, revise the comment and repeat 3b.

**Step 3c. Post** — if the user replied **1** or **2**, post the comment following `<skill-directory>/references/posting.md`.

**Step 3d. Continue** — after posting:
- If the user replied **1**, return to 3a.
- If the user replied **2** or **done**, end the session.
