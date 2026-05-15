# Copilot Instructions

## Project Overview

---

## Architecture

### Folder Structure

Vertical Slice Architecture — each feature owns all the logic it needs. Cross-cutting concerns live in `shared/`; external adapters in `infrastructure/`.

```
brain/
├── .githooks/pre-commit            # Syncs modules into plugins/skills before each commit
├── pyproject.toml
├── plugins/                        # Copilot agent plugins
├── skills/                         # Copilot agent skills
├── tools/
│   ├── src/
│   │   ├── modules/                # Shared Python modules — source of truth
│   │   │   └── github/             # GitHub domain + infrastructure (domain/, features/, infrastructure/, shared/)
│   │   └── ralph/                  # ralph CLI tool
│   │       ├── main.py             # Orchestrator: arg parsing, delegates to features
│   │       └── features/           # review_pull_request/, review_pull_requests/
│   └── tests/
│       ├── unit/                   # Unit tests mirroring src/ structure
│       └── integration/            # Integration tests
└── logs/                           # Runtime logs (daily JSON per repo)
```


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
