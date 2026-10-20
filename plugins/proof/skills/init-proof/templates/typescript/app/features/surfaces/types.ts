import type { Surface } from "../../kit";

export { SurfaceError, type Surface } from "../../kit";

// What a feature does, said once. Each surface turns the same call into its own way of driving the app
// and returns the same shape, so a contract rule is written once and checked on every surface.
export type AppStatus = { surface: Surface; ok: boolean; status: number };

export interface SurfaceAdapter {
  readonly surface: Surface;
  app: {
    /** Does the app answer on this surface? */
    status(): Promise<AppStatus>;
  };
}
