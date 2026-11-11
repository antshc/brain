# Post an inline review comment

## Code

Use the final agent-owned body returned by Git Conventions, including its terminal metadata. Set `COMMIT_ID` to `REVIEW_HEAD` and confirm the current PR head and base still match `REVIEW_HEAD` and `REVIEW_BASE`. Stop and report a stale review on a mismatch.

## HITL

Require explicit human approval of the exact human-owned body. Preserve the approved text verbatim and keep it unmarked. Confirm the current PR head still equals the reviewed `COMMIT_ID` before posting. Stop and report a stale review on a mismatch.

## Post and verify

Resolve `OWNER`, `REPO`, `PR_NUMBER`, the exact manifest `FILE_PATH`, and a commentable right-side `LINE_NUMBER`. Retain unanchored findings as unposted with the reason. Run the selected route's freshness check immediately before the API call.

*Run `github` skill to post pull request review threads* using Reviews, **Inline**, with the qualified PR, `COMMIT_ID`, exact path, line, and body file. Code also supplies `REVIEW_BASE`. Retain the confirmed comment ID. On mismatch or uncertain response, report the finding and reconcile before retrying. Leave review submission to the caller.
