"""Shared types of the proof kit. Imports nothing from the app or the features, so both can import it."""

from __future__ import annotations

import re
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Literal, Protocol, TypeGuard

if TYPE_CHECKING:
    from playwright.sync_api import Page

# A surface is one way a feature reaches a user: `web` is the app in a real Chrome, `api` is HTTP.
Surface = Literal["web", "api"]
ALL_SURFACES: tuple[Surface, ...] = ("web", "api")


def is_surface(value: str) -> TypeGuard[Surface]:
    return value in ALL_SURFACES


class SurfaceError(Exception):
    def __init__(self, surface: Surface, message: str, next_step: str) -> None:
        super().__init__(f"{surface}: {message}")
        self.surface = surface
        self.next_step = next_step


@dataclass(frozen=True)
class StartConfig:
    """How `mole up --start` runs the app. Omit `AppConfig.start` when the app is always started by hand."""

    command: str
    args: list[str] = field(default_factory=list)
    env: dict[str, str] = field(default_factory=dict)
    cwd: str | None = None
    # Raises with an actionable message when a tool is missing. May return extra environment for the command.
    prerequisites: Callable[[], dict[str, str] | None] | None = None
    # The app has answered `url`; return True once it is really ready (seed loaded, first render done).
    ready: Callable[[str], bool] | None = None
    timeout_s: float = 120.0


@dataclass(frozen=True)
class ApiConfig:
    # The API base URL, when it is not the app URL or PROOF_API_URL.
    discover: Callable[[], str | None] | None = None
    # Whether the API really answers at this base URL. Default: any answer below 500.
    probe: Callable[[str], bool] | None = None


@dataclass(frozen=True)
class WebConfig:
    # Wait until a page has finished rendering. Default: the load event.
    settle: Callable[[Page], None] | None = None
    # What a user sees, merged into `mole snapshot`. Default: url, title, h1, aria.
    snapshot: Callable[[Page], dict[str, Any]] | None = None


@dataclass(frozen=True)
class AppConfig:
    """Everything the engine needs to know about this repo's app. proof/app.py fills it in."""

    name: str
    # Where the app answers by default. `--url` overrides it.
    url: str
    # The surfaces this repo supports. Features may only use these.
    surfaces: list[Surface]
    # Repo-relative paths whose changes alter the running build. The revision is derived from them.
    source_paths: list[str]
    # Where the feature maps live.
    feature_maps: str = ".github/skills/verify-mole/features"
    # Extra patterns a feature map must not contain (selectors, routes, wire details).
    map_banned: list[re.Pattern[str]] = field(default_factory=list)
    start: StartConfig | None = None
    api: ApiConfig | None = None
    web: WebConfig | None = None


@dataclass(frozen=True)
class Check:
    name: str
    passed: bool
    expected: Any
    actual: Any
    hint: str | None = None

    def to_json(self) -> dict[str, Any]:
        data: dict[str, Any] = {"name": self.name, "pass": self.passed, "expected": self.expected, "actual": self.actual}
        if self.hint:
            data["hint"] = self.hint
        return data


class CheckFn(Protocol):
    def __call__(self, name: str, actual: Any, expected: Any, hint: str | None = None) -> None: ...


@dataclass(frozen=True)
class ProofKit:
    # A fresh visitor (no storage) with the app already loaded. Blank when the run has no web surface.
    page: Page
    # The surfaces this run proves. A feature checks its contract on each.
    surfaces: list[Surface]
    # Where the API answers, or None when the run has no API.
    api_url: str | None
    # Record one fact. Never raises: a failed check is evidence, not a crash.
    check: CheckFn
    # localStorage for the app's origin, read through the DevTools protocol.
    storage: Callable[[], dict[str, Any]]


Prove = Callable[[ProofKit], None]


@dataclass
class Receipt:
    verdict: Literal["PASS", "FAIL", "ERROR"]
    revision: str | None
    app: str
    at: str
    checks: list[Check] = field(default_factory=list)
    # The features this run proved. A subset is not a full proof.
    features: list[str] | None = None
    # The surfaces this run proved. A surface that did not run is not proved.
    surfaces: list[Surface] | None = None
    page_errors: list[str] = field(default_factory=list)
    screenshot: str | None = None
    error: str | None = None
    next_steps: list[str] = field(default_factory=list)

    def to_json(self) -> dict[str, Any]:
        data: dict[str, Any] = {
            "verdict": self.verdict,
            "revision": self.revision,
            "app": self.app,
            "at": self.at,
            "checks": [check.to_json() for check in self.checks],
        }
        if self.features is not None:
            data["features"] = self.features
        if self.surfaces is not None:
            data["surfaces"] = self.surfaces
        data["pageErrors"] = self.page_errors
        if self.screenshot:
            data["screenshot"] = self.screenshot
        if self.error:
            data["error"] = self.error
        data["next"] = self.next_steps
        return data


@dataclass(frozen=True)
class DriveCall:
    """One `mole <feature> <verb> ...` call, handed to the feature's `drive` hook."""

    # Every token after the feature name (the verb first), with --surface removed.
    argv: list[str]
    # The surface to drive on: web unless told otherwise (or the feature has no web).
    surface: Surface
    # The attached page on the web surface, otherwise None.
    page: Page | None
    # The API base URL on the api surface, otherwise None.
    api_url: str | None


@dataclass(frozen=True)
class DriveHook:
    usage: str
    summary: str
    run: Callable[[DriveCall], dict[str, Any]]


@dataclass(frozen=True)
class Feature:
    prove: Prove
    # Repo-relative path prefixes whose changes this feature must be re-proved for.
    touches: list[str]
    # The surfaces the feature is proved on. The map's frontmatter lists the same.
    surfaces: list[Surface]
    # Optional: lets `mole <feature> <verb>` drive the feature by hand. Return JSON-able data; raise SurfaceError for user mistakes.
    drive: DriveHook | None = None
