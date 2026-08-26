# GitHub API

Every `gh` invocation this skill makes. Copy each verbatim and substitute `{{owner}}`, `{{repo}}`, `{{number}}`, `{{threadId}}`.

## PR metadata

```bash
gh pr view {{number}} --repo {{owner}}/{{repo}} --json headRefName,baseRefName,state,url
```

`headRefName` is `$headRef`, the only push target. `baseRefName` is `$baseRef`. A `state` other than `OPEN` → stop and report.

## Acting login

```bash
gh api user -q .login
```

Resolves `$actingLogin`, used to recognise this skill's own earlier replies.

## Review threads

```bash
gh api graphql \
  -f query='
query($owner: String!, $repo: String!, $number: Int!, $cursor: String) {
  repository(owner: $owner, name: $repo) {
    pullRequest(number: $number) {
      reviewThreads(first: 100, after: $cursor) {
        pageInfo { hasNextPage endCursor }
        nodes {
          id isResolved isOutdated path line startLine diffSide
          comments(first: 50) {
            nodes { id author { login } body createdAt }
          }
        }
      }
    }
  }
}' \
  -f owner={{owner}} -f repo={{repo}} -F number={{number}}
```

`hasNextPage: true` → rerun with `-f cursor={{endCursor}}` appended and concatenate the `nodes` arrays. Repeat until `hasNextPage: false`.

Line range per thread: `startLine`–`line` when `startLine` is set, the single line `line` when `startLine` is null, and whole-file when both are null. `isOutdated: true` means the range points at a superseded diff — locate the code by symbol name from the comment body instead.

## PR-level discussion

```bash
gh pr view {{number}} --repo {{owner}}/{{repo}} --json comments,reviews
```

`reviews[].body` holds summary review text and `comments[]` holds the conversation tab. Both carry `author.login`; a review with an empty `body` contributes nothing.

## Reply to a review thread

Write the reply to a file first, so bodies containing backticks, quotes, or newlines survive the shell intact:

```bash
cat > /tmp/reply.md <<'BODY'
{{replyBody}}
BODY

gh api graphql -f query='
  mutation($threadId: ID!, $body: String!) {
    addPullRequestReviewThreadReply(input: { pullRequestReviewThreadId: $threadId, body: $body }) {
      comment { id }
    }
  }
' -f threadId={{threadId}} -F body=@/tmp/reply.md
```

## Reply to a PR-level comment

```bash
gh pr comment {{number}} --repo {{owner}}/{{repo}} --body-file /tmp/reply.md
```

PR-level comments have no thread id, so the reply lands on the conversation tab. Quote the line you are answering so the reviewer can match it.
