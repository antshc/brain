import { existsSync } from "node:fs";
import { mkdir, readFile, writeFile } from "node:fs/promises";
import { join } from "node:path";
import { FEATURES } from "../proof/features";
import { coverage, isStale, type Receipt, type Surface } from "../proof/kit";

// What the agent must still do before it may report: a subset of features or surfaces is not a full proof.
export function coverageNotes(run: { features: string[]; surfaces: Surface[] }): string[] {
  const { partialFeatures, skippedSurfaces } = coverage(FEATURES, run);
  return [
    ...(partialFeatures ? [`Only ${run.features.join(", ")} was proved. Run pnpm mole prove with no --feature before you report.`] : []),
    ...(skippedSurfaces.length ? [`The ${skippedSurfaces.join(", ")} surface did not run, so it is not proved. Run pnpm mole prove with no --surface before you report.`] : []),
  ];
}

// `latest` is what doctor reads. The history is appended, never overwritten: failures stay next to the final green.
export async function saveReceipt(dir: string, latest: string, receipt: Receipt) {
  const json = JSON.stringify(receipt, null, 2);
  await mkdir(join(dir, "receipts"), { recursive: true });
  await writeFile(latest, json);
  await writeFile(join(dir, "receipts", `${receipt.at.replace(/[:.]/g, "-")}-${receipt.revision ?? "unknown"}.json`), json);
}

// Is the last receipt about the code that is there now? For doctor.
export async function proofStatus(latest: string, source: string | null): Promise<{ status: string; next?: string }> {
  const receipt: Receipt | null = existsSync(latest) ? JSON.parse(await readFile(latest, "utf8")) : null;
  if (!receipt) return { status: "none yet", next: "pnpm mole prove" };
  if (isStale(receipt, source)) {
    return { status: `STALE: the last receipt says ${receipt.verdict} for ${receipt.revision}, but the source is now ${source}. That proof is for code that no longer exists.`, next: "pnpm mole prove" };
  }
  const { partialFeatures, skippedSurfaces } = coverage(FEATURES, { features: receipt.features ?? Object.keys(FEATURES), surfaces: receipt.surfaces ?? [] });
  const partial = receipt.features && partialFeatures ? `, only ${receipt.features.join(", ")}: run pnpm mole prove for all` : "";
  const skipped = receipt.surfaces && skippedSurfaces.length ? `, only the ${receipt.surfaces.join(", ")} surface: run pnpm mole prove with no --surface` : "";
  return { status: `${receipt.verdict} for the current source (${source}) at ${receipt.at}${partial}${skipped}`, ...(receipt.verdict !== "PASS" ? { next: receipt.next[0] } : {}) };
}
