# Ralph is agent-agnostic

Ralph does not hardcode Droid-specific behavior; it could launch any agent that honors the same invocation-directory contract established when handing off a task. Ralph's own logic — worktree creation, task handoff — carries no agent-specific naming, prompts, or assumptions about the launched agent's internals.
