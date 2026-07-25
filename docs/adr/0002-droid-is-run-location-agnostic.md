# Droid is run-location-agnostic

Droid executes code, Git, build, test, and exploration commands in the directory from which it was launched and does not change directories to interpret a worktree path. `WORKTREE_PATH` is not part of Droid's prompt, arguments, status output, or documentation. The agent does not need to know whether its directory is a worktree, a repository root, or another valid workspace; callers establish the execution location before invocation.

Droid resolves its per-repo `CODE.md`, `VERIFY.md`, and `MEMORY.md` files from its current directory during INPUT. When one is not present there, Droid discovers the Harness Root by resolving Harness Settings (via `resolve-harness`/the nearest `.harness.env`) instead of assuming its current directory is the harness root.
