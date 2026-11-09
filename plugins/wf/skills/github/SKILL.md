---
name: github
description: >-
  Manage Git branches, commits, worktrees, and GitHub repositories, specs, tickets, issues, pull requests, reviews, and checks. Use to name a branch, publish a spec, fetch a PR, reply to a review, or inspect checks.
---

# GitHub

Select one operation below. Load its tactic only, then follow any reference it selects. Reselect when the next operation changes. The caller supplies authority, target, and expected state, and owns workflow order, integration, approvals, and cleanup decisions.

| Intent | Tactic |
| --- | --- |
| Resolve a repository or read/search remote evidence | [Repository](tactics/repository.md) |
| Name, inspect, create, fetch, push, or delete a branch | [Branches](tactics/branches.md) |
| Draft a commit, read history, or commit authorized files | [Commits](tactics/commits.md) |
| Inspect, create, reuse, remove, or reconcile a worktree | [Worktrees](tactics/worktrees.md) |
| Read or change issues, labels, assignees, or relationships | [Issues](tactics/issues.md) |
| Publish a spec or ticket, read a graph, or handle issue artifacts | [Specs and tickets](tactics/specs-and-tickets.md) |
| Draft or read PR metadata, publish, get a diff, or post a conversation comment | [Pull requests](tactics/pull-requests.md) |
| Draft or finalize a review comment, inspect discussion, post, reply, or resolve | [Reviews](tactics/reviews.md) |
| Verify checks at a pinned head | [Checks](tactics/checks.md) |

For CLI operations, resolve `GH_TOOL` as `python3 <installed github skill directory>/scripts/github.py` before changing CWD. Use subcommand `--help` for flags and [CLI contract](references/cli-contract.md) when interpreting errors or adapting outputs. For remote operations, follow [Transports](references/transports.md). Explicit offline mode skips remote calls.
