# Post an inline review comment

## Code

Use the final agent-owned body returned by Git Conventions, including its terminal metadata. Set `COMMIT_ID` to `REVIEW_HEAD` and confirm the current PR head and base still match `REVIEW_HEAD` and `REVIEW_BASE`. Stop and report a stale review on a mismatch.

## HITL

Require explicit human approval of the exact human-owned body. Preserve the approved text verbatim and keep it unmarked. Confirm the current PR head still equals the reviewed `COMMIT_ID` before posting. Stop and report a stale review on a mismatch.

## Post and verify

Resolve `OWNER`, `REPO`, `PR_NUMBER`, the exact manifest `FILE_PATH`, and a commentable right-side `LINE_NUMBER`. Retain unanchored findings as unposted with the reason. Run the selected route's freshness check immediately before the API call.

Write the complete body to a unique temporary file. Build JSON with `jq --rawfile` and send it through `gh api --input -`, substituting the resolved values and body file path:

```bash
POSTED_COMMENT=$(jq -n \
  --arg commit_id "$COMMIT_ID" \
  --arg path "FILE_PATH" \
  --argjson line LINE_NUMBER \
  --arg side "RIGHT" \
  --rawfile body /path/to/comment_body.md \
  '{commit_id:$commit_id, path:$path, line:$line, side:$side, body:$body}' \
  | gh api repos/OWNER/REPO/pulls/PR_NUMBER/comments --input - --jq '{id,body}')
```

Require a returned `id` and verify that `body` matches the complete file byte for byte. Retain `id` as `COMMENT_ID` for later updates and remove the temporary file. On mismatch or API error, report the finding and the posting failure. Treat an uncertain response as unconfirmed and avoid duplicate posts. Do not submit the review.

## Gotchas

`gh api -f body="@path/to/file"` posts the literal path, not file contents. Use JSON input to preserve backticks, quotes, apostrophes, and newlines verbatim.
