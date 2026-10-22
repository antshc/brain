from __future__ import annotations

from collections.abc import Callable, Iterable, Sequence
from typing import Any


def same(actual: Any, expected: Any) -> bool:
    """Deep equality that, unlike ==, does not treat True as 1."""
    if isinstance(actual, bool) or isinstance(expected, bool):
        return isinstance(actual, bool) and isinstance(expected, bool) and actual == expected
    if isinstance(actual, dict) and isinstance(expected, dict):
        return actual.keys() == expected.keys() and all(same(actual[key], expected[key]) for key in actual)
    if isinstance(actual, (list, tuple)) and isinstance(expected, (list, tuple)):
        return len(actual) == len(expected) and all(same(left, right) for left, right in zip(actual, expected))
    return bool(actual == expected)



def matches_fields(actual: Any, expected_subset: Any) -> bool:
    if isinstance(expected_subset, dict):
        return isinstance(actual, dict) and all(
            key in actual and matches_fields(actual[key], value) for key, value in expected_subset.items()
        )
    return same(actual, expected_subset)


def contains_item(items: Any, expected_subset: Any) -> bool:
    return isinstance(items, (list, tuple)) and any(matches_fields(item, expected_subset) for item in items)


def count_matches(items: Iterable[Any], predicate: Callable[[Any], bool], *,
                  min_count: int | None = None, max_count: int | None = None, equals: int | None = None) -> bool:
    bounds = (min_count, max_count, equals)
    if all(value is None for value in bounds):
        raise ValueError("Declare a count bound")
    if any(value is not None and (type(value) is not int or value < 0) for value in bounds):
        raise ValueError("Count bounds must be nonnegative integers")
    if equals is not None and (min_count is not None or max_count is not None):
        raise ValueError("Use equals or bounds")
    if min_count is not None and max_count is not None and min_count > max_count:
        raise ValueError("Inverted count bounds")
    count = sum(1 for item in items if _predicate(predicate, item))
    return ((equals is None or count == equals) and (min_count is None or count >= min_count)
            and (max_count is None or count <= max_count))


def _predicate(predicate: Callable[[Any], bool], value: Any) -> bool:
    result = predicate(value)
    if type(result) is not bool:
        raise ValueError("Predicate must return bool")
    return result


def field_satisfies(actual: Any, path: str | Sequence[str | int], predicate: Callable[[Any], bool]) -> bool:
    parts: Sequence[str | int] = path.split(".") if isinstance(path, str) else path
    if not parts or any(type(part) not in (str, int) or part == "" for part in parts):
        raise ValueError("Use field names or list indices")
    for part in parts:
        if isinstance(actual, dict) and part in actual:
            actual = actual[part]
        elif isinstance(actual, list) and type(part) is int and 0 <= part < len(actual):
            actual = actual[part]
        else:
            return False
    return _predicate(predicate, actual)
