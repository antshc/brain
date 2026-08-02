# Ralph is agent-agnostic

Ralph does not hardcode Droid-specific behavior; it could launch any agent that honors the same invocation-directory contract established when handing off a task. Ralph's own logic — worktree creation, task handoff — carries no agent-specific naming, prompts, or assumptions about the launched agent's internals.

- **Resolve at the edge**: ambient location (`HARNESS_REPO_PATH`, `CODEBASE_REPO_PATH`) is discovered exactly once, by the entry-point skill (`resolve-harness`/`setup-harness`/`ralph:dev`/`ralph:fix`), and passed explicitly downstream through trusted channels (`## HARNESS`, worktree-skill arguments) rather than re-derived by each component. A component handed a present-but-invalid value stops as blocked instead of guessing or searching the filesystem itself.
