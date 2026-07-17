---
name: 'posting'
description: 'Post a review comment as an inline pull-request review comment via the gh API; invoked by PR-review skills.'
---

# Posting Review Comments via gh API

Post each review comment as an **inline pull-request review comment** using the gh API. Substitute `OWNER`, `REPO`, `PR_NUMBER`, `FILE_PATH`, `LINE_NUMBER`, and `REVIEW_COMMENT` for the review comment being posted.

## Post the comment

```bash
COMMIT_ID=$(gh pr view PR_NUMBER --repo OWNER/REPO --json headRefOid -q .headRefOid)
COMMENT_ID=$(gh api repos/OWNER/REPO/pulls/PR_NUMBER/comments \
  --method POST \
  -f commit_id="$COMMIT_ID" \
  -f path="FILE_PATH" \
  -F line=LINE_NUMBER \
  -f side="RIGHT" \
  -f body="REVIEW_COMMENT" \
  --jq '.id')
```

DO NOT submit the review.

Return `COMMENT_ID` to the caller — it identifies the posted comment for any later update.
