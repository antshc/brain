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
│   ├── review_service.py           # Orchestrator: arg parsing, PR loop, skip logic
│   ├── features/
│   │   ├── list_prs/
│   │   │   ├── handler.py          # Lists open PRs authored by a user
│   │   │   └── tests/
│   │   │       └── handler_test.py
│   │   ├── fetch_threads/
│   │   │   ├── handler.py          # Entry point: fetch + classify for a PR URL
│   │   │   ├── classifier.py       # Label detection and thread classification logic
│   │   │   └── tests/
│   │   │       └── classifier_test.py
│   │   ├── run_agent/
│   │   │   ├── handler.py          # Dispatches threads to the Copilot agent
│   │   │   ├── prompt_builder.py   # Assembles the prompt from threads + template
│   │   │   └── tests/
│   │   │       └── handler_test.py
│   │   └── track_execution/
│   │       ├── handler.py          # ExecutionLog: reads/writes per-PR attempt counts
│   │       └── tests/
│   │           └── handler_test.py
│   ├── domain/
│   │   ├── pull_request.py         # PullRequest dataclass (owner, repo, number, url)
│   │   ├── review_thread.py        # ReviewThread dataclass + ThreadLabel enum
│   │   └── execution_record.py     # ExecutionRecord dataclass (pr_url, count, last_run, last_threads)
│   ├── infrastructure/
│   │   ├── gh_client.py            # Thin wrapper around the `gh` CLI (GraphQL + REST)
│   │   └── copilot_client.py       # Thin wrapper around the `copilot` CLI
│   └── shared/
│       ├── log.py                  # log_json() — structured JSON logging to stderr
│       └── pr_url.py               # Parses GitHub PR URLs → (owner, repo, number)
└── logs/                           # Runtime logs written by run_agent and track_execution
```

### Slice Responsibilities

| Slice | Responsibility |
|---|---|
| `features/list_prs` | Lists open PR URLs for a given user and repo |
| `features/fetch_threads` | Fetches threads via `gh_client`, classifies by label |
| `features/run_agent` | Builds the prompt and launches the `copilot` CLI |
| `features/track_execution` | Reads/writes daily execution logs to cap retries |
| `infrastructure/gh_client.py` | All `gh` CLI calls — GraphQL queries, `pr list`, `pr checkout` |
| `infrastructure/copilot_client.py` | Launches `copilot` CLI, streams JSON output |
| `shared/log.py` | `log_json(level, message, **extra)` — structured stderr logging |
| `shared/pr_url.py` | Single-purpose URL parser — returns `(owner, repo, number)` |

Each feature's `handler.py` is the only public entry point for that slice. Do not call `classifier.py` or `prompt_builder.py` directly from outside their slice.

### Domain Entities

Domain types are plain Python `dataclass`es (or `Enum`s). They must not import from `features`, `infrastructure`, or `shared`.

| Entity | File | Fields |
|---|---|---|
| `PullRequest` | `domain/pull_request.py` | `owner: str`, `repo: str`, `number: int`, `url: str` |
| `ThreadLabel` | `domain/review_thread.py` | Enum: `FIX`, `SUGGEST_BANG`, `SUGGEST`, `NIT`, `GOOD`, `QUESTION` |
| `ReviewThread` | `domain/review_thread.py` | `thread_id: str`, `label: ThreadLabel`, `path: str`, `lines: str`, `body: str`, `discussion: list[dict]` |
| `ExecutionRecord` | `domain/execution_record.py` | `pr_url: str`, `count: int`, `last_run: str`, `last_threads: list[str]` |

- `ThreadLabel.is_actionable()` returns `True` for `FIX` and `SUGGEST_BANG`.
- `PullRequest` is constructed from a URL via `pr_url.parse_pr_url()`.
- `ExecutionRecord` is the domain model backing the `track_execution` feature. `ExecutionLog` serialises it to JSON under `logs/<repo-slug>/execution-log-<date>.json`. The `count` field is what the orchestrator checks against `max_executions` to prevent infinite retry loops.
- Features receive and return domain types — not raw dicts from the GitHub API.

---

## Conventions

### GitHub Integration

All GitHub access goes through the `gh` CLI — never call the GitHub REST/GraphQL APIs directly over HTTP.

```python
# gh_client.py — GraphQL helper
def graphql(query: str, variables: dict | None = None) -> dict:
    cmd = ["gh", "api", "graphql", "-f", f"query={query}"]
    for key, value in (variables or {}).items():
        flag = "-F" if isinstance(value, (int, float)) else "-f"
        cmd.extend([flag, f"{key}={value}"])
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return json.loads(result.stdout)
```

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

`copilot_client.py` assembles the prompt and runs the `copilot` CLI:

```python
def build_prompt(threads_json: str) -> str:
    template = PROMPT_PATH.read_text()
    return f"# Review Threads\n\n{threads_json}\n\n{template}"
```

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
