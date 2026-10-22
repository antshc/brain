import type { Registry } from "./features";
import type { CheckResult, Receipt, ScenarioResult, ScenarioVerdict, Verdict } from "./types";

/** Exit code for a receipt: 0 PASS, 1 FAIL, 2 can't tell. */
export const exitCode = (receipt: Pick<Receipt, "verdict">) => receipt.verdict === "PASS" ? 0 : receipt.verdict === "FAIL" ? 1 : 2;

/** A receipt describes the revision it ran on; once the source moves on, it describes code that no longer exists. */
export const isStale = (receipt: Pick<Receipt, "revision">, revision: string | null) => receipt.revision !== revision;

/** What a run left unproved: a subset of the scenarios is not a full proof. */
export function coverage(registry: Registry, ran: string[]) {
  const missing = registry.scenarios.map(ref => ref.id).filter(id => !ran.includes(id));
  return { partial: missing.length > 0, missing };
}

/** A check proves itself only with its own artifact from each declared source. */
export const lacksEvidence = (check: Pick<CheckResult, "required" | "evidence">) =>
  check.required.filter(source => !check.evidence.some(ref => ref.source === source));

/** Never let a PASS stand on missing evidence or a non-PASS step, whatever produced it. */
export function sealScenario(result: ScenarioResult): ScenarioResult {
  if (result.verdict !== "PASS") return result;
  const bad = result.checks.find(check => check.verdict !== "PASS" || lacksEvidence(check).length);
  const stopped = result.steps.find(step => step.verdict !== "PASS");
  if (!bad && !stopped && result.checks.some(check => check.kind === "proof")) return result;
  const why = bad
    ? `${bad.id} cannot pass: ${lacksEvidence(bad).length ? `no evidence from ${lacksEvidence(bad).join(", ")}` : `it is ${bad.verdict}`}.`
    : stopped ? `${stopped.id} is ${stopped.verdict}.` : "no proof check ran.";
  return { ...result, verdict: "ERROR", error: `PASS rejected: ${why}` };
}

const rank: Record<ScenarioVerdict, number> = { PASS: 0, ERROR: 1, STALE: 1, FAIL: 2 };

/** FAIL when any scenario's evidence shows the app wrong, ERROR when any could not be proved, PASS only when every one passed. */
export function aggregate(scenarios: ScenarioResult[]): Verdict {
  if (!scenarios.length) return "ERROR";
  const worst = scenarios.reduce((top, scenario) => (rank[scenario.verdict] > rank[top] ? scenario.verdict : top), "PASS" as ScenarioVerdict);
  return worst === "PASS" ? "PASS" : worst === "FAIL" ? "FAIL" : "ERROR";
}
