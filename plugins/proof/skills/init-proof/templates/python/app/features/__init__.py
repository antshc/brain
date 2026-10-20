from __future__ import annotations

from mole.feature import MoleFeature

from .example import prove_example

# Each key has a map at .github/skills/verify-mole/features/<key>.md. `{{TEST_PROOF}}` keeps the two in step.
# A feature may add `drive=DriveHook(usage, summary, run)` (from mole.feature) so `{{MOLE}} <key> <verb>` can drive it by hand.
FEATURES: dict[str, MoleFeature] = {
    # Placeholder: replace it with real features, or keep it as a smoke check.
    "example": MoleFeature(
        prove=prove_example,
        surfaces=[{{SURFACES_LIST}}],
        touches=["src/"],  # TODO(proof): the path prefixes of this feature's files
    ),
}
