from __future__ import annotations

import json
from collections.abc import Callable, Sequence
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

from playwright.sync_api import Browser, Page
from playwright.sync_api import Error as PlaywrightError

from .types import Check, ProofKit, Prove, Receipt, Surface

# The caller supplies a revision of the code under proof, or it stays None.
Revision = Callable[[], "str | None"]


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


def same(actual: Any, expected: Any) -> bool:
    """Deep equality that, unlike ==, does not treat True as 1."""
    if isinstance(actual, bool) or isinstance(expected, bool):
        return isinstance(actual, bool) and isinstance(expected, bool) and actual == expected
    if isinstance(actual, dict) and isinstance(expected, dict):
        return actual.keys() == expected.keys() and all(same(actual[key], expected[key]) for key in actual)
    if isinstance(actual, (list, tuple)) and isinstance(expected, (list, tuple)):
        return len(actual) == len(expected) and all(same(left, right) for left, right in zip(actual, expected))
    return bool(actual == expected)


def _show(value: Any) -> str:
    return json.dumps(value, default=repr)


def _first_line(exception: BaseException) -> str:
    return str(exception).split("\n")[0]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


# Runs a `prove()` against a running app and returns a receipt. If the revision changes while
# proving, the evidence belongs to two builds and the verdict is "can't tell".
def run_proof(
    browser: Browser,
    app: str,
    prove: Prove,
    *,
    # Where to save a full-page screenshot (web surface only).
    screenshot: Path | None = None,
    revision: Revision = lambda: None,
    # The surfaces this run proves.
    surfaces: Sequence[Surface] = ("web",),
    api_url: str | None = None,
    # The feature names this run proves, recorded on the receipt.
    features: Sequence[str] | None = None,
    # How to run the proof again, quoted in a FAIL receipt.
    rerun: str = "Run the proof again",
    # What to do when the verdict is "can't tell" or a surface cannot be observed.
    diagnose: str = "Check that the app is running and the build is fresh",
) -> Receipt:
    checks: list[Check] = []
    page_errors: dict[str, None] = {}
    run_surfaces = list(surfaces)
    receipt = Receipt(
        verdict="ERROR", revision=None, app=app, at=_now(), checks=checks,
        features=None if features is None else list(features), surfaces=run_surfaces,
    )

    def check(name: str, actual: Any, expected: Any, hint: str | None = None) -> None:
        checks.append(Check(name, same(actual, expected), expected, actual, hint))

    context = browser.new_context(ignore_https_errors=True)  # fresh visitor: no storage, no cookies
    try:
        page = context.new_page()
        page.set_default_timeout(2500)
        page.on("pageerror", lambda error: page_errors.setdefault(error.message))
        page.on("console", lambda message: page_errors.setdefault(message.text) if message.type == "error" else None)
        receipt.revision = revision()
        if "web" in run_surfaces:
            page.goto(app, wait_until="load", timeout=5000)
        try:
            prove(ProofKit(page=page, surfaces=run_surfaces, api_url=api_url, diagnose=diagnose, check=check, storage=lambda: read_storage(page)))
        except Exception as exception:  # A feature may raise anything; that is a finding, not a crash of the kit.
            receipt.error = (
                f"prove() raised: {type(exception).__name__}: {_first_line(exception)}"
                ". If something is missing, that is a finding: record it with check() instead of raising."
            )
        else:
            now = revision()
            if now != receipt.revision:
                receipt.error = f"The source changed while proving (started on {receipt.revision}, now {now}). Evidence from two builds proves neither."
            elif not checks:
                receipt.error = "prove() recorded no checks. Call check(name, actual, expected) for each fact you observe."
            else:
                receipt.verdict = "PASS" if all(item.passed for item in checks) else "FAIL"
        # A run with no web surface has no page worth a picture.
        if screenshot and "web" in run_surfaces:
            try:
                page.screenshot(path=str(screenshot), full_page=True)
                receipt.screenshot = str(screenshot)
            except (PlaywrightError, OSError) as exception:
                # The receipt tells the agent to read the screenshot, so a missing one can't pass.
                receipt.verdict = "ERROR"
                receipt.error = f"Couldn't save the screenshot ({_first_line(exception)}). A receipt without its screenshot can't be read."
    except PlaywrightError as exception:
        receipt.error = f"The browser failed: {_first_line(exception)}"
    finally:
        context.close()
    receipt.page_errors = list(page_errors)
    if receipt.verdict == "PASS":
        receipt.next_steps = [
            "These checks passed on this revision. They cover nothing else: read the screenshot for anything they missed."
            if "web" in run_surfaces
            else "These checks passed on this revision. They cover nothing else."
        ]
    elif receipt.verdict == "FAIL":
        receipt.next_steps = [
            *(item.hint or f'Fix "{item.name}": expected {_show(item.expected)}, got {_show(item.actual)}.' for item in checks if not item.passed),
            f"Then re-run: {rerun}",
        ]
    else:
        receipt.next_steps = [
            receipt.error or "Unknown error.",
            f"Can't tell is not the same as broken. {diagnose}, then prove again.",
        ]
    return receipt
