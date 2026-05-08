# Copilot Instructions

## Project Overview

**ralph** is a Python-based AFK (Away From Keyboard) automated PR review service. It finds open GitHub PRs authored by a user, fetches unresolved review threads, and drives the Copilot CLI agent to address them — committing fixes and replying to threads without human intervention.

---

## Architecture

### Folder Structure

The codebase follows **Vertical Slice Architecture** — each feature owns all the logic it needs. Cross-cutting concerns live in `shared/`; external system adapters live in `infrastructure/`.

```
ralph/
├── afk-review-service.sh           # Shell entry point — cds into repo-dir, invokes review_service.py
├── prompt.md                       # Copilot agent instructions injected into every run
├── unit_tests/                     # uses for the unit tests
├── integration_tests/              # uses for integration tests
├── app/
│   ├── main.py           # Orchestrator: arg parsing, delegate the call to the features
│   ├── features/
│   │   ├── usecase/
│   │   │   ├── handler.py          # Entry point: fetch + classify for a PR URL
│   │   │   ├── classifier.py       # Label detection and thread classification logic
│   │   │   └── tests/
│   │   │       └── classifier_test.py
│   ├── domain/
│   │   ├── pull_request.py         # PullRequest dataclass (owner, repo, number, url)
│   │   ├── review_thread.py        # ReviewThread dataclass + ThreadLabel enum
│   │   └── execution_record.py     # ExecutionRecord dataclass (pr_url, count, last_run, last_threads)
│   ├── infrastructure/
│   │   ├── vcs_client.py            # Thin wrapper around the `gh` CLI (GraphQL + REST)
│   │   └── ai_agent.py       # Thin wrapper around the `copilot` CLI
│   └── shared/
│       ├── log.py                  # log_json() — structured JSON logging to stderr
│       └── pr_url.py               # Parses GitHub PR URLs → (owner, repo, number)
└── logs/                           # Runtime logs written by run_agent and track_execution
```

Each feature's `handler.py` is the only public entry point for that slice. Do not call `classifier.py` or `prompt_builder.py` directly from outside their slice.

### Domain Entities

Domain types are plain Python `class`es (or `Enum`s). They must not import from `features`, `infrastructure`, or `shared`.

---

## Conventions

### GitHub Integration

All GitHub access goes through the `gh` CLI — never call the GitHub REST/GraphQL APIs directly over HTTP.
- String variables use `-f`, numeric variables use `-F`.
- `subprocess.run(..., check=True)` — let exceptions propagate; do not swallow `CalledProcessError`.

### Execution Log

`ExecutionLog` prevents infinite retry loops. It writes a daily JSON file per repo under `logs/<repo-slug>/execution-log-<date>.json`.

- Call `exec_log.get_count(pr_url)` before processing.
- Call `exec_log.update(pr_url, thread_ids)` after dispatching to the agent.
- Skip the PR (log a warning) if `count >= max_executions`.

### Logging

Use `log_json` from `log.py` for all runtime events — never `print()` to stdout in library code.

```python
log_json("info", "Processing PR", pr_url=pr_url)
log_json("warning", "Execution limit reached", pr_url=pr_url, count=str(exec_count))
```

All values must be strings. Output goes to stderr as newline-delimited JSON.

---

## Python CLI

Use `python3` — `python` is not available in this environment.

## Test writing Guidelines

- Tests live in `unit_tests/`m `integration_tests` and mirror the module they test.
- Every test must be traceable to a scenario in `TEST_PLAN.md`:
  - Test class docstring → Feature name (e.g., `"Feature: Comment Label Detection"`).
  - Test method name → Scenario name in snake_case and the comment under the Test method name with the scenario name `Scenario: a ReviewThread from a raw dict.`.
  - When a test or scenario changes, update both sides to keep the mapping in sync.

## Running Tests

Tests use `pytest` via the `python3 -m pytest` invocation. Run all tests from the repo root:

```bash
python3 -m pytest app/
```

Run a specific test file:

```bash
python3 -m pytest app/features/review/tests/classifier_test.py -v
```

Test files add `app/` to `sys.path` manually, so no `PYTHONPATH` export is needed.


## General Guidelines

- Each module has a single, clearly named responsibility — do not merge concerns.
- All GitHub I/O goes through `gh_client.py`; all Copilot I/O through `copilot_client.py`.
- Prefer `subprocess.run(..., check=True)` and let errors bubble — no silent failures.
- Use `pathlib.Path` for all file system operations.

