---
name: code-review
description: 'Reviews a GitHub pull request for quality attributes, code smells, and ticket requirements in separate subagents, deduplicates findings, and posts actionable inline review comments. Use for PR code review, design smells, and requirements coverage.'
argument-hint: '<PR_URL>'
disable-model-invocation: true
---

# Code review

## Workflow

1. Parse `<PR_URL>` into `OWNER`, `REPO`, `PR_NUMBER`. Follow [Fetch PR diff](references/fetch-diff.md), resolved from this skill's base directory, to check out the PR branch and fetch its diff with a path manifest. Continue only when `bin/review_diff/_manifest.tsv` and its per-file diffs are available.
2. Fetch the PR title, body, and head commit with `gh pr view PR_NUMBER --repo OWNER/REPO --json title,body,headRefOid`. Fetch all existing inline comments with `gh api --paginate repos/OWNER/REPO/pulls/PR_NUMBER/comments`. Retain paths, current/original lines, and bodies. Use the PR's stated work, affected files, and exclusions as scope context.
3. Resolve the requirements gate in the parent before spawning reviewers. Inspect **only the PR body** for ticket references:
   - GitHub issue numbers, qualified `owner/repo#number` references, or issue URLs: fetch the referenced issue's `title,body` with `gh issue view`; use the referenced repository, defaulting to the PR repository for bare numbers.
   - Jira keys or issue URLs: *Run `fetch-work` skill to fetch the Jira work item as Markdown*, retaining its description separately from comments and other fields.
   - A ticket qualifies only when fetched successfully and its description contains non-whitespace content; for ADF, require nonempty description content, not merely a non-null document wrapper. Title, comments, and metadata do not substitute for a description. Pass every qualifying ticket's identity and full description to the requirements reviewer.
   - **Spawn requirements coverage only if at least one ticket mentioned in the PR body qualifies.** Otherwise record `skipped` with the reason: no ticket reference, empty description, or fetch unavailable/failed. Continue quality and code-smells reviews. Do not substitute title/branch references, user-provided spec paths, or local spec files.
4. Spawn one read-only subagent per eligible axis, in parallel. Give each the repository path, diff directory and manifest, PR context, existing comments, the shared review contract below, and the absolute path to its axis reference, resolved from this skill's base directory. Each reviews the complete change for its own axis and returns JSON with posting-ready comments formatted under its axis reference's Comment format section. Subagents must not fetch/check out the diff again, edit source, or post comments.

   | Axis | Spawn condition | Reference and extra input |
   |---|---|---|
   | `quality-attributes` | Always | [Quality rules](references/quality-review-guidance.md) |
   | `code-smells` | Always | [Code-smells rules](references/smells-review-guidance.md) |
   | `requirements-coverage` | Step 3 gate passes | [Requirements rules](references/reqs-review-guidance.md); qualifying ticket descriptions |

5. Collect each result; record failure objects separately from successful findings arrays. Validate the output contract, axis-specific comment format, and diff anchors; return malformed findings to their reviewer for correction before posting. Deduplicate against existing comments and across axes by issue/root cause; use `FILE_PATH` + `LINE_NUMBER` to locate candidate duplicates, not to merge unrelated issues sharing a line. Keep only net-new, actionable findings.
6. In the parent, post each retained `REVIEW_COMMENT` verbatim using [Posting](references/posting.md), resolved from this skill's base directory; do not reformat or add labels. Use the reviewed head commit and exact manifest path. If the PR head has changed, stop posting and report the stale review; do not attach old findings to a new commit. Record each returned comment ID. Do not submit a review.
7. Report each axis as completed, skipped (reason), or failed; report posted comment IDs and any unposted findings or posting failures. A failed reviewer or post is not a clean review.

## Shared review contract

- Ground findings in specific code evidence and LSP analysis, not the patch alone; consider cross-symbol behavior and design intent. If LSP is unavailable, report the limitation to the parent; do not claim an evidence-grounded review completed.
- Treat existing comments as already reviewed. Do not revalidate, repeat, restate, or re-report them; use them only to understand covered areas and avoid duplicates. Report only fresh, actionable issues, never unsupported speculation.
- On success, return JSON only: an array of at most five objects per axis, or `[]` when no net-new actionable issue exists. Each object represents one issue and contains only `AXIS`, `FILE_PATH`, `LINE_NUMBER`, `REVIEW_COMMENT`.
- On unavailable LSP, missing required input, or another review blocker, return `{"AXIS":"<assigned axis>","STATUS":"failed","REASON":"<specific blocker>"}` instead of an array. The parent records the failure; it must not interpret it as no issues found.
- `FILE_PATH` must exactly match the manifest. `LINE_NUMBER` is an integer identifying a commentable new-file line on the diff's right side, the last line for a multi-line range. Evidence elsewhere grounds the conclusion, never substitutes for the diff anchor.
- `REVIEW_COMMENT` is the complete, self-contained posting body, formatted by the subagent using its axis reference. Start with the issue itself. Order findings by impact, highest first, then by file and line.

## Gotchas

- Resolve Jira tickets in the parent: subagents may not inherit Atlassian MCP connections. Pass fetched descriptions, not instructions to fetch them.
- `gh api` comment bodies need JSON input, not `-f body=@file`; load the posting reference before any post.

## Completion criteria

- Quality and code smells each ran in their own subagent and have recorded outcomes; requirements ran in its own subagent only when the PR-body ticket-description gate passed, otherwise its skip reason is explicit.
- Every posted finding has a validated manifest path, right-side diff line, reviewed commit, and returned comment ID; duplicates are excluded and no review was submitted.
- Run a closing completeness sweep across eligible axes, qualifying tickets, and retained findings. Account for every skipped, failed, or unposted item before reporting completion.