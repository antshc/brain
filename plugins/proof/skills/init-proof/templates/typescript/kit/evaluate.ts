import { isDeepStrictEqual } from "node:util";
import { contractDigest, openEvidence } from "./evidence";
import { JunitAdapter, TrxAdapter, JsonAdapter, tests, validateTestMetadata, type TestResultAdapter, type TestRunMetadata } from "./test-results";
import type { EvidenceContract, EvidencePolicy } from "./evidence-types";
import type { Check, Receipt } from "./types";

export type EvaluateOptions = {
  root: string; runDir: string; app: string; contracts: readonly EvidenceContract[];
  policy: EvidencePolicy; features?: readonly string[]; jsonAdapter?: TestResultAdapter;
};
/** Reads saved files only. Contracts, adapters and authorize are trusted project code, not sandboxed scripts. */
export async function evaluateEvidence(options: EvaluateOptions): Promise<Receipt> {
  const { policy, contracts } = options;
  const receipt: Receipt = { verdict: "ERROR", revision: policy.revision || null, app: options.app,
    at: new Date().toISOString(), checks: [], pageErrors: [], next: [] };
  const errors: string[] = [];
  const check = (name: string, actual: unknown, expected: unknown, hint?: string): Check =>
    ({ name, actual, expected, pass: isDeepStrictEqual(actual, expected), ...(hint ? { hint } : {}) });
  try {
    const names = options.features?.length ? [...options.features] : contracts.map(c => c.feature);
    if (!names.length || new Set(names).size !== names.length || new Set(contracts.map(c => c.feature)).size !== contracts.length ||
      names.some(n => !contracts.some(c => c.feature === n))) throw new Error("Missing/duplicate/unknown evidence features");
    const selected = names.map(name => contracts.find(c => c.feature === name)!);
    receipt.features = names;
    // Receipt surfaces apply to every selected feature; mixed coverage cannot claim a union.
    receipt.surfaces = ["web", "api"].filter(s => selected.every(c => c.surfaces.includes(s as "web" | "api"))) as Receipt["surfaces"];
    const allIds = new Set<string>();
    for (const contract of selected) {
      if (!contract.required.length || !contract.surfaces.length || contract.surfaces.some(s => s !== "web" && s !== "api")) throw new Error("Invalid evidence contract");
      for (const name of [...contract.required, ...contract.optional ?? []]) {
        if (!name || name.startsWith("tests/") || allIds.has(name)) throw new Error(`Duplicate/reserved check: ${name}`);
        allIds.add(name);
      }
      if (!contract.resource || !["api", "db"].includes(contract.resource.kind) ||
        (contract.resource.kind === "db" && !contract.resource.noReadApiReason?.trim())) throw new Error("Persisted GET or approved DB resource required");
    }
    const { manifest, reader, used } = await openEvidence(options.root, options.runDir, policy);
    for (const contract of selected) {
      const seen = new Set<string>();
      const allowed = new Set([...contract.required, ...contract.optional ?? []]);
      try {
        if (manifest.artifacts[contract.resource.path]?.kind !== contract.resource.kind) throw new Error("Persisted resource evidence missing/wrong source");
        // Requiring consumption prevents a supporting screenshot/task alone from passing.
        used.delete(contract.resource.path);
        await contract.verify({ evidence: reader, check(name, actual, expected, hint) {
          if (!allowed.has(name) || seen.has(name)) {
            const error = `Unknown/duplicate check: ${name}`;
            errors.push(error); // A contract cannot catch the error and turn it into PASS.
            throw new Error(error);
          }
          seen.add(name);
          receipt.checks.push(check(name, actual, expected, hint));
        } });
        if (!used.has(contract.resource.path)) throw new Error("Persisted resource was not evaluated");
      } catch (error) { errors.push(`${contract.feature}: ${String(error)}`); }
      for (const name of contract.required) if (!seen.has(name)) errors.push(`Required check not executed: ${name}`);
    }
    try {
      const spec = policy.tests;
      if (!spec.requiredIds.length && !spec.requiredSuites.length) throw new Error("Approve required test IDs or suites before implementation");
      const report = await reader.text(spec.report);
      validateTestMetadata(await reader.json<TestRunMetadata>(spec.metadata), manifest, report, spec);
      const adapter = spec.format === "junit" ? new JunitAdapter() : spec.format === "trx" ? new TrxAdapter() : spec.format === "json" ? options.jsonAdapter ?? new JsonAdapter() : null;
      if (!adapter) throw new Error("Unknown test report format");
      const result = adapter.parse(report, spec.report);
      // Adapters must also return a complete, nonempty normalized result.
      const normalized = new JsonAdapter().parse(JSON.stringify({ ...result, complete: true }), spec.report);
      if (!tests.requiredPresent(normalized, spec.requiredIds, spec.requiredSuites) || normalized.passed + normalized.failed === 0) throw new Error("Required tests missing or no tests executed");
      receipt.checks.push(check("tests/allPassed", tests.allPassed(normalized), true, spec.report));
      receipt.checks.push(check("tests/noUnexpectedSkips", tests.noUnexpectedSkips(normalized, spec.allowedSkips), true, spec.report));
    } catch (error) { errors.push(String(error)); }
    if (await contractDigest(options.root, policy.modules) !== policy.contractDigest) errors.push("Contract changed during evaluation");
    if (errors.length) throw new Error(errors.join("; "));
    receipt.verdict = receipt.checks.every(c => c.pass) ? "PASS" : "FAIL";
    receipt.next = receipt.verdict === "FAIL" ? receipt.checks.filter(c => !c.pass).map(c => `${c.name}: ${c.hint ?? "Inspect saved evidence; fix the feature and collect a fresh run"}`) : [];
  } catch (error) {
    receipt.error = String(error);
    receipt.next = ["Restore approved contracts and collect complete authorized evidence for the final revision. Keep this failed run."];
  }
  return receipt;
}
