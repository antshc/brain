---
name: github
description: >-
  Run GitHub platform mechanics for repositories, specs, tickets, issues, pull requests, review threads, and checks. Use for 'publish a spec', 'fetch a PR', 'post a reply', or 'inspect checks'. Branches, commits and worktrees belong to `git`; review judgment belongs to `review`.
---

# GitHub

Select one operation below. Load its tactic only, then follow any reference it selects. Reselect when the next operation changes. The caller supplies authority, target, and expected state, and owns workflow order, integration, approvals, and cleanup decisions.

| Intent | Tactic |
| --- | --- |
| Read/search GitHub repository metadata or pinned evidence | [Repository](tactics/repository.md) |
| Read or change issues, labels, assignees, or relationships | [Issues](tactics/issues.md) |
| Publish a spec or ticket, read a graph, or handle issue artifacts | [Specs and tickets](tactics/specs-and-tickets.md) |
| Draft or read PR metadata, publish, get a diff, or post a conversation comment | [Pull requests](tactics/pull-requests.md) |
| Draft or finalize a review comment, inspect discussion, post, reply, or resolve | [Reviews](tactics/reviews.md) |
| Verify checks at a pinned head | [Checks](tactics/checks.md) |

`github` owns mechanics only. *Load and follow the `review` skill to review code changes, PR comments, and downstream blast radius risks*; long-running review and CI monitoring is the caller's loop.

For CLI operations, resolve `GH_TOOL` as `python3 <installed github skill directory>/scripts/github.py` before changing CWD. Use subcommand `--help` for flags and [CLI contract](references/cli-contract.md) when interpreting errors or adapting outputs. For remote operations, follow [Transports](references/transports.md). Explicit offline mode skips remote calls.
