import type { Feature } from "../engine/registry";
import { proveExample } from "./example";

// Each key has a map at .github/skills/verify-mole/features/<key>.md. `pnpm test:proof` keeps the two in step.
// A feature may add `drive: { usage, summary, run }` so `pnpm mole <key> <verb>` can drive it by hand.
export const FEATURES: Record<string, Feature> = {
  // Placeholder: replace it with real features, or keep it as a smoke check.
  example: {
    prove: proveExample,
    surfaces: [{{SURFACES_LIST}}],
    touches: ["src/"], // TODO(proof): the path prefixes of this feature's files
  },
};
