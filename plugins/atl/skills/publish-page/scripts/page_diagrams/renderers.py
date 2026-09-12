"""Renderer vocabulary and readiness gate for `ATLASSIAN_DIAGRAM_RENDERER`.

Three modes: `png` rasterises the diagram with mmdc, `drawio` produces an editable Draw.io
diagram, `mermaid` publishes the source as a live Confluence macro. All three run mmdc — as
the renderer for `png`, as a syntax gate for the other two.

`mermaid` is recognised but cannot publish yet: it replaces the marker with a Confluence
macro, and section 7 of docs/ongoing/publish-page-diagram-renderers.md requires capturing a
real macro via `body-format=atlas_doc_format` before that ADF shape is written, because
Connect and Forge installations represent the same macro differently. Keeping that refusal
here lets the pipeline fail before it touches a page instead of publishing a guess.
"""
from __future__ import annotations

PNG = "png"
DRAWIO = "drawio"
MERMAID = "mermaid"

NAMES = (PNG, DRAWIO, MERMAID)
DEFAULT = PNG

_PENDING_MACRO_CAPTURE = (
    "renderer {name!r} is not usable yet: its Confluence macro ADF shape must first be "
    "captured from a real diagram via body-format=atlas_doc_format (see "
    "docs/ongoing/publish-page-diagram-renderers.md section 7). Set "
    "ATLASSIAN_DIAGRAM_RENDERER=png to publish now."
)


def validate(name: str) -> str:
    """Return `name` if it is a known renderer; raise `ValueError` naming the alternatives."""
    if name not in NAMES:
        raise ValueError(
            f"ATLASSIAN_DIAGRAM_RENDERER={name!r} is not supported; expected one of {', '.join(NAMES)}"
        )
    return name


def unavailable_reason(name: str) -> str | None:
    """Why `name` cannot publish yet, or `None` when it can."""
    if name == MERMAID:
        return _PENDING_MACRO_CAPTURE.format(name=name)
    return None
