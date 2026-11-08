import type { Page } from "@playwright/test";
import type { DomQuery } from "./evidence";

// A surface is one way a feature reaches a user: `web` is the app in a real Chrome, `api` is HTTP.
export type Surface = "web" | "api";

/** PASS and FAIL are verdicts on the app; ERROR means the proof could not be made ("can't tell"). */
export type Verdict = "PASS" | "FAIL" | "ERROR";
/** NOT_REACHED: an earlier step stopped the scenario. */
export type StepVerdict = Verdict | "NOT_REACHED";
/** STALE: the source or the served build changed while the scenario ran, so its evidence belongs to two builds. */
export type ScenarioVerdict = Verdict | "STALE";

/** One thing the browser reported, tagged with the step that was running: step-scoped observations. */
export type BrowserEvent = {
  step: number;
  at: string;
  type: "console" | "pageerror" | "response" | "requestfailed";
  level?: string;
  method?: string;
  status?: number;
  url?: string;
  text?: string;
};
export type EventLog = { step: number; entries: BrowserEvent[] };

/** What a flow, a proof check and an evidence adapter can see of the run. */
export type RunEnv = {
  /** A fresh visitor (no storage) with the app already loaded when the repo has a web surface. */
  page: Page;
  appUrl: string;
  /** Where the API answers, or null when the run has no API. */
  apiUrl: string | null;
  surfaces: Surface[];
  /** Collectors start with the visitor, before any flow acts. */
  events: EventLog;
  /** Scenario variables (a selected product id) that flows hand to later flows and checks. */
  vars: Record<string, unknown>;
};

export type FlowContext = RunEnv;

/** A user action. It acts and returns variables to remember; it never decides acceptance. Throw `Failure` when a precondition of the user's path is violated. */
export type Flow = {
  id: string;
  run(ctx: FlowContext): Promise<Record<string, unknown> | void>;
};

export type ProofContext = Pick<RunEnv, "page" | "appUrl" | "apiUrl" | "surfaces"> & {
  vars: Readonly<Record<string, unknown>>;
  /** Capture evidence from a declared source, persist it for this check and return what was observed. */
  observe<T = unknown>(source: "dom-assertion", query: DomQuery): Promise<T>;
  observe<T = unknown>(source: string, query?: unknown): Promise<T>;
};

export type Finding = { pass: boolean; expected: unknown; actual: unknown; hint?: string };

/** An acceptance assertion. It observes; it never navigates or changes the app. */
export type ProofCheck = {
  id: string;
  /** The evidence sources it proves itself with. Each must be captured through `observe`. */
  evidence: string[];
  run(ctx: ProofContext): Promise<Finding>;
};

export type Step =
  | { kind: "flow"; flow: Flow }
  /** A proof clause of the feature map. */
  | { kind: "proof"; check: ProofCheck }
  /** A supplementary check (for example no unexpected browser errors) that the map does not list. */
  | { kind: "guard"; check: ProofCheck };

export type Scenario = { id: string; steps: Step[] };
export type SubFeature = { id: string; scenarios: Scenario[] };
/** A named proof: its sub-features and scenarios, which files it must be re-proved for, and which surfaces it uses. */
export type Feature = {
  name: string;
  /** Repo-relative path prefixes whose changes this feature must be re-proved for. */
  touches: string[];
  /** The surfaces the feature uses. Null means every surface the repo supports. */
  surfaces: Surface[] | null;
  subFeatures: SubFeature[];
};

export type EvidenceRef = { source: string; /** Relative to the run's artifact root. */ artifact: string; at: string; step: number };
export type CheckResult = {
  id: string;
  step: number;
  kind: "proof" | "guard";
  verdict: StepVerdict;
  /** Sources the check declared; a PASS needs an artifact for each. */
  required: string[];
  evidence: EvidenceRef[];
  expected?: unknown;
  actual?: unknown;
  hint?: string;
  error?: string;
  at: string;
};
export type StepResult = { index: number; kind: Step["kind"]; id: string; verdict: StepVerdict; ms: number; error?: string };
export type ScenarioResult = {
  /** `feature.sub-feature.scenario` */
  id: string;
  feature: string;
  subFeature: string;
  scenario: string;
  verdict: ScenarioVerdict;
  revision: { start: string | null; end: string | null };
  /** The feature-map paragraph and the hash of its file, as they were when the scenario ran. */
  map?: { hash: string; text: string };
  steps: StepResult[];
  checks: CheckResult[];
  pageErrors: string[];
  error?: string;
};

export type Receipt = {
  verdict: Verdict;
  revision: string | null;
  app: string;
  at: string;
  /** What was asked for: feature, feature.sub-feature or feature.sub-feature.scenario ids; empty means everything. */
  targets: string[];
  /** The features this run covered. A subset is not a full proof. */
  features: string[];
  surfaces: Surface[];
  scenarios: ScenarioResult[];
  error?: string;
  next: string[];
};

/** Where evidence artifacts live. Returns the artifact's path relative to the artifact root. */
export interface ArtifactStore {
  save(artifact: { scenario: string; check: string; source: string; ext: string; data: string | Uint8Array }): Promise<string>;
}

/** What the checks and flows run against: a fresh visitor with its collectors already listening. */
export type Visitor = { page: Page; events: EventLog; close(): Promise<void> };

/** A flow that finds the user's path violated, as opposed to a crash: the scenario FAILS instead of ERRORs. */
export class Failure extends Error {}

/** A required piece of evidence could not be captured, or was captured the wrong way: the check can only ERROR. */
export class EvidenceError extends Error {}
