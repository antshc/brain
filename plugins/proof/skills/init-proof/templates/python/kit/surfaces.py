from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import TypeGuard, TypeVar

from playwright.sync_api import Error as PlaywrightError

from .types import ProofKit, Surface

T = TypeVar("T")

ALL_SURFACES: tuple[Surface, ...] = ("web", "api")


def is_surface(value: str) -> TypeGuard[Surface]:
    return value in ALL_SURFACES


class SurfaceError(Exception):
    def __init__(self, surface: Surface, message: str, next_step: str) -> None:
        super().__init__(f"{surface}: {message}")
        self.surface = surface
        self.next_step = next_step


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


# A surface that cannot be observed is a finding, not a crash: a raise would turn the whole run into "can't tell".
def observe(kit: ProofKit, label: str, step: Callable[[], T]) -> T | None:
    try:
        return step()
    except (SurfaceError, PlaywrightError, OSError) as exception:
        hint = exception.next_step if isinstance(exception, SurfaceError) else kit.diagnose
        kit.check(f"{label}: observed", str(exception).split("\n")[0], "an observation", hint)
        return None
