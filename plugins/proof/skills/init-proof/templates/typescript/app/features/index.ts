import type { Feature } from "../kit";
import { example } from "./example";

// Each feature has a map at .github/skills/verify-mole/features/<name>.md. `pnpm test:proof` keeps the two in step.
export const FEATURES: Feature[] = [example];
