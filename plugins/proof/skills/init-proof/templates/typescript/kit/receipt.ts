import { featureNames, type Features } from "./features";
import { ALL_SURFACES } from "./surfaces";
import type { Receipt, Surface } from "./types";

/** Exit code for a receipt: 0 PASS, 1 FAIL, 2 can't tell. */
export const exitCode = (receipt: Pick<Receipt, "verdict">) => receipt.verdict === "PASS" ? 0 : receipt.verdict === "FAIL" ? 1 : 2;

/** A receipt describes the revision it ran on; once the source moves on, it describes code that no longer exists. */
export const isStale = (receipt: Pick<Receipt, "revision">, revision: string | null) => receipt.revision !== revision;

/** What a run left unproved: a feature subset, and surfaces the proved features have but the run skipped. */
export function coverage(features: Features, run: { features: string[]; surfaces: Surface[] }) {
  return {
    partialFeatures: run.features.length < featureNames(features).length,
    skippedSurfaces: ALL_SURFACES.filter(surface =>
      !run.surfaces.includes(surface) && run.features.some(name => features[name]?.surfaces.includes(surface))),
  };
}
