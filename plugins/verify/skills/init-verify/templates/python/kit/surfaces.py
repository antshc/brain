from __future__ import annotations

from collections.abc import Sequence
from typing import TypeGuard

from .types import Surface, SurfaceError

__all__ = ["ALL_SURFACES", "SurfaceError", "is_surface", "select_surfaces"]

ALL_SURFACES: tuple[Surface, ...] = ("web", "api")


def is_surface(value: str) -> TypeGuard[Surface]:
    return value in ALL_SURFACES


# No names means every available surface. An unknown name is the caller's mistake, so say what exists.
def select_surfaces(names: Sequence[str], available: Sequence[Surface]) -> list[Surface]:
    unknown = [name for name in names if not is_surface(name)]
    if unknown:
        raise ValueError(f'Unknown surface "{", ".join(unknown)}". Surfaces: {", ".join(ALL_SURFACES)}')
    chosen = [name for name in dict.fromkeys(names) if is_surface(name)]
    missing = [name for name in chosen if name not in available]
    if missing:
        raise ValueError(f'This feature has no "{", ".join(missing)}" surface. It has: {", ".join(available)}')
    return chosen or list(available)
