import { existsSync } from "node:fs";
import { mkdir, readFile, readdir, writeFile } from "node:fs/promises";
import { join } from "node:path";
import { ADAPTERS } from "../proof/adapters";
import { FEATURES } from "../proof/features";
import { buildRegistry, builtinAdapters, coverage, isStale, mergeAdapters, type Receipt } from "../proof/kit";

export const adapters = () => mergeAdapters(builtinAdapters(), ADAPTERS);
export const registry = () => buildRegistry(FEATURES, adapters());

// What the agent must still do before it may report: a subset of the scenarios is not a full proof.
export function coverageNotes(ran: string[]): string[] {
  const { partial, missing } = coverage(registry(), ran);
  return partial ? [`${missing.length} scenario(s) did not run, so they are not proved. Run pnpm mole run with no target before you report.`] : [];
}

// `latest` is what doctor reads. The history is appended, never overwritten: failures stay next to the final green.
export async function saveReceipt(dir: string, latest: string, receipt: Receipt) {
  const json = JSON.stringify(receipt, null, 2);
  await mkdir(join(dir, "receipts"), { recursive: true });
  await writeFile(latest, json);
  await writeFile(join(dir, "receipts", `${receipt.at.replace(/[:.]/g, "-")}-${receipt.revision ?? "unknown"}.json`), json);
}

export async function readReceipts(dir: string, target?: string): Promise<Receipt[]> {
  const folder = join(dir, "receipts");
  const files = existsSync(folder) ? (await readdir(folder)).filter(name => name.endsWith(".json")).sort() : [];
  const receipts: Receipt[] = [];
  for (const file of files) receipts.push(JSON.parse(await readFile(join(folder, file), "utf8")));
  return target ? receipts.filter(receipt => receipt.scenarios.some(scenario => scenario.id === target || scenario.id.startsWith(`${target}.`))) : receipts;
}

// Is the last receipt about the code that is there now? For doctor.
export async function proofStatus(latest: string, source: string | null): Promise<{ status: string; next?: string }> {
  const receipt: Receipt | null = existsSync(latest) ? JSON.parse(await readFile(latest, "utf8")) : null;
  if (!receipt) return { status: "none yet", next: "pnpm mole run" };
  if (isStale(receipt, source)) {
    return { status: `STALE: the last receipt says ${receipt.verdict} for ${receipt.revision}, but the source is now ${source}. That proof is for code that no longer exists.`, next: "pnpm mole run" };
  }
  const partial = coverage(registry(), receipt.scenarios.map(scenario => scenario.id)).partial ? `, only ${receipt.scenarios.length} scenario(s): run pnpm mole run for all` : "";
  return { status: `${receipt.verdict} for the current source (${source}) at ${receipt.at}${partial}`, ...(receipt.verdict !== "PASS" ? { next: receipt.next[0] } : {}) };
}
