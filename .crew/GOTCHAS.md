# GOTCHAS

<!-- Reusable directives, loaded by droid-gotchas before implementation and distilled/written directly by the agent after each session (extends an existing line when the same rule recurs). -->

## Gotchas

<!-- One directive per line. Example shape (replace with real, agent-written gotchas): -->
<!-- - <directive> -->
- A local `copilot plugin marketplace add` registers under the name in the target `marketplace.json`'s `"name"` field, not the `add` command's argument — testing a worktree's marketplace changes against the real `brain` marketplace name collides; temporarily rename the field for the test, then revert it before finishing.
- When grepping this repo for a retired capability/agent name after a rename, exclude `docs/adr/*` (decision history and rejected-options prose intentionally retain the old name) and `CONTEXT.md`'s `_Avoid_:` glossary lines (they intentionally name the old term as guidance).
- When operating in a worktree checkout that is separate from `HARNESS_REPO_PATH`, the bash tool's default cwd is neither — always `cd` into the intended directory explicitly at the start of every command rather than assuming persistence across calls.
- Before changing a skill's Python interpreter invocation token (`python3` vs `python`), check `.github/copilot-instructions.md`'s "Python CLI" section — it pins one token for environment reasons and a skill-level change can silently contradict it.
- When a shared `tools/src/modules/<name>/` module's pre-commit rsync destination folder is named differently from `<name>` (e.g. flattened into a skill's `scripts/` folder to satisfy the `scripts/<name>.py` invocation convention), an entry script cannot hardcode `from <name>.features... import ...` the way `github`'s `fetch_threads.py` does — resolve the package name dynamically from the script's own containing directory (`Path(__file__).resolve().parent.name`) via `importlib.import_module`, since dev and synced locations differ in folder name.
- `git worktree add` failing because the branch/path already exists is not reliably identified by exit code alone (observed both 255 and 128 depending on which check fails first) — detect it by checking `"already exists" in stderr.lower()` instead.
- When converting a bash skill script to Python and the task requires "the same output shape as today", check the *original* bash's exact output format (e.g. `KEY: value` colon-separated) rather than assuming a newer sibling script's convention (e.g. `resolve_harness.py`'s `KEY=value`) applies — the two can differ per-skill.
- `.githooks/pre-commit`'s `sync_module` rsync only fires at commit time, so an uncommitted `tools/src/modules/<name>/` edit leaves the synced skill-folder copy (e.g. `plugins/ralph/skills/create-worktree/scripts/`) stale — before manually verifying a fix via the synced entrypoint, run the same `rsync -a --delete <src> <dest>` by hand first.
- When manually testing a real `git merge` conflict for `actualize_branch`-style code (as opposed to a non-conflict pull failure), a plain divergent-branches `git pull` fails before ever reaching `git merge` if `pull.rebase`/`pull.ff` isn't configured — set `git config pull.rebase false` in the test repo first so pull actually attempts (and fails with) a real merge conflict.
