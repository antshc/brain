---
name: post-review-comment
description: Post one or more findings as inline pull-request review comments via the gh API, without submitting the review. Use when a review skill has findings ready to post to a GitHub PR.
argument-hint: '<PR context + findings JSON> (owner/repo/number and an array of {file_path, line_number, body})'
---

**Goal:** post each finding as an inline pull-request review comment on the `RIGHT` side of the diff, without submitting the review.

**Step 1 — Get the input**
Expect the input as JSON:

```json
{
  "pr": { "owner": "OWNER", "repo": "REPO", "number": 1245 },
  "comments": [
    { "file_path": "src/Foo.cs", "line_number": 42, "body": "COMMENT_BODY" }
  ]
}
```

If `{{input}}` already contains this JSON (or an equivalent `owner`, `repo`, `number`, and a list of findings), use it.
Otherwise ask: *"Provide the PR (owner/repo/number) and the findings to post (file path, line, body)."* and wait for the response.

**Step 2 — Resolve the head commit once**

```bash
COMMIT_ID=$(gh pr view PR_NUMBER --repo OWNER/REPO --json headRefOid -q .headRefOid)
```

**Step 3 — Post each comment**
For every entry in `comments`, post one inline comment on the `RIGHT` side:

```bash
gh api repos/OWNER/REPO/pulls/PR_NUMBER/comments \
  --method POST \
  -f commit_id="$COMMIT_ID" \
  -f path="FILE_PATH" \
  -F line=LINE_NUMBER \
  -f side="RIGHT" \
  -f body="COMMENT_BODY"
```

**Rules**
- Post one comment per finding; never merge unrelated findings into one comment.
- DO NOT submit the review — post inline comments only.
- Report a short summary of how many comments were posted and any that failed.
