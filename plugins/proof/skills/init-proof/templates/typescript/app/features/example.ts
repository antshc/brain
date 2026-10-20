import { observe, type ProofKit } from "../kit";
import { adapterFor } from "./surfaces";

// Map: .github/skills/verify-mole/features/example.md
// The contract is checked through each surface's adapter, so a rule is written once and proved everywhere.
export async function proveExample(kit: ProofKit) {
  for (const surface of kit.surfaces) {
    const name = (rule: string) => `example/${surface}: ${rule}`;
    const status = await observe(kit, name("reaches the app"), () => adapterFor(surface, kit).app.status());
    if (status) kit.check(name("the app answers"), status.ok, true, `The ${surface} surface did not answer well. Is the app up and the build fresh? pnpm mole doctor`);
  }
}
