from __future__ import annotations

from proof.checks.app import app_answers
from proof.flows.app import open_app
from proof.kit import Feature, feature


# Map: {{SKILL_DIR}}/features/example.md
# Flows act, checks observe, and the builder composes them. Reuse flows and checks from proof/flows and proof/checks.
def example() -> Feature:
    return (
        feature(
            "example",
            touches=["src/"],  # TODO(proof): the path prefixes of this feature's files
            surfaces=[{{SURFACES_LIST}}],
        )
        .sub_feature("smoke")
        .scenario("app-answers")
        .flow(open_app)
        .proof(app_answers())
        .build()
    )
