import type { Feature } from "../kit";
import { example } from "./example";

// Each feature has a map at {{SKILL_DIR}}/features/<name>.md. `pnpm test:proof` keeps the two in step.
export const FEATURES: Feature[] = [example];
