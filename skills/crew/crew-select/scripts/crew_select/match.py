"""Match changed file paths against installed Stacks' declared scope, resolving a primary."""
from __future__ import annotations

from fnmatch import fnmatch


def _matches(path: str, globs: list[str]) -> bool:
    normalized = path.replace("\\", "/")
    basename = normalized.rsplit("/", 1)[-1]
    return any(fnmatch(normalized, glob) or fnmatch(basename, glob) for glob in globs)


def select_stacks(changed_files: list[str], stack_scopes: dict[str, list[str]]) -> dict:
    """Match `changed_files` against every installed Stack's glob scope.

    Returns `{"matched": [...sorted stack ids...], "primary": id|None, "detail": {stack: [files]}}`.
    `matched` lists every Stack with at least one matched file; `primary` is the Stack with the
    most matches, ties broken by ascending stack id. A path matching two Stacks' globs counts
    toward both — `detail` is not partitioned.
    """
    detail: dict[str, list[str]] = {}
    for stack_id, globs in stack_scopes.items():
        hits = [f for f in changed_files if _matches(f, globs)]
        if hits:
            detail[stack_id] = hits

    matched = sorted(detail)
    primary = None
    if matched:
        best_count = max(len(hits) for hits in detail.values())
        primary = min(stack_id for stack_id in matched if len(detail[stack_id]) == best_count)

    return {"matched": matched, "primary": primary, "detail": detail}
