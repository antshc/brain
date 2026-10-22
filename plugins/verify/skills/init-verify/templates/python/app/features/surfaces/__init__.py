from __future__ import annotations

from typing import Protocol

from playwright.sync_api import Page

from proof.kit import Surface
from .types import AppApi, AppStatus, SurfaceAdapter, SurfaceError
# <surface: api>
from .api import ApiSurface, api_surface
# </surface: api>
# <surface: web>
from .web import COLD, WebSurface, web_surface
# </surface: web>

__all__ = [
    "AppApi", "AppStatus", "SurfaceAdapter", "SurfaceError", "Target", "adapter_for",
    # <surface: web>
    "COLD", "WebSurface", "web_surface",
    # </surface: web>
    # <surface: api>
    "ApiSurface", "api_surface",
    # </surface: api>
]


class Target(Protocol):
    """A FlowContext (or the page and API URL of any other run) for the adapters below."""

    @property
    def page(self) -> Page | None: ...

    @property
    def api_url(self) -> str | None: ...


# A surface's adapter for one run. The API has no browser and needs the URL that `up` recorded; without it every call says so.
def adapter_for(surface: Surface, target: Target) -> SurfaceAdapter:
    # <surface: web>
    if surface == "web":
        if target.page is None:
            raise ValueError("The web surface needs a browser page.")
        return web_surface(target.page)
    # </surface: web>
    # <surface: api>
    if surface == "api":
        return api_surface(target.api_url)
    # </surface: api>
    raise ValueError(f"The {surface} surface is not supported by this repo's proof kit.")
