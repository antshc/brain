---
name: gh-issue
description: Create a GitHub issue with title, body, labels, and optional repo targeting. Handles repo resolution and falls back gracefully when issues are disabled. Use when any skill needs to file a GitHub issue.
argument-hint: '<command> eg create'
---

### Create gh issue

```bash
gh issue create \
  --title "<title>" \
  --body "<body>" \
  [--repo "<owner>/<repo>"] \
  [--label "<label>"]
```

if the error message contains "Issues are disabled for this repo", resolve user private repo using following command and retry with the `--repo <owner>/<repo>`

```
<owner>: $(gh api user --jq .login)
<repo>: $(basename "$(git rev-parse --show-toplevel)")
```