---
name: fix
description: Fix review comments by applying the suggested changes.
argument-hint: '<PR URL> (e.g., "https://github.com/owner/repo/pull/1245")'
---

# Setup

Parse `{{input}}` to extract `<owner>`, `<repo>`, `<number>` from `https://github.com/{owner}/{repo}/pull/{number}`.

1. Resolve repository root: `repo_root=$(git rev-parse --show-toplevel)`
2. Get PR branch name: `branch=$(gh pr view <number> --repo <owner>/<repo> --json headRefName -q .headRefName)`
3. Ensure worktree parent exists at the same level as the repository root: `mkdir -p "$repo_root.worktrees"`
4. Create and switch to a dedicated worktree at `<repository_root>.worktrees/<branch>`:
   ```bash
   git fetch --all --prune
   git worktree add "$repo_root.worktrees/$branch" "$branch" 2>/dev/null \
     || git worktree add --track -b "$branch" "$repo_root.worktrees/$branch" "origin/$branch"
   cd "$repo_root.worktrees/$branch"
   ```
5. Run thread fetch from inside the worktree: `python3 <skill-directory>/github/fetch_threads.py <pr_url>`

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

`actionable_comment` contains the actual fix instructions. `comments` contains the history of the thread conversation.

# Process threads grouped by file

Group threads by `path`. For each file group (`fix!` groups first):

## 1. Explore

- Read the file. Review each thread's `lines`, `actionable_comment`, and `comments` history.
- **If a thread is unclear** (vague, ambiguous, conflicting interpretations, missing context) — mark it for clarification, do not fix it.

## 2. Implement

- Apply all clear fixes in a single editing pass. Minimal changes only.

## 3. Verify

- Build and run tests for changed files.

## 4. Commit, push, and remove worktree

- `git commit` with summary of changes, files, and any blockers.
- `git push` (no flags).
- Remove the worktree folder: `git worktree remove "$repo_root.worktrees/$branch" --force`

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
