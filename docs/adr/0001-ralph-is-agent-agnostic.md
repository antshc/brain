# Ralph is agent-agnostic

Ralph knows its agent roster but nothing about what the agents contain. It names `codey` and `chorey` directly at the launch site, and encodes the ordering, gate, and unavailability policy between them — but carries no assumption about an agent's internals, prompts beyond the documented handoff sections, or toolchain, and could launch any agent that honors the same invocation-directory contract and five-field report format.

- **Resolve at the edge**: ambient location (`HARNESS_REPO_PATH`, `CODEBASE_REPO_PATH`) is discovered exactly once, by the entry-point skill (`resolve-harness`/`setup-harness`/`ralph:dev`/`ralph:fix`), and passed explicitly downstream through trusted channels (`## HARNESS`, worktree-skill arguments) rather than re-derived by each component. A component handed a present-but-invalid value stops as blocked instead of guessing or searching the filesystem itself.
- **Contract, not internals**: Ralph depends only on what an agent *exposes* — it runs in its invocation directory and returns the five-field report. How it implements, verifies, or reviews is opaque. An agent Ralph cannot invoke is substituted or skipped per its documented policy, and Ralph synthesizes the missing five-field report itself so downstream steps never read an absent `STATUS`.

## Considered Options

- **Resolve agents through a role indirection layer** (`implementation agent`/`review agent` names read from configuration) — rejected: it buys substitutability that no second roster exists to use, and adds a configuration source to resolve and validate for a value that has exactly one setting.

