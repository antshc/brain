from __future__ import annotations

from collections.abc import Callable
from dataclasses import asdict
from typing import Any

from proof.kit import FlowContext
from proof.kit.logs import LogRecord


class LogEvidence:
    """Project evidence: the records of one run, parsed by a log adapter and read through `LogView` in a check. `load` returns the complete capture."""

    label = "log"
    suffix = ".json"

    def __init__(self, load: Callable[[FlowContext], list[LogRecord]], *, name: str = "log") -> None:
        self.load = load
        self.name = name

    def capture(self, context: FlowContext) -> Any:
        return {"records": [asdict(record) for record in self.load(context)]}
