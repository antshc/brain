# Posting inline comments

Post the complete final body returned by the parent's shared conversation step; preserve its visible text and metadata verbatim. Resolve `OWNER`, `REPO`, `PR_NUMBER`, exact manifest `FILE_PATH`, right-side `LINE_NUMBER`, and the reviewed `COMMIT_ID` before posting. Confirm the current PR head still equals that commit and base still equals REVIEW_BASE; stop on a mismatch. Do not post findings with a null/non-commentable line; retain them as unposted with reason.

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

Confirm returned `body` matches the complete file, including the terminal block; retain returned `id` as `COMMENT_ID` for later updates, then remove the temporary file. On mismatch or API error, report the unposted finding and failure; claim no success or duplicate an uncertain post. Do not submit the review.

## Gotchas

`gh api -f body="@path/to/file"` posts the literal path, not file contents. Use JSON input to preserve backticks, quotes, apostrophes, and newlines verbatim.