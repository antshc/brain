# Csdroid uses its invocation directory

Csdroid executes code, Git, build, test, and exploration commands in the directory from which it was launched and does not change directories to interpret a worktree path. `WORKTREE_PATH` is not part of Csdroid's prompt, arguments, status output, or documentation. The agent does not need to know whether its directory is a worktree, a repository root, or another valid workspace; callers establish the execution location before invocation.
