# Ralph launches Csdroid from the worktree

Ralph owns worktree creation and launches Csdroid with the worktree as its invocation directory on every Ralph-to-Csdroid handoff. Csdroid receives the task and `HARNESS_ROOT`, but has no `WORKTREE_PATH` contract and does not determine whether its current directory is a worktree; `to-droid` likewise launches it from its own current directory. This keeps execution-location policy with the caller that owns it.
