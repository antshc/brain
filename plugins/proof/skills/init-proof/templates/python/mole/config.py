"""What the mole needs to know about this repo's app. proof/app.py fills it in."""

from __future__ import annotations

import re
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from proof.kit import Surface

if TYPE_CHECKING:
    from playwright.sync_api import Page


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
    """Everything the mole needs to know about this repo's app. proof/app.py fills it in."""

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
