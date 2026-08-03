# GOTCHAS

<!-- Reusable directives, loaded by droid-gotchas before implementation and distilled/written directly by the agent after each session (extends an existing line when the same rule recurs). -->

## Gotchas

<!-- One directive per line. Example shape (replace with real, agent-written gotchas): -->
<!-- - <directive> -->
- A local `copilot plugin marketplace add` registers under the name in the target `marketplace.json`'s `"name"` field, not the `add` command's argument — testing a worktree's marketplace changes against the real `brain` marketplace name collides; temporarily rename the field for the test, then revert it before finishing.
- When grepping this repo for a retired capability/agent name after a rename, exclude `docs/adr/*` (decision history and rejected-options prose intentionally retain the old name) and `CONTEXT.md`'s `_Avoid_:` glossary lines (they intentionally name the old term as guidance).
- When operating in a worktree checkout that is separate from `HARNESS_REPO_PATH`, the bash tool's default cwd is neither — always `cd` into the intended directory explicitly at the start of every command rather than assuming persistence across calls.
