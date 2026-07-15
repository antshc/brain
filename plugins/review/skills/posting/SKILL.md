---
name: 'posting'
description: 'Post a review finding as an inline pull-request review comment via the gh API; invoked by PR-review skills.'
---

# Posting Review Comments via gh API

Post each finding as an **inline pull-request review comment** using the gh API. Substitute `OWNER`, `REPO`, `PR_NUMBER`, `FILE_PATH`, `LINE_NUMBER`, and `FINDING_BODY` for the finding being posted.

## Post the comment

```bash
COMMIT_ID=$(gh pr view PR_NUMBER --repo OWNER/REPO --json headRefOid -q .headRefOid)
gh api repos/OWNER/REPO/pulls/PR_NUMBER/comments \
  --method POST \
  -f commit_id="$COMMIT_ID" \
  -f path="FILE_PATH" \
  -F line=LINE_NUMBER \
  -f side="RIGHT" \
  -f body="FINDING_BODY"
```

DO NOT submit the review.
