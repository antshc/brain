import type { EvidenceAdapter } from "./evidence";
import type { Feature, Flow, Finding, ProofCheck, ProofContext, Scenario, Step, SubFeature, Surface } from "./types";

const ID = /^[a-z][a-z0-9-]*$/;
const own = (what: string, id: string) => {
  if (!ID.test(id)) throw new Error(`${what} id "${id}" must be lowercase words joined by hyphens`);
  return id;
};

/** A flow: `id` is what `flow <id>` runs and what the receipt's trace names. */
export const defineFlow = (id: string, run: Flow["run"]): Flow => ({ id, run });

/** A proof check. `evidence` names the sources it captures through `ctx.observe`, in the words of its map clause ("api-response"). */
export const defineProof = (id: string, evidence: string[], run: (ctx: ProofContext) => Promise<Finding>): ProofCheck => ({ id, evidence, run });

export type ScenarioBuilder = {
  /** A user action. */
  flow(flow: Flow): ScenarioBuilder;
  /** The next proof clause of the map, in order. */
  proof(check: ProofCheck): ScenarioBuilder;
  /** A supplementary check the map does not list. It also needs evidence and can fail the scenario. */
  guard(check: ProofCheck): ScenarioBuilder;
};
export type SubFeatureBuilder = { scenario(id: string, build: (scenario: ScenarioBuilder) => unknown): void };
export type FeatureBuilder = {
  /** Repo-relative path prefixes whose changes this feature must be re-proved for. */
  touches(...prefixes: string[]): void;
  /** The surfaces the feature uses. Default: every surface the repo supports. */
  surfaces(...surfaces: Surface[]): void;
  subFeature(id: string, build: (sub: SubFeatureBuilder) => unknown): void;
};

/** Builds a feature: sub-features own named scenarios, a scenario composes flows and attaches proof checks where they belong. */
export function defineFeature(name: string, build: (feature: FeatureBuilder) => unknown): Feature {
  const feature: Feature = { name: own("Feature", name), touches: [], surfaces: null, subFeatures: [] };
  build({
    touches: (...prefixes) => { feature.touches.push(...prefixes); },
    surfaces: (...surfaces) => { feature.surfaces = [...surfaces]; },
    subFeature(id, buildSub) {
      const sub: SubFeature = { id: own("Sub-feature", id), scenarios: [] };
      feature.subFeatures.push(sub);
      buildSub({
        scenario(scenarioId, buildScenario) {
          const scenario: Scenario = { id: own("Scenario", scenarioId), steps: [] };
          sub.scenarios.push(scenario);
          const builder: ScenarioBuilder = {
            flow: flow => { scenario.steps.push({ kind: "flow", flow }); return builder; },
            proof: check => { scenario.steps.push({ kind: "proof", check }); return builder; },
            guard: check => { scenario.steps.push({ kind: "guard", check }); return builder; },
          };
          buildScenario(builder);
        },
      });
    },
  });
  return feature;
}

export type ScenarioRef = { id: string; feature: Feature; subFeature: SubFeature; scenario: Scenario };
export type Registry = { features: Feature[]; scenarios: ScenarioRef[]; flows: Map<string, Flow> };

export class RegistryError extends Error {
  constructor(readonly problems: string[]) { super(`Invalid feature registry:\n- ${problems.join("\n- ")}`); }
}

export const scenarioId = (feature: string, sub: string, scenario: string) => `${feature}.${sub}.${scenario}`;

const dupes = (ids: string[]) => ids.filter((id, i) => ids.indexOf(id) !== i);

/** Validates the builders and indexes them by stable `feature.sub-feature.scenario` ids. */
export function buildRegistry(features: readonly Feature[], adapters: readonly EvidenceAdapter[]): Registry {
  const problems: string[] = [];
  const assertive = new Map(adapters.map(adapter => [adapter.source, adapter.assertive]));
  const flows = new Map<string, Flow>();
  const scenarios: ScenarioRef[] = [];
  for (const name of dupes(features.map(feature => feature.name))) problems.push(`Duplicate feature "${name}".`);
  for (const feature of features) {
    for (const id of dupes(feature.subFeatures.map(sub => sub.id))) problems.push(`${feature.name}: duplicate sub-feature "${id}".`);
    if (!feature.touches.length) problems.push(`${feature.name}: touches nothing, so \`features --changed\` can never select it.`);
    for (const subFeature of feature.subFeatures) {
      for (const id of dupes(subFeature.scenarios.map(scenario => scenario.id))) problems.push(`${feature.name}.${subFeature.id}: duplicate scenario "${id}".`);
      for (const scenario of subFeature.scenarios) {
        const id = scenarioId(feature.name, subFeature.id, scenario.id);
        scenarios.push({ id, feature, subFeature, scenario });
        if (!scenario.steps.some(step => step.kind === "proof")) problems.push(`${id}: has no proof check.`);
        const checks = scenario.steps.flatMap(step => (step.kind === "flow" ? [] : [step.check]));
        for (const check of dupes(checks.map(c => c.id))) problems.push(`${id}: duplicate check "${check}".`);
        for (const step of scenario.steps as Step[]) {
          if (step.kind === "flow") {
            const known = flows.get(step.flow.id);
            if (known && known !== step.flow) problems.push(`${id}: two different flows share the id "${step.flow.id}".`);
            flows.set(step.flow.id, known ?? step.flow);
            continue;
          }
          const { check } = step;
          if (!check.evidence.length) problems.push(`${id}: check "${check.id}" declares no evidence.`);
          for (const source of check.evidence) if (!assertive.has(source)) problems.push(`${id}: check "${check.id}" names the evidence source "${source}", which no adapter provides.`);
          if (check.evidence.length && !check.evidence.some(source => assertive.get(source))) {
            problems.push(`${id}: check "${check.id}" is backed by ${check.evidence.join(", ")} only; a screenshot cannot prove a requirement without an assertive source beside it.`);
          }
        }
      }
    }
  }
  if (problems.length) throw new RegistryError(problems);
  return { features: [...features], scenarios, flows };
}

export const featureNames = (registry: Registry) => registry.features.map(feature => feature.name);

// No targets means every scenario. A target is a feature, `feature.sub-feature` or `feature.sub-feature.scenario`; an unknown one is the caller's mistake, so say what exists.
export function selectScenarios(registry: Registry, targets: string[] = []): ScenarioRef[] {
  if (!targets.length) return registry.scenarios;
  const unknown = targets.filter(target => !registry.scenarios.some(ref => ref.id === target || ref.id.startsWith(`${target}.`)));
  if (unknown.length) throw new Error(`Unknown target "${unknown.join('", "')}". Scenarios: ${registry.scenarios.map(ref => ref.id).join(", ")}`);
  return registry.scenarios.filter(ref => targets.some(target => ref.id === target || ref.id.startsWith(`${target}.`)));
}

// The features a set of changed files belongs to.
export function featuresFor(registry: Registry, files: string[]): string[] {
  return registry.features.filter(feature => feature.touches.some(prefix => files.some(file => file.startsWith(prefix)))).map(feature => feature.name);
}

/** The surfaces a set of scenarios uses, out of the ones the repo supports. */
export function surfacesFor(refs: ScenarioRef[], supported: readonly Surface[]): Surface[] {
  const used = new Set(refs.flatMap(ref => ref.feature.surfaces ?? supported));
  return supported.filter(surface => used.has(surface));
}
