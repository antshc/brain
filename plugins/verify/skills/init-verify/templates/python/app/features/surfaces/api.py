from __future__ import annotations

import json
from collections.abc import Callable
from typing import Any
from urllib.parse import urlencode, urljoin, urlsplit

from mole.commands import MOLE
from mole.runtime import HttpResponse, fetch
from .types import AppStatus, Surface, SurfaceError


# Everything about the HTTP wire lives here: base path, versioning, auth headers, paging and id translation.
# Features see the same shapes the other surfaces return.
class ApiSurface:
    surface: Surface = "api"

    def __init__(self, base_url: str | None, fetcher: Callable[[str], HttpResponse] = fetch) -> None:
        self.base_url = base_url
        self._fetcher = fetcher
        self.app = _ApiApp(self)

    def _fail(self, message: str, next_step: str = f"Is the app running? {MOLE} doctor") -> SurfaceError:
        return SurfaceError("api", message, next_step)

    def request(self, path: str, params: dict[str, Any] | None = None) -> HttpResponse:
        if not self.base_url:
            raise self._fail("No API URL is known for this run.", f"Start the app, then: {MOLE} down; {MOLE} up. Or set PROOF_API_URL.")
        query = urlencode({key: value for key, value in (params or {}).items() if value is not None})
        url = urljoin(self.base_url, path) + (f"?{query}" if query else "")
        try:
            return self._fetcher(url)
        except OSError as exception:
            split = urlsplit(url)
            raise self._fail(
                f"Can't reach {split.scheme}://{split.netloc}: {exception}.",
                f"Check the app is running and the URL is right: {MOLE} doctor. To set it by hand: PROOF_API_URL=<url>",
            ) from exception

    def json(self, path: str, params: dict[str, Any] | None = None) -> Any:
        response = self.request(path, params)
        if not 200 <= response.status < 300:
            raise self._fail(f"GET {path} answered {response.status}.", "Check the route in the app's API definition.")
        return json.loads(response.body)


class _ApiApp:
    def __init__(self, api: ApiSurface) -> None:
        self._api = api

    def status(self) -> AppStatus:
        response = self._api.request("/")
        return AppStatus("api", response.status < 500, response.status)


def api_surface(base_url: str | None, fetcher: Callable[[str], HttpResponse] = fetch) -> ApiSurface:
    return ApiSurface(base_url, fetcher)
