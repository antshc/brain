from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import TypeVar

from playwright.sync_api import Error as PlaywrightError

from ..app import APP
from .commands import MOLE
from .model import ALL_SURFACES, ProofKit, Surface, SurfaceError, is_surface

__all__ = ["ALL_SURFACES", "SURFACES", "Surface", "SurfaceError", "is_surface", "observe", "select_surfaces"]

T = TypeVar("T")

# The surfaces this repo supports. proof/app.py says which.
SURFACES: tuple[Surface, ...] = tuple(APP.surfaces)


# No names means every available surface. An unknown name is the caller's mistake, so say what exists.
def select_surfaces(names: Sequence[str] = (), available: Sequence[Surface] | None = None) -> list[Surface]:
    pool = list(SURFACES if available is None else available)
    unknown = [name for name in names if not is_surface(name)]
    if unknown:
        raise ValueError(f'Unknown surface "{", ".join(unknown)}". Surfaces: {", ".join(SURFACES)}')
    chosen = [name for name in dict.fromkeys(names) if is_surface(name)]
    missing = [name for name in chosen if name not in pool]
    if missing:
        raise ValueError(f'This feature has no "{", ".join(missing)}" surface. It has: {", ".join(pool)}')
    return chosen or pool


# A surface that cannot be observed is a finding, not a crash: a raise would turn the whole run into "can't tell".
def observe(kit: ProofKit, label: str, step: Callable[[], T]) -> T | None:
    try:
        return step()
    except (SurfaceError, PlaywrightError, OSError) as exception:
        hint = exception.next_step if isinstance(exception, SurfaceError) else f"Is the app up and the build fresh? {MOLE} doctor"
        kit.check(f"{label}: observed", str(exception).split("\n")[0], "an observation", hint)
        return None
