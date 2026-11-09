"""Builds the Jira Cloud client shared by `fetch-work` and `publish-work`."""
from __future__ import annotations

from typing import Any

from . import config


def get_jira(credentials: dict[str, str]) -> Any:
    config.require_supported_library()
    from atlassian import Jira

    return Jira(
        url=config.site_url(credentials),
        username=credentials["email"],
        password=credentials["token"],
        cloud=True,
    )
