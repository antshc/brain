"""Publish-side config: credentials that raise naming every missing key, plus renderer
settings. Parsing and site normalization come from the shared `config` module.
"""
from __future__ import annotations

import re

from ..config import load_config, site_url  # noqa: F401  site_url re-exported for the pipeline
from . import renderers

DRAWIO_EXTENSION_KEY = "drawioExtensionKey"

_EXTENSION_KEY_RE = re.compile(r"\A[^/\s]+/[^/\s]+/static/[^/\s]+\Z")


def load_credentials(config_path: str) -> dict[str, str]:
    """Return `site`/`email`/`token`; raises `SystemExit` naming the missing key(s)."""
    config = load_config(config_path)
    site = str(config.get("cloudId", "")).strip()  # config key is `cloudId`, not `site`
    email = str(config.get("email", "")).strip()
    token = str(config.get("apiToken", "")).strip()
    missing = [
        name
        for name, value in (
            ("cloudId", site),
            ("email", email),
            ("apiToken", token),
        )
        if not value
    ]
    if missing:
        raise SystemExit(f"error: .atlassian.json.user missing required key(s): {', '.join(missing)}")
    return {"site": site, "email": email, "token": token}


def load_renderer(config_path: str) -> str:
    """Return the configured diagram renderer, defaulting to `png` when the key is absent.

    Unlike `load_credentials`, a missing config is not an error here — the default keeps
    existing repos publishing exactly as they did before the key existed.
    """
    config = load_config(config_path)
    name = str(config.get("diagramRenderer", "")).strip() or renderers.DEFAULT
    return renderers.validate(name)


def load_swimlane_drawio_enabled(config_path: str) -> bool:
    """Whether `swimlaneDrawio` opts into the native swimlane-beta-to-drawio converter; defaults
    to `True`, opting out only on an explicit falsy value.
    """
    config = load_config(config_path)
    value = str(config.get("swimlaneDrawio", "")).strip().lower()
    if not value:
        return True
    return value not in ("0", "false", "no")


def load_drawio_extension_key(config_path: str) -> str:
    """Return the Draw.io Forge extension key; raise `ValueError` when absent or malformed.

    The key embeds the app id and the environment id, both of which differ per site and per
    install, so it cannot be hard-coded and has no usable default.
    """
    config = load_config(config_path)
    key = str(config.get(DRAWIO_EXTENSION_KEY, "")).strip()
    if not key:
        raise ValueError(
            f"diagramRenderer=drawio needs {DRAWIO_EXTENSION_KEY} in .atlassian.json.user; it embeds "
            "the Draw.io app id and environment id, which differ per site. To find it, read a page "
            "that already carries a Draw.io diagram as raw ADF (REST v2 body-format=atlas_doc_format) and copy the diagram "
            "node's attrs.extensionKey."
        )
    if not _EXTENSION_KEY_RE.match(key):
        raise ValueError(
            f"atl.{DRAWIO_EXTENSION_KEY}={key!r} is malformed; expected <appId>/<envId>/static/drawio"
        )
    return key
