from dataclasses import dataclass


@dataclass(frozen=True)
class LabelResult:
    """Outcome of ensuring one label exists: whether it was just created or already existed."""

    name: str
    created: bool
