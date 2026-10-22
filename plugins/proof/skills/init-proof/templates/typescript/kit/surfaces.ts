import type { Surface } from "./types";

export const ALL_SURFACES: readonly Surface[] = ["web", "api"];

/** A surface that cannot be observed. `next` says what to do about it. */
export class SurfaceError extends Error {
  constructor(readonly surface: Surface, message: string, readonly next: string) { super(`${surface}: ${message}`); }
}

export const isSurface = (value: string): value is Surface => (ALL_SURFACES as readonly string[]).includes(value);
