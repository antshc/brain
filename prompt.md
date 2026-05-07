# Setup

Input is a JSON array of actionable threads sorted by priority (`fix!` before `suggest!`). Each thread has: `thread_id`, `prefix`, `path`, `lines`, `body`, `discussion`.

# Process threads grouped by file

Group threads by `path`. For each file group (`fix!` groups first):

## 1. Explore

- Read the file. Review each thread's `lines` and `discussion`.
- **If a thread is unclear** (vague, ambiguous, conflicting interpretations, missing context) — mark it for clarification, do not fix it.

## 2. Implement

- Apply all clear fixes in a single editing pass. Minimal changes only.

## 3. Verify

- Build and run tests for changed files.

## 4. Commit & push

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
- **Unclear threads:** reply with `question!: <specific clarification question>` — reference the ambiguity, offer options when possible. No generic questions.

Do not resolve threads. Repeat for next file group.

# Rules

- Never push to base branches (`main`, `master`). Never force-push, delete branches, or rebase/amend pushed commits.
- If `git push` is rejected, stop and report.
- If unclear, reply `question!:` — don't guess. Next run auto-skips threads with `question!:`.
- Don't skip actionable threads without a reason.
