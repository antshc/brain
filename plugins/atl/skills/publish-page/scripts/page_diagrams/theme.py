"""Recolors dark-theme mermaid hex codes to a Confluence-page-friendly light palette
before rendering. Pure string substitution — the source markdown is never touched, only
the throwaway `.mmd` written to the assets dir at render time. A no-op for diagrams that
don't use these specific hex codes.
"""
from __future__ import annotations

# 1:1 hex swap covering the dark-theme palette used by common diagram templates
# (fill/stroke/text/added/removed/person-accent).
LIGHT_THEME_COLOR_MAP = {
    "#8b949e": "#57606a",  # stroke / lineColor / signalColor
    "#2a2a2a": "#f6f8fa",  # fill / actorBkg / noteBkgColor / activationBkgColor
    "#c9d1d9": "#24292f",  # text
    "#4a7a5a": "#1a7f37",  # added stroke
    "#8a4a4a": "#cf222e",  # removed stroke
    "#4a5a8a": "#0969da",  # C4 Person accent border
}

# Override for mermaid's hardcoded `.cluster rect` rule (classDiagram `namespace`, flowchart
# `subgraph`) — not reachable via `themeVariables`, so it's injected into `mmdc` via `--cssFile`.
LIGHT_THEME_CSS = """\
.cluster rect { fill: #eaeef2 !important; stroke: #8c959f !important; }
.cluster-label text, .cluster-label span { fill: #24292f !important; color: #24292f !important; }
"""


def apply_light_theme(code: str) -> str:
    """Swap every dark-theme hex code in a mermaid diagram's source for its light equivalent."""
    for dark, light in LIGHT_THEME_COLOR_MAP.items():
        code = code.replace(dark, light)
    return code
