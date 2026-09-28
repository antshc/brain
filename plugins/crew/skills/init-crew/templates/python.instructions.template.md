---
applyTo: "**/*.py"
---
# Python code conventions

- Follow observed repository structure and formatting before applying these defaults. Keep changes inside the affected package.
- Start new modules with `from __future__ import annotations`; use PEP 604/585 hints (`str | None`, `list[str]`) and module-level imports unless the project uses lazy imports.
- Use `snake_case` for functions/variables, `PascalCase` for classes, frozen dataclasses for simple immutable values, f-strings for interpolation, and `pathlib.Path` where appropriate.
- Check the actual exception type before adding `except`; name caught exceptions `exception`; avoid bare or blanket exception handling for control flow.
- Avoid mutable default arguments and shared state across invocations.
- Put user-facing errors on stderr; reuse existing logging for diagnostics.
- Inject clock, sleep, and clients where that makes the behavior testable. Avoid new dependencies and unrelated refactors or comments that restate code.
- Update affected behavior tests and runnable entry points. The `codey-py` agent owns the focused verification flow.
