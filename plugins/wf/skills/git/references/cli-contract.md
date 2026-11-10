# Git CLI contract

`GIT_TOOL` means `python3 <absolute installed git skill>/scripts/git.py`. JSON on stdout, diagnostics on stderr. Exit 0 confirms operation, 1 Git/tool failure or blocked worktree, 2 invalid input/routing, 3 verification problems.

Use explicit checkout roots, qualified repository identities, pinned SHAs and message files. Failed reads do not establish absence. Preserve uncertain state and reconcile before retrying. Worktree removal never forces, prunes, resets, or recursively deletes unverified data.
