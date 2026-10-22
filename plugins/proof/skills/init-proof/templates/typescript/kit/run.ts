import type { Browser } from "@playwright/test";
import { EvidenceError, Failure, type ArtifactStore, type BrowserEvent, type CheckResult, type EventLog, type EvidenceRef, type Flow, type ProofCheck, type ProofContext, type Receipt, type RunEnv, type ScenarioResult, type ScenarioVerdict, type StepResult, type Surface, type Visitor } from "./types";
import type { EvidenceAdapter } from "./evidence";
import type { ScenarioRef } from "./features";
import { aggregate, lacksEvidence, sealScenario } from "./receipt";

/** The caller supplies a revision of the code under proof, or it stays null. */
export type Revision = () => Promise<string | null>;

export type RunHost = {
  app: string;
  appUrl: string;
  apiUrl: string | null;
  /** The surfaces this run observes. */
  surfaces: Surface[];
  adapters: readonly EvidenceAdapter[];
  store: ArtifactStore;
  /** A fresh, isolated visitor for each scenario. */
  visitor(): Promise<Visitor>;
  revision?: Revision;
  /** The map paragraph and file hash a scenario answers to, kept in its receipt. */
  mapOf?(ref: ScenarioRef): { hash: string; text: string } | undefined;
  /** How to run the proof again, quoted in a FAIL receipt. */
  rerun?: string;
  /** What to do when the verdict is "can't tell". */
  diagnose?: string;
};

const first = (error: unknown) => (error instanceof Error ? error.message.split("\n")[0] : String(error));

/**
 * A fresh visitor: its own context with no storage and no cookies, collectors listening before the first action,
 * and the app loaded when the run has a web surface.
 */
export async function openVisitor(browser: Browser, appUrl: string, surfaces: Surface[], timeoutMs = 5000): Promise<Visitor> {
  const context = await browser.newContext({ ignoreHTTPSErrors: true });
  const events: EventLog = { step: -1, entries: [] };
  const push = (event: Omit<BrowserEvent, "step" | "at">) => events.entries.push({ step: events.step, at: new Date().toISOString(), ...event });
  try {
    const page = await context.newPage();
    page.setDefaultTimeout(timeoutMs);
    page.on("pageerror", error => push({ type: "pageerror", level: "error", text: error.message }));
    page.on("console", message => push({ type: "console", level: message.type(), text: message.text() }));
    page.on("response", response => push({ type: "response", method: response.request().method(), status: response.status(), url: response.url() }));
    page.on("requestfailed", request => push({ type: "requestfailed", method: request.method(), url: request.url(), text: request.failure()?.errorText }));
    if (surfaces.includes("web")) await page.goto(appUrl, { waitUntil: "load", timeout: timeoutMs });
    return { page, events, close: () => context.close() };
  } catch (error) {
    await context.close().catch(() => {});
    throw error;
  }
}

async function runCheck(kind: "proof" | "guard", check: ProofCheck, step: number, env: RunEnv, host: RunHost, ref: ScenarioRef): Promise<CheckResult> {
  const evidence: EvidenceRef[] = [];
  const base = { id: check.id, step, kind, required: [...check.evidence], at: new Date().toISOString() };
  const ctx: ProofContext = {
    page: env.page, appUrl: env.appUrl, apiUrl: env.apiUrl, surfaces: env.surfaces, vars: env.vars,
    async observe<T>(source: string, query?: unknown): Promise<T> {
      // Evidence is attributed to the check that captured it, so a check cannot borrow another's observation.
      if (!check.evidence.includes(source)) throw new EvidenceError(`${check.id} captured "${source}" evidence it did not declare (it declares ${check.evidence.join(", ")}).`);
      const adapter = host.adapters.find(candidate => candidate.source === source);
      if (!adapter) throw new EvidenceError(`No evidence adapter provides "${source}". Add one to proof/adapters/.`);
      const unavailable = adapter.unavailable(env);
      if (unavailable) throw new EvidenceError(`The "${source}" evidence is unavailable: ${unavailable}.`);
      const { result, artifact } = await adapter.capture(env, query);
      const data = artifact instanceof Uint8Array ? artifact : JSON.stringify({ source, check: check.id, capturedAt: new Date().toISOString(), observed: artifact }, null, 2);
      const path = await host.store.save({ scenario: ref.id, check: check.id, source, ext: adapter.ext, data });
      evidence.push({ source, artifact: path, at: new Date().toISOString(), step });
      return result as T;
    },
  };
  try {
    const finding = await check.run(ctx);
    const result = { ...base, evidence, expected: finding.expected, actual: finding.actual, ...(finding.pass !== true && finding.hint ? { hint: finding.hint } : {}) };
    const missing = lacksEvidence({ required: check.evidence, evidence });
    if (missing.length) {
      return { ...result, verdict: "ERROR", error: `${check.id} returned a verdict without evidence from ${missing.join(", ")}. A check proves itself by observing each source it declares.` };
    }
    return { ...result, verdict: finding.pass === true ? "PASS" : "FAIL" };
  } catch (error) {
    const message = first(error);
    // A diagnostic is not required evidence: it records why the observation failed.
    try {
      const path = await host.store.save({ scenario: ref.id, check: check.id, source: "diagnostic", ext: "txt", data: message });
      evidence.push({ source: "diagnostic", artifact: path, at: new Date().toISOString(), step });
    } catch { /* the error itself is still on the receipt */ }
    return { ...base, evidence, verdict: "ERROR", error: message };
  }
}

