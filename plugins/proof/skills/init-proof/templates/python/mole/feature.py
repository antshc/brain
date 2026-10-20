from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from proof.kit import Feature, Surface

if TYPE_CHECKING:
    from playwright.sync_api import Page


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
class MoleFeature(Feature):
    """A proof feature the mole can also drive by hand."""

    # Optional: lets `mole <feature> <verb>` drive the feature by hand. Return JSON-able data; raise SurfaceError for user mistakes.
    drive: DriveHook | None = None
