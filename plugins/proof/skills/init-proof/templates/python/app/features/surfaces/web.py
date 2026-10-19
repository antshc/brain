from __future__ import annotations

from urllib.parse import urljoin

from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import Page, Response

from ...app import APP
from ...engine.commands import MOLE
from .types import AppStatus, Surface, SurfaceError

# A freshly started app renders its first pages slowly; waits for first renders use this (milliseconds).
COLD = 15_000


def _fail(message: str, next_step: str) -> SurfaceError:
    return SurfaceError("web", message, next_step)


# Everything about the app's pages lives here: selectors, routes, the URL it keeps state in. Features never touch them.
class WebSurface:
    surface: Surface = "web"

    def __init__(self, page: Page) -> None:
        self.page = page
        self.app = _WebApp(self)

    def home(self) -> str:
        return urljoin(self.page.url if self.page.url.startswith("http") else APP.url, "/")

    def settle(self) -> None:
        if APP.web and APP.web.settle:
            APP.web.settle(self.page)
        else:
            self.page.wait_for_load_state("load")

    def go(self, url: str) -> Response | None:
        try:
            response = self.page.goto(url, wait_until="load", timeout=COLD)
        except PlaywrightError as exception:
            raise _fail(f"Can't open {url}: {str(exception).splitlines()[0]}.", f"Is the app up? {MOLE} doctor") from exception
        self.settle()
        return response

    # What only a browser visitor has: the page chrome, URL state, navigation. No other surface has these.
    def url(self) -> str:
        return self.page.url


class _WebApp:
    def __init__(self, web: WebSurface) -> None:
        self._web = web

    def status(self) -> AppStatus:
        response = self._web.go(self._web.home())
        status = response.status if response else 0
        return AppStatus("web", 0 < status < 400, status)


def web_surface(page: Page) -> WebSurface:
    return WebSurface(page)
