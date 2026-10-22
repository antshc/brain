from __future__ import annotations

import json
from collections.abc import Callable
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urljoin, urlsplit

from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import Page

from .types import EventWindow, EvidenceAdapter, EvidenceRef, FlowContext, SurfaceError


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def _parse(value: str) -> Any:
    try:
        return json.loads(value)
    except ValueError:
        return value


def read_storage(page: Page) -> dict[str, Any]:
    split = urlsplit(page.url)
    cdp = page.context.new_cdp_session(page)
    try:
        cdp.send("DOMStorage.enable")
        result = cdp.send(
            "DOMStorage.getDOMStorageItems",
            {"storageId": {"securityOrigin": f"{split.scheme}://{split.netloc}", "isLocalStorage": True}},
        )
        return {key: _parse(value) for key, value in result["entries"]}
    finally:
        cdp.detach()


class Collectors:
    """Listens from before the first action, so a checkpoint sees everything since the previous one and nothing from before."""

    def __init__(self) -> None:
        self._console: list[dict[str, Any]] = []
        self._network: list[dict[str, Any]] = []
        self._errors: list[str] = []

    def attach(self, page: Page) -> None:
        page.on("console", lambda message: self._console.append({"level": message.type, "text": message.text}))
        page.on("pageerror", lambda error: self._errors.append(error.message))
        page.on("response", lambda response: self._network.append({
            "type": "response", "method": response.request.method, "resource": response.request.resource_type, "status": response.status, "url": response.url,
        }))
        page.on("requestfailed", lambda request: self._network.append({
            "type": "requestfailed", "method": request.method, "resource": request.resource_type, "url": request.url, "text": request.failure,
        }))

    def mark(self) -> tuple[int, int, int]:
        return len(self._console), len(self._network), len(self._errors)

    def window(self, since: tuple[int, int, int] = (0, 0, 0)) -> EventWindow:
        console, network, errors = since
        return EventWindow(tuple(self._console[console:]), tuple(self._network[network:]), tuple(self._errors[errors:]))

    # Console errors and uncaught exceptions of the whole run; a PASS does not fail on them, the receipt lists them.
    def page_errors(self) -> list[str]:
        return list(dict.fromkeys([*self._errors, *(entry["text"] for entry in self._console if entry["level"] == "error")]))


class BrowserSnapshot:
    name = "browser-snapshot"
    label = "browser snapshot"
    suffix = ".json"

    def capture(self, context: FlowContext) -> Any:
        page = context.page
        heading = page.get_by_role("heading", level=1)
        try:
            aria: str | None = page.locator("body").aria_snapshot(timeout=1500)
        except PlaywrightError:
            aria = None
        return {"url": page.url, "title": page.title(), "heading": heading.first.inner_text().strip() if heading.count() else None, "aria": aria}


class Screenshot:
    name = "screenshot"
    label = "screenshot"
    suffix = ".png"

    def capture(self, context: FlowContext) -> Any:
        return context.page.screenshot(full_page=True)


class ConsoleLog:
    name = "console-log"
    label = "console log"
    suffix = ".json"

    def capture(self, context: FlowContext) -> Any:
        return {"messages": list(context.window.console), "pageErrors": list(context.window.page_errors)}


class NetworkLog:
    name = "network-log"
    label = "network log"
    suffix = ".json"

    def capture(self, context: FlowContext) -> Any:
        entries = context.window.network
        return {
            "responses": [entry for entry in entries if entry["type"] == "response"],
            "failed": [entry for entry in entries if entry["type"] == "requestfailed"],
        }


class StorageState:
    name = "storage"
    label = "storage"
    suffix = ".json"

    def capture(self, context: FlowContext) -> Any:
        return {"localStorage": read_storage(context.page), "cookies": [cookie["name"] for cookie in context.page.context.cookies()]}


class ApiResponse:
    """GET one API path. The path belongs to the project's check, not to the kit."""

    label = "API response"
    suffix = ".json"

    def __init__(self, path: str, *, name: str = "api-response") -> None:
        self.path = path
        self.name = name

    def capture(self, context: FlowContext) -> Any:
        if not context.api_url:
            raise SurfaceError("api", "No API URL is known for this run.", "Start the app so the API is found, or set PROOF_API_URL.")
        url = urljoin(context.api_url, self.path)
        answer = context.fetch(url)
        try:
            body: Any = json.loads(answer.body)
        except ValueError:
            body = answer.body[:4000]
        return {"url": url, "status": answer.status, "body": body}


class EvidenceError(Exception):
    pass


def _write(path: Path, data: Any) -> None:
    if isinstance(data, bytes):
        path.write_bytes(data)
    else:
        path.write_text(json.dumps(data, indent=2, default=repr))


# Persist what one adapter saw for one check. A capture that fails or sees nothing leaves a diagnostic artifact and raises:
# the check cannot pass on evidence that was never kept.
def capture(adapter: EvidenceAdapter, context: FlowContext, *, check: str, step: int, directory: Path, now: Callable[[], str] = now_iso) -> tuple[EvidenceRef, Any]:
    folder = f"{step:02d}-{check}"
    (directory / folder).mkdir(parents=True, exist_ok=True)
    try:
        data = adapter.capture(context)
        if data is None:
            raise EvidenceError("The adapter observed nothing.")
        if isinstance(data, bytes) != (adapter.suffix != ".json"):
            raise EvidenceError(f"The adapter returned {type(data).__name__} for a {adapter.suffix} artifact.")
        _write(directory / folder / f"{adapter.name}{adapter.suffix}", data)
    except Exception as exception:  # An adapter may raise anything; that is a failed capture, not a crash of the kit.
        message = f"{type(exception).__name__}: {str(exception).splitlines()[0] if str(exception) else ''}".strip()
        _write(directory / folder / f"{adapter.name}.error.json", {"source": adapter.name, "error": message})
        raise EvidenceError(f'Could not capture "{adapter.label}" for check "{check}" ({message}).') from exception
    reference = EvidenceRef(check, adapter.name, adapter.label, f"{folder}/{adapter.name}{adapter.suffix}", now(), step)
    return reference, {"bytes": len(data)} if isinstance(data, bytes) else data
