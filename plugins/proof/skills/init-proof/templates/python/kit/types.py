from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Literal, Protocol

if TYPE_CHECKING:
    from playwright.sync_api import Page

# A surface is one way a feature reaches a user: `web` is the app in a real Chrome, `api` is HTTP.
Surface = Literal["web", "api"]


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
    # What to tell the reader to do when a surface cannot be observed. Supplied by the caller of run_proof.
    diagnose: str
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
class Feature:
    """A named proof: what it proves, on which surfaces, and which files it must be re-proved for."""

    prove: Prove
    # Repo-relative path prefixes whose changes this feature must be re-proved for.
    touches: list[str]
    # The surfaces the feature is proved on. The map's frontmatter lists the same.
    surfaces: list[Surface]
