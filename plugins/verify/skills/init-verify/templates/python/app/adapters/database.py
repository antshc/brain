from __future__ import annotations

from typing import Any, Protocol

from proof.kit import FlowContext


class ResourceReader(Protocol):
    def get_resource(self, kind: str, key: str) -> dict[str, Any] | None: ...


class DatabaseEvidence:
    """Project evidence: one database resource, read through an adapter from proof/tools/database.py. Read only."""

    label = "database"
    suffix = ".json"

    def __init__(self, reader: ResourceReader, kind: str, key: str, *, name: str = "database") -> None:
        self.reader = reader
        self.kind = kind
        self.key = key
        self.name = name

    def capture(self, context: FlowContext) -> Any:
        return {"kind": self.kind, "key": self.key, "resource": self.reader.get_resource(self.kind, self.key)}
