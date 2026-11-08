from __future__ import annotations

from proof.kit import FlowContext, flow
from proof.pages.home import HomePage


@flow("app.open")
def open_app(context: FlowContext) -> None:
    if "web" in context.surfaces:
        HomePage(context).open()
