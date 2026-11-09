# CLI contract

`GH_TOOL` means `python3 <absolute installed github skill>/scripts/github.py`. Commands print JSON to stdout, with diagnostics on stderr. Exit 0 confirms the operation, 1 is a tool or remote failure, 2 is invalid input or unresolved routing, 3 reports verification problems. The worktree and review discussion gates preserve their existing JSON status/action and exit 1 on a block.

Use qualified targets, explicit checkout roots, pinned SHAs, and body files. A failed or incomplete read does not establish absence. Retain verified IDs, paths and partial state. Reconcile an uncertain write before retrying. Do not report verified success from an unverified response.
