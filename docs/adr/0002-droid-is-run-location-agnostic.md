# Droid is run-location-agnostic

Droid executes code, Git, build, test, and exploration commands in the directory from which it was launched and does not change directories to interpret a worktree path. `WORKTREE_PATH` is not part of Droid's prompt, arguments, status output, or documentation. The agent does not need to know whether its directory is a worktree, a repository root, or another valid workspace; callers establish the execution location before invocation.

Droid does not resolve repository-location declarations. Coding, verification, and Gotchas guidance are skill-owned references beside their consuming skills; each skill reports a missing reference and uses its bundled technology-agnostic fallback.
