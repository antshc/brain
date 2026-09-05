---
name: 'posting'
description: 'Post a review comment as an inline pull-request review comment via the gh API; invoked by PR-review skills.'
---

# Posting Review Comments via gh API

Post each review comment as an **inline pull-request review comment** using the gh API. Substitute `OWNER`, `REPO`, `PR_NUMBER`, `FILE_PATH`, `LINE_NUMBER`, and `REVIEW_COMMENT` for the review comment being posted.

## Post the comment

`REVIEW_COMMENT` bodies routinely contain backticks, double quotes, and apostrophes, which break naive shell quoting. Never write the body to a temp file and reference it as `-f body="@path/to/file"` — the `gh api` `-f`/`-F` flags do **not** expand a leading `@` to file contents; it gets posted as the literal string `@path/to/file...`. Instead build the JSON payload with `jq --rawfile` (which reads the whole file into a string) and pipe it into `gh api --input -`:

```bash
COMMIT_ID=$(gh pr view PR_NUMBER --repo OWNER/REPO --json headRefOid -q .headRefOid)

# Write REVIEW_COMMENT verbatim to a temp file first, e.g.:
# printf '%s' "$REVIEW_COMMENT" > /tmp/comment_body.md

COMMENT_ID=$(jq -n \
  --arg commit_id "$COMMIT_ID" \
  --arg path "FILE_PATH" \
  --argjson line LINE_NUMBER \
  --arg side "RIGHT" \
  --rawfile body /tmp/comment_body.md \
  '{commit_id:$commit_id, path:$path, line:$line, side:$side, body:$body}' \
  | gh api repos/OWNER/REPO/pulls/PR_NUMBER/comments --input - --jq '.id')
```

DO NOT submit the review.

Return `COMMENT_ID` to the caller — it identifies the posted comment for any later update.
