from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from ...engine.model import Surface, SurfaceError

__all__ = ["AppApi", "AppStatus", "Surface", "SurfaceAdapter", "SurfaceError"]


# What a feature does, said once. Each surface turns the same call into its own way of driving the app
# and returns the same shape, so a contract rule is written once and checked on every surface.
@dataclass(frozen=True)
class AppStatus:
    surface: Surface
    ok: bool
    status: int


class AppApi(Protocol):
    def status(self) -> AppStatus:
        """Does the app answer on this surface?"""
        ...


class SurfaceAdapter(Protocol):
    @property
    def surface(self) -> Surface: ...

    @property
    def app(self) -> AppApi: ...
