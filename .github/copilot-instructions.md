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

Domain types are plain Python `dataclass`es (or `Enum`s). They must not import from `features`, `infrastructure`, or `shared`.

---

## Conventions

### GitHub Integration

All GitHub access goes through the `gh` CLI — never call the GitHub REST/GraphQL APIs directly over HTTP.
- String variables use `-f`, numeric variables use `-F`.
- `subprocess.run(..., check=True)` — let exceptions propagate; do not swallow `CalledProcessError`.

### Thread Classification

Threads are classified by label prefix in `fetch_threads.py`:

| Label | Actionable |
|---|---|
| `fix!:` | Yes — must be addressed |
| `suggest!:` | Yes — should be addressed |
| `suggest:` | No |
| `nit:` | No |
| `good:` | No |
| `question!:` | Excluded — do not retry |

- Classification scans comments in **reverse order** — the last meaningful signal wins.
- Threads containing `fixed.` or `question!:` keywords are excluded from the actionable set.
- Only threads with `fix!` or `suggest!` labels are passed to the Copilot agent.

### Execution Log

`ExecutionLog` prevents infinite retry loops. It writes a daily JSON file per repo under `logs/<repo-slug>/execution-log-<date>.json`.

- Call `exec_log.get_count(pr_url)` before processing.
- Call `exec_log.update(pr_url, thread_ids)` after dispatching to the agent.
- Skip the PR (log a warning) if `count >= max_executions`.

### Copilot Agent

- The agent instructions live in `prompt.md` — edit that file to change agent behavior.
- Denied tools: `shell(git reset)`, `shell(git rebase)`, `shell(git clean)`.
- Default model: `claude-sonnet-4.6`.

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

```bash
python3 app/main.py ...
```

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

## Running the Service

```bash
./afk-review-service.sh <repo-dir> <github-user> <owner/repo> [max-executions]
```

- `repo-dir` — path to the local clone of the target repository.
- `github-user` — GitHub username; only PRs authored by this user are processed.
- `owner/repo` — repository in `owner/repo` format.
- `max-executions` — optional cap on processing attempts per PR (default: 5).

Set `AFK_DEBUG=1` to enable `DEBUG`-level logging.

---

## General Guidelines

- Each module has a single, clearly named responsibility — do not merge concerns.
- All GitHub I/O goes through `gh_client.py`; all Copilot I/O through `copilot_client.py`.
- Prefer `subprocess.run(..., check=True)` and let errors bubble — no silent failures.
- Use `pathlib.Path` for all file system operations.
- Tests live in `app/tests/` and mirror the module they test.
