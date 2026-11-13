---
name: git
description: >-
  Run verified Git mechanics for branch naming, creation, fetch, push, commit messages, history, and worktree lifecycle. Use for 'name a branch', 'creating the worktree', 'draft a commit', 'push a branch', or 'read commit history'. GitHub issues, PRs, and checks belong to `github`.
---

# Git

Select one tactic, loading references only when needed. Reselect for a different operation. The caller owns workflow sequence, authority, integration, approvals, and cleanup decisions. Git owns deterministic local and remote Git mechanics.

| Intent | Tactic |
| --- | --- |
| Identify a checkout and verify its remote | [Repository](tactics/repository.md) |
| Name, inspect, create, fetch, push, or delete a branch | [Branches](tactics/branches.md) |
| Merge a verified local result into a caller-owned branch | [Integration](tactics/integration.md) |
| Draft a message, inspect history, or create an authorized commit | [Commits](tactics/commits.md) |
| Inspect, create, reuse, remove, or reconcile a worktree | [Worktrees](tactics/worktrees.md) |

For CLI operations, resolve `GIT_TOOL` as `python3 <installed git skill directory>/scripts/git.py` before changing CWD. Use subcommand `--help` and [CLI contract](references/cli-contract.md) for errors and results. Use explicit checkouts and pinned SHAs. GitHub API operations belong to `github`.
