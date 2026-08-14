# GOTCHAS

<!-- Reusable directives, loaded by droid-gotchas before implementation and distilled/written directly by the agent after each session (extends an existing line when the same rule recurs). -->

## Gotchas

<!-- One directive per line. Example shape (replace with real, agent-written gotchas): -->
<!-- - <directive> -->
- A local `copilot plugin marketplace add` registers under the name in the target `marketplace.json`'s `"name"` field, not the `add` command's argument — testing a worktree's marketplace changes against the real `brain` marketplace name collides; temporarily rename the field for the test, then revert it before finishing.
- When grepping this repo for a retired capability/agent name after a rename, exclude `docs/adr/*` (decision history and rejected-options prose intentionally retain the old name) and `CONTEXT.md`'s `_Avoid_:` glossary lines (they intentionally name the old term as guidance).
- When operating in a worktree checkout that is separate from `HARNESS_REPO_PATH`, the bash tool's default cwd is neither — always `cd` into the intended directory explicitly at the start of every command rather than assuming persistence across calls.
- When a task scopes a `python3`→`python` rename to "invocation instruction text" only (e.g. resolve-harness, fix), leave each script's own `#!/usr/bin/env python3` shebang and internal `Usage: python3 <script>` docstrings untouched — those are script internals, not the calling skill's invocation text.
- When adding a new `.githooks/pre-commit` `sync_module` mapping (module → skill `scripts/` folder), Codey never commits, so the hook never fires this session — manually run the equivalent `rsync -a --delete <src>/ <dest>/` now so the synced copy exists on disk and is included in the uncommitted diff left for `to-commit`.
- When a new synced Python module's skill-folder destination directory name differs from the module's own name under `tools/src/modules/` (e.g. `github_tracker/` → `.../scripts/`), each entry-point script must resolve sibling package imports dynamically via `_SCRIPT_DIR.name` + `importlib` (like `git_worktree/create_worktree.py`), not hardcoded package-name imports (like `github/fetch_issues.py`, which only works because its synced destination folder is also named `github`).
- When deciding whether to extend an existing shared `tools/src/modules/` module vs. creating a new one, check `.githooks/pre-commit`'s `sync_module` mappings first — if the existing module already syncs into an unrelated skill folder, adding new code there bloats that skill's footprint; prefer a new self-contained module when the concerns genuinely differ (e.g. `github`'s read-only GraphQL vs. the new `github_tracker`'s write-oriented `gh` CLI ops).
- When a task requires an "identical stdout contract" with a bash script being replaced, verify exact spacing byte-for-byte with `cat -A` (or equivalent) rather than eyeballing — e.g. `create-labels.sh`'s `echo "exists:  $name"` has two spaces vs. `echo "created: $name"`'s one.
- When a Markdown output template contains fenced code examples, wrap the template in a longer fence than its examples and verify both opening/closing counts after patching — a broad fence replacement can close the outer template at the first inner example.
- When changed files are untracked, `git diff HEAD` and `git diff --check` omit them — use `git diff --no-index /dev/null <file>` to review them without staging user work.
- Direct Codey invocations must place the implementation request under a trusted `## TASK` heading — shorthand such as `implement` cannot inherit a task from conversation or session memory and is blocked before implementation.
- Skills with `context: fork` produce editor errors when `github.copilot.chat.skillTool.enabled` is disabled — omit `context` unless the plugin explicitly requires and enables that tool.
