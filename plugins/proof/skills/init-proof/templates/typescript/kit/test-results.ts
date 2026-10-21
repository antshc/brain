import { XMLParser, XMLValidator } from "fast-xml-parser";
import { sha256, time } from "./evidence";
import type { EvidenceManifest, TestPolicy } from "./evidence-types";
export type TestCase = { id: string; suite: string; status: "passed" | "failed" | "skipped"; failure?: string };
export type TestRunResult = { passed: number; failed: number; skipped: number; total: number; cases: TestCase[]; failures: string[]; source: string };
export interface TestResultAdapter { parse(input: string, source: string): TestRunResult }
const list = <T>(value: T | T[] | undefined): T[] => value === undefined ? [] : Array.isArray(value) ? value : [value];
export function normalizeTests(cases: TestCase[], source: string): TestRunResult {
  if (!cases.length || new Set(cases.map(c => c.id)).size !== cases.length || cases.some(c => !c || typeof c.id !== "string" || !c.id || typeof c.suite !== "string" || !c.suite || !["passed", "failed", "skipped"].includes(c.status))) throw new Error("Empty/duplicate/invalid test cases (resolve retries in a project adapter)");
  return { cases, source, total: cases.length, passed: cases.filter(c => c.status === "passed").length,
    failed: cases.filter(c => c.status === "failed").length, skipped: cases.filter(c => c.status === "skipped").length,
    failures: cases.filter(c => c.status === "failed").map(c => c.failure ?? c.id) };
}
// No entities, DTD, executable content or external resource resolution.
function xml(input: string): any {
  if (/<!DOCTYPE|<!ENTITY/i.test(input) || XMLValidator.validate(input) !== true) throw new Error("Malformed/unsafe XML report");
  return new XMLParser({ ignoreAttributes: false, attributeNamePrefix: "@", removeNSPrefix: true, parseTagValue: false, processEntities: false }).parse(input);
}
function totals(node: any, names: Record<string, number>) {
  for (const [key, value] of Object.entries(names)) {
    if (node[`@${key}`] !== undefined && (!/^\d+$/.test(String(node[`@${key}`])) || Number(node[`@${key}`]) !== value)) throw new Error(`Inconsistent test total: ${key}`);
  }
}
export class JunitAdapter implements TestResultAdapter {
  parse(input: string, source: string): TestRunResult {
    const doc = xml(input), cases: TestCase[] = [];
    const walk = (suite: any, parent = ""): TestCase[] => {
      const name = suite["@name"] || parent;
      const local: TestCase[] = list<any>(suite.testcase).map(c => {
        if (!c["@name"] || !name || ["flakyFailure", "rerunFailure", "rerunError", "flakyError"].some(k => k in c)) throw new Error("Unnamed/retried JUnit test");
        if ((c["@status"] !== undefined && !["run", "passed", "failed"].includes(c["@status"])) ||
          (c["@result"] !== undefined && c["@result"] !== "completed")) throw new Error("Unknown/incomplete JUnit status");
        const states = ["failure", "error", "skipped"].filter(k => k in c);
        if (states.some(k => Array.isArray(c[k]))) throw new Error("Retried/duplicate JUnit result");
        if (states.length > 1 || (c["@status"] === "failed" && !states.length) || (c["@status"] === "passed" && states.length)) throw new Error("Ambiguous JUnit status");
        return { id: `${name}::${c["@classname"] ?? ""}::${c["@name"]}`, suite: name,
          status: states[0] === "skipped" ? "skipped" : states.length ? "failed" : "passed",
          ...(states.length && states[0] !== "skipped" ? { failure: JSON.stringify(c[states[0]]) } : {}) };
      });
      const children = list<any>(suite.testsuite).flatMap(s => walk(s, name));
      const all = [...local, ...children];
      if (all.length) {
        const result = normalizeTests(all, source);
        totals(suite, { tests: result.total, failures: local.filter(c => c.status === "failed").length + children.filter(c => c.status === "failed").length - countErrors(suite), errors: countErrors(suite), skipped: result.skipped });
      } else if (Number(suite["@tests"] ?? 0) !== 0) throw new Error("JUnit suite omitted cases");
      return all;
    };
    const countErrors = (suite: any): number => list<any>(suite.testcase).filter(c => "error" in c).length + list<any>(suite.testsuite).reduce((n, s) => n + countErrors(s), 0);
    if (doc.testsuites) {
      cases.push(...list<any>(doc.testsuites.testsuite).flatMap(s => walk(s)));
      const result = normalizeTests(cases, source);
      totals(doc.testsuites, { tests: result.total, failures: cases.filter(c => c.status === "failed").length - list<any>(doc.testsuites.testsuite).reduce((n, s) => n + countErrors(s), 0), errors: list<any>(doc.testsuites.testsuite).reduce((n, s) => n + countErrors(s), 0), skipped: result.skipped });
      return result;
    }
    if (!doc.testsuite) throw new Error("Not a JUnit report");
    return normalizeTests(walk(doc.testsuite), source);
  }
}
export class TrxAdapter implements TestResultAdapter {
  parse(input: string, source: string): TestRunResult {
    const run = xml(input).TestRun;
    if (!run?.ResultSummary?.Counters || !run.Results) throw new Error("Incomplete TRX report");
    const definitions = new Map(list<any>(run.TestDefinitions?.UnitTest).map(t => [t["@id"], t]));
    const cases = list<any>(run.Results.UnitTestResult).map(c => {
      const definition = definitions.get(c["@testId"]);
      if (!definition?.TestMethod?.["@className"] || !c["@testId"]) throw new Error("TRX test definition missing");
      const outcome = c["@outcome"];
      if (!["Passed", "Failed", "NotExecuted"].includes(outcome)) throw new Error(`Incomplete/unknown TRX result: ${outcome}`);
      return { id: c["@testId"], suite: definition.TestMethod["@className"], status: outcome === "Passed" ? "passed" as const : outcome === "Failed" ? "failed" as const : "skipped" as const,
        ...(outcome === "Failed" ? { failure: JSON.stringify(c.Output?.ErrorInfo ?? c["@testName"]) } : {}) };
    });
    const result = normalizeTests(cases, source);
    for (const [key, value] of Object.entries(run.ResultSummary.Counters)) {
      if (!["@total", "@executed", "@passed", "@failed", "@notExecuted"].includes(key) && Number(value) !== 0) throw new Error("Incomplete/unknown TRX counter");
    }
    totals(run.ResultSummary.Counters, { total: result.total, executed: result.passed + result.failed, passed: result.passed, failed: result.failed, notExecuted: result.skipped });
    if (result.failed === 0 && run.ResultSummary["@outcome"] !== "Completed" && run.ResultSummary["@outcome"] !== "Passed") throw new Error("Incomplete TRX run");
    return result;
  }
}
/** Explicit normalized schema only. Playwright JSON needs a project adapter to handle retries/projects. */
export class JsonAdapter implements TestResultAdapter {
  parse(input: string, source: string): TestRunResult {
    const data = JSON.parse(input);
    if (data.complete !== true || !Array.isArray(data.cases)) throw new Error("Incomplete JSON test report");
    const result = normalizeTests(data.cases, source);
    for (const key of ["passed", "failed", "skipped", "total"] as const) if (data[key] !== result[key]) throw new Error(`Inconsistent JSON total: ${key}`);
    return result;
  }
}
export const tests = {
  allPassed: (r: TestRunResult) => r.failed === 0 && r.passed > 0,
  minimumExecuted: (r: TestRunResult, minimum: number) => {
    if (!Number.isSafeInteger(minimum) || minimum < 1) throw new Error("Invalid minimum test count");
    return r.passed + r.failed >= minimum;
  },
  requiredPresent: (r: TestRunResult, ids: readonly string[], suites: readonly string[] = []) => ids.every(id => r.cases.some(c => c.id === id)) && suites.every(s => r.cases.some(c => c.suite === s)),
  noUnexpectedSkips: (r: TestRunResult, allowed: readonly string[]) => r.cases.every(c => c.status !== "skipped" || allowed.includes(c.id)),
  matchesRevision: (tested: string, expected: string) => tested === expected,
};
export type TestRunMetadata = { runId: string; revision: string; build: string; command: string; startedAt: string; endedAt: string; reportHash: string; dirty: boolean; complete: boolean; provenance: unknown };
export function validateTestMetadata(meta: TestRunMetadata, manifest: EvidenceManifest, report: string, policy: TestPolicy): void {
  // The authorized manifest binds this metadata too, including trusted execution provenance.
  if (meta.runId !== manifest.runId || !tests.matchesRevision(meta.revision, manifest.revision) || meta.build !== manifest.build ||
    meta.dirty !== false || meta.complete !== true || !meta.command || !meta.provenance || meta.reportHash !== sha256(report) ||
    time(meta.startedAt) < time(manifest.startedAt) || time(meta.endedAt) < time(meta.startedAt) || time(meta.endedAt) > time(manifest.endedAt) ||
    time(meta.endedAt) > time(manifest.artifacts[policy.report]?.capturedAt) ||
    time(meta.endedAt) > time(manifest.artifacts[policy.metadata]?.capturedAt) ||
    manifest.artifacts[policy.report]?.kind !== "tests" || manifest.artifacts[policy.metadata]?.kind !== "metadata") throw new Error("Missing/stale/untrusted test execution metadata");
}
