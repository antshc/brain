# WF Skills

## ~~Ad Hoc: Use an external GitHub repository as a board remote~~ (Outdated)

> **Outdated.** Superseded by the root-level board repository harness pattern below.
> Kept for reference only.

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

## Ad Hoc: Use the root-level board repository as a harness around the project source

When AI artifacts (plans, PRDs, tickets, specs, notes) must never leak into the source
project's history, wrap the project in a **root-level board repository**. The parent/root
repo is the *harness environment*: it tracks all AI-generated artifacts, while the actual
project source lives in a nested workspace folder that the harness **ignores**. Nothing the
agent produces at the harness level can reach the source project's commits.

```
my-project-board/            # root-level "board" repo (the harness) — git-tracked
├── .git/                    # harness history: holds AI artifacts only
├── .gitignore               # ignores the nested workspace/ source folder
├── plans/                   # AI artifacts (plans, PRDs, tickets, specs)
├── specs/
└── workspace/               # nested project source — ignored by the harness
    └── my-project/          # has its own .git; never sees AI artifacts
        └── .git/
```

```bash
# 1. From the root-level board repo, ignore the nested source workspace
echo "workspace/" >> .gitignore

# 2. Confirm the harness does NOT see the project source as changes
git -C my-project-board status --short
# → workspace/ must not appear (it is ignored)

# 3. Run board skills at the harness level; artifacts stay in the board repo
#    while the project source in workspace/ remains untouched.

# 4. Extract the board owner/repo slug from the harness "origin"
git -C my-project-board remote get-url origin \
  | sed -E 's#^git@[^:]+:##; s#^https?://[^/]+/##; s#\.git$##'
# → acme-org/my-project-board

# 5. Work on the source inside the nested workspace using its own git
git -C my-project-board/workspace/my-project status
```

Key points:

- The **root/parent repo is the harness** — it isolates AI artifacts from the project source.
- The **nested `workspace/` folder is git-ignored** by the harness, so source code and AI
  artifacts never cross-contaminate.
- The nested project keeps its **own `.git`**; commits there stay free of AI artifacts.
- Use the harness `origin` slug (see the section above) as the `board` target for skills
  like `to-tickets` and `to-spec`.
