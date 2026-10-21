import { randomUUID } from "node:crypto";
import { parseArgs } from "node:util";
import { join, resolve } from "node:path";
import { mkdir, writeFile } from "node:fs/promises";
import { evaluateEvidence } from "../proof/kit/evaluate";
import { exitCode } from "../proof/kit/receipt";
import type { Receipt } from "../proof/kit/types";

export async function main() {
  let runDir: string | undefined;
  let receipt: Receipt;
  try {
    const { values } = parseArgs({ options: { evidence: { type: "string" }, feature: { type: "string", multiple: true } } });
    if (!values.evidence) throw new Error("--evidence requires a saved run directory");
    runDir = resolve(values.evidence);
    const { EVIDENCE_APP, EVIDENCE_POLICY, EVIDENCE_JSON_ADAPTER } = await import("../proof/evidence-config");
    const { CONTRACTS } = await import("../proof/contracts");
    receipt = await evaluateEvidence({ root: process.cwd(), runDir, app: EVIDENCE_APP,
      policy: EVIDENCE_POLICY, contracts: CONTRACTS, features: values.feature, jsonAdapter: EVIDENCE_JSON_ADAPTER });
  } catch (error) {
    receipt = { verdict: "ERROR", revision: null, app: "proof", at: new Date().toISOString(), checks: [], pageErrors: [],
      error: String(error), next: ["Configure approved proof/contracts and evidence-config, then collect a fresh authorized run."] };
  }
  const dir = join(process.cwd(), "proof", ".runs");
  await mkdir(join(dir, "receipts"), { recursive: true });
  const json = JSON.stringify(receipt, null, 2);
  // Exclusive writes preserve all attempts, including repeated evaluations of one run.
  const history = join(dir, "receipts", `${receipt.at.replace(/[:.]/g, "-")}-${randomUUID()}.json`);
  await writeFile(history, json, { flag: "wx" });
  await writeFile(join(dir, "last-receipt.json"), json);
  if (runDir) await writeFile(join(runDir, "receipt.json"), json, { flag: "wx" }).catch((error: NodeJS.ErrnoException) => {
    if (error.code !== "EEXIST" && error.code !== "ENOENT") throw error;
  });
  console.log(json);
  process.exitCode = exitCode(receipt);
}
