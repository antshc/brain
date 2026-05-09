# Posting Review Comments via gh API

## Post the comment

```bash
COMMIT_ID=$(gh pr view PR_NUMBER --repo OWNER/REPO --json headRefOid -q .headRefOid)
gh api repos/OWNER/REPO/pulls/PR_NUMBER/comments \
  --method POST \
  -f commit_id="$COMMIT_ID" \
  -f path="FILE_PATH" \
  -F line=LINE_NUMBER \
  -f side="RIGHT" \
  -f body="COMMENT_BODY"
```

DO NOT submit the review.
