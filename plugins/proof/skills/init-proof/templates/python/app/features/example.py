from __future__ import annotations

from ..engine.commands import MOLE
from ..engine.model import ProofKit
from ..engine.surfaces import observe
from .surfaces import adapter_for


# Map: .github/skills/verify-mole/features/example.md
# The contract is checked through each surface's adapter, so a rule is written once and proved everywhere.
def prove_example(kit: ProofKit) -> None:
    for surface in kit.surfaces:

        def name(rule: str) -> str:
            return f"example/{surface}: {rule}"

        status = observe(kit, name("reaches the app"), lambda: adapter_for(surface, kit).app.status())
        if status:
            kit.check(name("the app answers"), status.ok, True, f"The {surface} surface did not answer well. Is the app up and the build fresh? {MOLE} doctor")
