# WF Skills

## Ad Hoc: Use an external GitHub repository as a board remote

Some skills (e.g. `to-tickets`, `to-spec`) need to target a GitHub repo that is not the current `origin`.
The pattern below registers it temporarily as a `board` remote, extracts the `owner/repo` slug
for use in API calls, then removes the remote when done.

```bash
# 1. Add the target repository as a remote named "board"
git remote add board git@github.com:acme-org/my-project-board.git

# 2. Verify it was registered
git remote -v

# 3. Extract the owner/repo slug
git remote get-url board | sed -E 's#^git@[^:]+:##; s#^https?://[^/]+/##; s#\.git$##'
# → acme-org/my-project-board

# 4. Use "board" if it exists, otherwise fall back to "origin"
( git remote get-url board 2>/dev/null || git remote get-url origin ) \
  | sed -E 's#^git@[^:]+:##; s#^https?://[^/]+/##; s#\.git$##'

# 5. Clean up — remove the board remote
git remote remove board
```