const pageErrorsOf = (events: EventLog) => [...new Set(events.entries.filter(event => event.type === "pageerror" || (event.type === "console" && event.level === "error")).map(event => event.text ?? ""))];

/** Runs one scenario's flows and proof checks, in order, in one fresh visitor. The first step that is not PASS stops it; the rest are NOT_REACHED. */
export async function runScenario(ref: ScenarioRef, host: RunHost): Promise<ScenarioResult> {
  const revision = host.revision ?? (async () => null);
  const result: ScenarioResult = {
    id: ref.id, feature: ref.feature.name, subFeature: ref.subFeature.id, scenario: ref.scenario.id, verdict: "ERROR",
    revision: { start: null, end: null }, steps: [], checks: [], pageErrors: [], ...(host.mapOf?.(ref) ? { map: host.mapOf(ref) } : {}),
  };
  let visitor: Visitor | undefined;
  try {
    result.revision.start = await revision();
    visitor = await host.visitor();
    const env: RunEnv = { page: visitor.page, appUrl: host.appUrl, apiUrl: host.apiUrl, surfaces: host.surfaces, events: visitor.events, vars: {} };
    let stopped = false;
    for (const [index, step] of ref.scenario.steps.entries()) {
      const id = step.kind === "flow" ? step.flow.id : step.check.id;
      if (stopped) {
        result.steps.push({ index, kind: step.kind, id, verdict: "NOT_REACHED", ms: 0 });
        if (step.kind !== "flow") result.checks.push({ id, step: index, kind: step.kind, verdict: "NOT_REACHED", required: [...step.check.evidence], evidence: [], at: new Date().toISOString() });
        continue;
      }
      visitor.events.step = index;
      const started = Date.now();
      let record: StepResult;
      if (step.kind === "flow") {
        record = { index, kind: "flow", id, verdict: "PASS", ms: 0 };
        try { Object.assign(env.vars, await (step.flow as Flow).run(env) ?? {}); } catch (error) {
          record.verdict = error instanceof Failure ? "FAIL" : "ERROR";
          record.error = first(error);
        }
      } else {
        const check = await runCheck(step.kind, step.check, index, env, host, ref);
        result.checks.push(check);
        record = { index, kind: step.kind, id, verdict: check.verdict, ms: 0, ...(check.error ? { error: check.error } : {}) };
      }
      record.ms = Date.now() - started;
      result.steps.push(record);
      if (record.verdict !== "PASS") stopped = true;
    }
    result.pageErrors = pageErrorsOf(visitor.events);
    const worst = result.steps.find(step => step.verdict === "ERROR") ?? result.steps.find(step => step.verdict === "FAIL");
    result.verdict = worst ? worst.verdict as ScenarioVerdict : "PASS";
    if (worst?.error) result.error = worst.error;
  } catch (error) {
    result.verdict = "ERROR";
    result.error = `Couldn't run the scenario: ${first(error)}`;
  } finally {
    await visitor?.close().catch(() => {});
  }
  try { result.revision.end = await revision(); } catch (error) { result.error ??= first(error); }
  if (result.revision.end !== result.revision.start) {
    result.verdict = "STALE";
    result.error = `The source changed while proving (started on ${result.revision.start}, now ${result.revision.end}). Evidence from two builds proves neither.`;
  }
  return sealScenario(result);
}

/** Runs the scenarios one after another, each in its own fresh visitor, and returns the receipt. */
export async function runScenarios(refs: ScenarioRef[], host: RunHost, targets: string[] = []): Promise<Receipt> {
  const revision = host.revision ?? (async () => null);
  const receipt: Receipt = {
    verdict: "ERROR", revision: await revision().catch(() => null), app: host.app, at: new Date().toISOString(), targets,
    features: [...new Set(refs.map(ref => ref.feature.name))], surfaces: host.surfaces, scenarios: [], next: [],
  };
  for (const ref of refs) receipt.scenarios.push(await runScenario(ref, host));
  receipt.verdict = aggregate(receipt.scenarios);
  if (!receipt.scenarios.length) receipt.error = "No scenario ran.";
  const rerun = host.rerun ?? "Run the proof again";
  const diagnose = host.diagnose ?? "Check that the app is running and the build is fresh";
  if (receipt.verdict === "PASS") {
    receipt.next = ["These checks passed on this revision, each with its own evidence under the receipt's artifacts. They cover nothing else: read the evidence, screenshots included, for anything the checks missed."];
  } else if (receipt.verdict === "FAIL") {
    receipt.next = [...receipt.scenarios.flatMap(scenario => scenario.checks.filter(check => check.verdict === "FAIL").map(check =>
      check.hint ?? `Fix ${scenario.id} / "${check.id}": expected ${JSON.stringify(check.expected)}, got ${JSON.stringify(check.actual)}.`)),
      ...receipt.scenarios.filter(scenario => scenario.verdict === "FAIL" && !scenario.checks.some(check => check.verdict === "FAIL")).map(scenario => `Fix ${scenario.id}: ${scenario.error}`),
      `Then re-run: ${rerun}`];
  } else {
    receipt.next = [...receipt.scenarios.filter(scenario => scenario.verdict === "ERROR" || scenario.verdict === "STALE").map(scenario => `${scenario.id}: ${scenario.error ?? scenario.verdict}`),
      ...(receipt.error ? [receipt.error] : []), `Can't tell is not the same as broken. ${diagnose}, then prove again.`];
  }
  return receipt;
}
