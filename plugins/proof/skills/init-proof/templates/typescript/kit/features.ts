import { selectSurfaces } from "./surfaces";
import type { Feature, Prove, Surface } from "./types";

/** Features by name. The caller owns the map; the kit only reads it. */
export type Features = Record<string, Feature>;

export const featureNames = (features: Features) => Object.keys(features);

// No names means every feature. An unknown name is the caller's mistake, so say what exists.
export function selectFeatures(features: Features, names: string[] = []): string[] {
  const unknown = names.filter(name => !(name in features));
  if (unknown.length) throw new Error(`Unknown feature "${unknown.join('", "')}". Features: ${featureNames(features).join(", ")}`);
  return names.length ? [...new Set(names)] : featureNames(features);
}

// The surfaces to run for these features. No names means every supported surface all of them share; a name a feature lacks is refused.
export function surfacesFor(features: Features, selected: string[], supported: readonly Surface[], names: string[] = []): Surface[] {
  const shared = supported.filter(surface => selected.every(name => features[name].surfaces.includes(surface)));
  return selectSurfaces(names, shared);
}

// Each feature runs on the surfaces the run asked for that it has.
export function proveFeatures(features: Features, names: string[] = []): Prove {
  const selected = selectFeatures(features, names);
  return async kit => {
    for (const name of selected) {
      const surfaces = kit.surfaces.filter(surface => features[name].surfaces.includes(surface));
      await features[name].prove({ ...kit, surfaces });
    }
  };
}

// The features a set of changed files belongs to.
export function featuresFor(features: Features, files: string[]): string[] {
  return featureNames(features).filter(name => features[name].touches.some(prefix => files.some(file => file.startsWith(prefix))));
}
