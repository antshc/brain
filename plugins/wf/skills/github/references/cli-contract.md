# CLI contract

`GH_TOOL` means `python3 <absolute installed github skill>/scripts/github.py`. JSON on stdout, diagnostics on stderr. Exit 0 confirms operation, 1 tool/remote failure, 2 invalid input/routing, 3 verification problems. Review discussion preserves its JSON status/action and exits 1 on a block. Use `GIT_TOOL` for branches, commits and worktrees.

Use qualified targets, explicit checkout roots, pinned SHAs, and body files. A failed or incomplete read does not establish absence. Retain verified IDs, paths and partial state. Reconcile an uncertain write before retrying. Do not report verified success from an unverified response.
