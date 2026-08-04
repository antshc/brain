from dataclasses import dataclass


@dataclass(frozen=True)
class LabelSpec:
    """A label this repo's ticket tracker expects to exist, with its intended styling."""

    name: str
    color: str
    description: str


# Source of truth for `manage-backlog`'s "Ticket tracker: GitHub" > Labels table.
LABEL_CATALOG: tuple[LabelSpec, ...] = (
    LabelSpec(name="hitl", color="fbca04", description="Requires human implementation"),
    LabelSpec(name="spec", color="5319e7", description="Spec task with implementation context"),
)
