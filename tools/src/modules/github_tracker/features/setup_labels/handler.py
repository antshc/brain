"""Setup Labels use case: creates any GitHub labels `manage-backlog` needs that are missing."""

from ...domain.label_result import LabelResult
from ...domain.label_spec import LABEL_CATALOG
from ...infrastructure.gh_cli import GhCli


def setup_labels(*, gh: GhCli | None = None) -> list[LabelResult]:
    """Ensure every label in LABEL_CATALOG exists on the resolved repo.

    Leaves already-existing labels unchanged; creates any missing ones with the
    catalog's documented name, color, and description.
    """
    gh = gh or GhCli()
    repo = gh.resolve_repo()
    existing = set(gh.label_names(repo))

    results = []
    for label in LABEL_CATALOG:
        if label.name in existing:
            results.append(LabelResult(name=label.name, created=False))
        else:
            gh.label_create(repo, label.name, label.color, label.description)
            results.append(LabelResult(name=label.name, created=True))
    return results
