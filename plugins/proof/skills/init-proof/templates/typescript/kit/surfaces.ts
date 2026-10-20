import type { ProofKit, Surface } from "./types";

export const ALL_SURFACES: readonly Surface[] = ["web", "api"];

export class SurfaceError extends Error {
  constructor(readonly surface: Surface, message: string, readonly next: string) { super(`${surface}: ${message}`); }
}

export const isSurface = (value: string): value is Surface => (ALL_SURFACES as readonly string[]).includes(value);

// No names means every available surface. An unknown name is the caller's mistake, so say what exists.
export function selectSurfaces(names: string[], available: readonly Surface[]): Surface[] {
  const unknown = names.filter(name => !isSurface(name));
  if (unknown.length) throw new Error(`Unknown surface "${unknown.join('", "')}". Surfaces: ${ALL_SURFACES.join(", ")}`);
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
      known ? error.next : kit.diagnose);
    return null;
  }
}
