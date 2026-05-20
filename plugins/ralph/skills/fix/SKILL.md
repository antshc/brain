---
name: fix
description: Fix review comments by applying the suggested changes.
argument-hint: '<PR URL> (e.g., "https://github.com/owner/repo/pull/1245")'
---

# Setup

Parse `{{input}}` to extract `<owner>`, `<repo>`, `<number>` from `https://github.com/{owner}/{repo}/pull/{number}`.

1. Get PR branch name: `branch=$(gh pr view <number> --repo <owner>/<repo> --json headRefName -q .headRefName)`
2. Invoke the `/worktree` skill:
   ```
   /worktree <branch> <branch>
   ```
   Parse the output to capture `WORKTREE_PATH`. Switch into `WORKTREE_PATH`.
3. Run thread fetch from inside the worktree: `python3 <skill-directory>/github/fetch_threads.py <pr_url>`

Output is a JSON array of actionable threads. Each thread has this structure:

```json
{
  "thread_id": "str",
  "prefix": "str",
  "path": "str",
  "lines": "str",
  "actionable_comment": "str",
  "comments": [{"author": "str", "body": "str"}]
}
```

## Apply fix to thread

`actionable_comment` contains the actual fix instructions. `comments` contains the history of the thread conversation.

## 1. Explore

- Read the file. Review each thread's `lines`, `actionable_comment`, and `comments` if needed for more context history.
- **If a thread is unclear** (vague, ambiguous, conflicting interpretations, missing context) — mark it for clarification, DO NOT fix it.

## 2. Implement

- Fix the thread actionable comment by making only the necessary changes to address the issue without altering unrelated code.

## 3. Verify

- Build and run tests for changed files.

## 4. Commit, push

- `git commit` with summary of changes, files, and any blockers.
- `git push` (no flags).

## 5. Reply

Reply to each thread via GraphQL:

```
gh api graphql -f query='
  mutation($threadId: ID!, $body: String!) {
    addPullRequestReviewThreadReply(input: { pullRequestReviewThreadId: $threadId, body: $body }) {
      comment { id }
    }
  }
' -f threadId=<thread_id> -f body='<reply>'
```

- **Fixed threads:** reply with `Fixed.`
- **Unclear threads:** reply with `question: <specific clarification question>` — reference the ambiguity, offer options when possible. No generic questions.

Do not resolve threads.

# Rules

- Never push to base branches (`main`, `master`); always push only to the PR branch. Never force-push, delete branches, or rebase/amend pushed commits.
- If `git push` to the PR branch is rejected, stop and report.
- If unclear, reply `question:` — don't guess. Next run auto-skips threads with `question:`.
- Don't skip actionable threads without a reason.
