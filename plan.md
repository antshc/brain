# Plan: Restructure brain_tools → tools/ layout

## Summary

Move from a flat `brain_tools/` package at the project root to a `tools/` package also at the project root (no `src/` wrapper). Internal modules reorganize into `ralph/`, `scripts/`, and `shared/`. `tests/` stays at the root unchanged.

---

## New Structure

```
tools/
├── __init__.py
├── scripts/
│   ├── __init__.py
│   └── fetch_threads.py        ← brain_tools/fetch_threads.py
├── ralph/
│   ├── __init__.py
│   └── main.py                 ← brain_tools/ralph.py
└── shared/
    ├── __init__.py
    ├── domain/                 ← brain_tools/domain/
    ├── features/               ← brain_tools/features/
    ├── infrastructure/         ← brain_tools/infrastructure/
    ├── execution_log.py        ← brain_tools/shared/execution_log.py
    ├── log.py                  ← brain_tools/shared/log.py
    └── pr_url.py               ← brain_tools/shared/pr_url.py
tests/                          (unchanged location)
```

---

## Steps

### Phase 1 — Create directory skeleton

Create all `__init__.py` stubs:
- `tools/__init__.py`
- `tools/scripts/__init__.py`
- `tools/ralph/__init__.py`
- `tools/shared/__init__.py`
- `tools/shared/domain/__init__.py`
- `tools/shared/domain/services/__init__.py`
- `tools/shared/features/__init__.py`
- `tools/shared/features/fetch_threads/__init__.py`
- `tools/shared/features/review_pull_request/__init__.py`
- `tools/shared/features/review_pull_requests/__init__.py`
- `tools/shared/infrastructure/__init__.py`
- `tools/shared/infrastructure/tests/__init__.py`

### Phase 2 — Move source files + update imports

Copy each file to its new path, rewriting `from brain_tools.` imports:

| Old import prefix            | New import prefix              |
|------------------------------|--------------------------------|
| `brain_tools.domain.`        | `tools.shared.domain.`         |
| `brain_tools.features.`      | `tools.shared.features.`       |
| `brain_tools.infrastructure.`| `tools.shared.infrastructure.` |
| `brain_tools.shared.`        | `tools.shared.`                |

File moves:

| From                                             | To                                                  |
|--------------------------------------------------|-----------------------------------------------------|
| `brain_tools/ralph.py`                           | `tools/ralph/main.py`                               |
| `brain_tools/fetch_threads.py`                   | `tools/scripts/fetch_threads.py`                    |
| `brain_tools/domain/*.py`                        | `tools/shared/domain/*.py`                          |
| `brain_tools/domain/services/*.py`               | `tools/shared/domain/services/*.py`                 |
| `brain_tools/features/fetch_threads/handler.py`  | `tools/shared/features/fetch_threads/handler.py`    |
| `brain_tools/features/review_pull_request/handler.py` | `tools/shared/features/review_pull_request/handler.py` |
| `brain_tools/features/review_pull_requests/handler.py` | `tools/shared/features/review_pull_requests/handler.py` |
| `brain_tools/infrastructure/*.py`                | `tools/shared/infrastructure/*.py`                  |
| `brain_tools/infrastructure/tests/fake_gh_cli.py`| `tools/shared/infrastructure/tests/fake_gh_cli.py`  |
| `brain_tools/shared/execution_log.py`            | `tools/shared/execution_log.py`                     |
| `brain_tools/shared/log.py`                      | `tools/shared/log.py`                               |
| `brain_tools/shared/pr_url.py`                   | `tools/shared/pr_url.py`                            |

### Phase 3 — Update imports in test files

Rewrite all `from brain_tools.` imports in `tests/` with the same mapping (no file moves needed).

### Phase 4 — Update pyproject.toml

1. Change `include = ["brain_tools*"]` → `include = ["tools*"]`
2. Update entry points:
   - `ralph = "tools.ralph.main:main"`
   - `fetch-threads-script = "tools.scripts.fetch_threads:main"`

### Phase 5 — Remove old directory *(destructive — confirm before doing)*

Delete `brain_tools/`.

---

## Verification

1. `pip install -e ".[dev]"` — reinstall with new package layout
2. `python3 -m pytest tests/ -v` — all tests pass
3. `ralph --help` and `fetch-threads-script` — CLI entry points resolve correctly
