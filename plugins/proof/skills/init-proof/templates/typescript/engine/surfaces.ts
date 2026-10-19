import { APP } from "../app";
import type { ProofKit } from "./proof";

// A surface is one way a feature reaches a user: `web` is the app in a real Chrome, `api` is HTTP.
export type Surface = "web" | "api";
export const ALL_SURFACES: readonly Surface[] = ["web", "api"];
/** The surfaces this repo supports. proof/app.ts says which. */
export const SURFACES: readonly Surface[] = APP.surfaces;

export class SurfaceError extends Error {
  constructor(readonly surface: Surface, message: string, readonly next: string) { super(`${surface}: ${message}`); }
}

export const isSurface = (value: string): value is Surface => (ALL_SURFACES as readonly string[]).includes(value);

// No names means every available surface. An unknown name is the caller's mistake, so say what exists.
export function selectSurfaces(names: string[] = [], available: readonly Surface[] = SURFACES): Surface[] {
  const unknown = names.filter(name => !isSurface(name));
  if (unknown.length) throw new Error(`Unknown surface "${unknown.join('", "')}". Surfaces: ${SURFACES.join(", ")}`);
  const chosen = names as Surface[];
  const missing = chosen.filter(name => !available.includes(name));
  if (missing.length) throw new Error(`This feature has no "${missing.join('", "')}" surface. It has: ${available.join(", ")}`);
  return chosen.length ? [...new Set(chosen)] : [...available];
}

// A surface that cannot be observed is a finding, not a crash: a throw would turn the whole run into "can't tell".
export async function observe<T>(kit: ProofKit, label: string, step: () => Promise<T>): Promise<T | null> {
  try { return await step(); } catch (error) {
    const known = error instanceof SurfaceError;
    kit.check(`${label}: observed`, error instanceof Error ? error.message.split("\n")[0] : String(error), "an observation",
      known ? error.next : "Is the app up and the build fresh? pnpm mole doctor");
    return null;
  }
}
