# Posting inline comments

For each finding, post `REVIEW_COMMENT` as an inline pull-request comment. Resolve `OWNER`, `REPO`, `PR_NUMBER`, exact manifest `FILE_PATH`, right-side `LINE_NUMBER`, and the reviewed `COMMIT_ID` before posting. Confirm the current PR head still equals that commit; stop on a mismatch.

Write the body verbatim to a unique temporary file. Build JSON with `jq --rawfile` and send it through `gh api --input -`, substituting the resolved values and body file path:

```bash
COMMENT_ID=$(jq -n \
  --arg commit_id "$COMMIT_ID" \
  --arg path "FILE_PATH" \
  --argjson line LINE_NUMBER \
  --arg side "RIGHT" \
  --rawfile body /path/to/comment_body.md \
  '{commit_id:$commit_id, path:$path, line:$line, side:$side, body:$body}' \
  | gh api repos/OWNER/REPO/pulls/PR_NUMBER/comments --input - --jq '.id')
```

Return the posted `COMMENT_ID`; retain it for later updates and remove the temporary body file. On failure, report the unposted finding and API error; do not claim success or blindly retry an uncertain post. Do not submit the review.

## Gotchas

`gh api -f body="@path/to/file"` posts the literal path, not file contents. Use JSON input to preserve backticks, quotes, apostrophes, and newlines verbatim.
