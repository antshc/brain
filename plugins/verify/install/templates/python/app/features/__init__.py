from __future__ import annotations

from proof.kit import Registry, registry

from .example import example

# Each feature has a map at {{SKILL_DIR}}/features/<feature>.md. `{{TEST_PROOF}}` keeps the two in step.
# Add a feature by writing proof/features/<feature>.py with the builder, then listing it here.
REGISTRY: Registry = registry(
    # Placeholder: replace it with real features, or keep it as a smoke check.
    example(),
)
