# Excluded Folders

**Never scan, read, or edit `_backup/`, `docs/kbs`, `_in-progress/`.** Treat them as out of scope for all tasks.

# Writing or updating the skill, templates, agents standards

See [CODE.md](../.droid/CODE.md) for writing style and syntax conventions.

See **Skills best practices** fetch `https://agentskills.io/skill-creation/best-practices` for How to write skills that are well-scoped and calibrated to the task.


### Plugin Marketplace

All plugins are registered in `.github/plugin/marketplace.json`. **When adding, renaming, or deleting a plugin under `plugins/`, always update `marketplace.json` to match.**

## Python CLI

Use `python3` — `python` is not available in this environment.

## Python coding

### Module Sync (pre-commit hook)

`modules/` contains shared Python code used by skills. The pre-commit hook (`./githooks/pre-commit`) syncs each module into the plugin/skill that consumes it using `rsync`. Paths in the hook are relative to the repo root. Example: `tools/src/modules/github/` → `plugins/ralph/skills/fix/github/`.

- **Edit source in `tools/src/modules/<module>/`** — NEVER EDIT the copy inside `plugins/`.
- Import paths inside a skill use relative imports matching the synced destination folder name.
- Add new module→destination mappings to `.githooks/pre-commit`.

### General Python Guidelines

- Each module has a single, clearly named responsibility — do not merge concerns.
- All GitHub I/O goes through `infrastructure/` adapters; never call GitHub APIs directly over HTTP.
- Prefer `subprocess.run(..., check=True)` — let errors bubble, no silent failures.
- Use `pathlib.Path` for all file system operations.
- Edit shared code in `tools/src/modules/` only; the pre-commit hook propagates changes to plugins.

### Tests

- Tests live in `tools/tests/unit/` and `tools/tests/integration/`, mirroring `tools/src/`.
- Every test is traceable to a scenario in `TEST_PLAN.md`:
  - Test class docstring → Feature name (e.g., `"Feature: Comment Label Detection"`).
  - Test method name → Scenario name in snake_case; add `# Scenario: ...` comment below the def.
  - Keep both sides in sync when changing a test or scenario.
- Run all tests: `python3 -m pytest tools/` from repo root.
- Run a specific file: `python3 -m pytest tools/tests/unit/domain/thread_label_test.py -v`.

## Domain modeling (wf plugin)

Single repo — docs and codebase live together, no `workspace/` split.

### Authoritative sources

- **Domain glossary:** `CONTEXT.md` — domain terminology and concepts.
- **Architecture:** `ARCHITECTURE.md` — ADR/Concept indexes, high-level source structure.


### Ticket tracker

Tickets live as GitHub issues in this repo (`gh issue` commands). Labels `hitl` and `spec` are set up per `/manage-backlog`.
