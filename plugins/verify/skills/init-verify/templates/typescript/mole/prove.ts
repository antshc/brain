import type { Browser } from "@playwright/test";
import { join } from "node:path";
import { APP } from "../proof/app";
import { RegistryError, checkMaps, openVisitor, parseMap, runScenarios, selectScenarios, surfacesFor, type Receipt } from "../proof/kit";
import { fileArtifactStore } from "./artifacts";
import { loadMaps } from "./maps";
import { adapters, coverageNotes, registry, saveReceipt } from "./receipts";
import { MoleError, sourceRevision } from "./runtime";

export type ProveOptions = {
  browser: Browser;
  appUrl: string;
  apiUrl: string | null;
  /** Where receipts and artifacts go. */
  dir: string;
  targets: string[];
  rerun: string;
  diagnose: string;
};

/** Checks the maps against the builders, runs the selected scenarios in fresh visitors, and saves the receipt next to its artifacts. */
export async function proveScenarios(options: ProveOptions): Promise<Receipt> {
  let reg;
  try { reg = registry(); } catch (error) {
    if (error instanceof RegistryError) throw new MoleError(`The features are not valid:\n- ${error.problems.join("\n- ")}`, "Fix proof/features/ and proof/adapters/, then run again.");
    throw error;
  }
  const maps = await loadMaps();
  const problems = checkMaps(reg, maps, APP.mapBanned ?? []);
  if (problems.length) throw new MoleError(`The feature maps and the builders disagree:\n- ${problems.join("\n- ")}`, "Make the map paragraphs and proof/features/ say the same thing, then run again.");
  let refs;
  try { refs = selectScenarios(reg, options.targets); } catch (error) {
    throw new MoleError((error as Error).message.split("\n")[0], "See the scenarios: pnpm mole features");
  }
  const surfaces = surfacesFor(refs, APP.surfaces);
  if (surfaces.includes("api") && !options.apiUrl) throw new MoleError("The API was not found, and a selected scenario needs it.",
    "Start the app, or set PROOF_API_URL, or make APP.api.discover in proof/app.ts return the base URL.");
  const revision = await sourceRevision();
  const parsed = Object.fromEntries(Object.entries(maps).map(([name, text]) => [name, parseMap(text)]));
  const receipt = await runScenarios(refs, {
    app: APP.name, appUrl: options.appUrl, apiUrl: options.apiUrl, surfaces, adapters: adapters(), revision: sourceRevision,
    store: fileArtifactStore(options.dir, revision),
    visitor: () => openVisitor(options.browser, options.appUrl, surfaces),
    mapOf: ref => {
      const map = parsed[ref.feature.name];
      const entry = map?.scenarios.find(scenario => scenario.sub === ref.subFeature.id && scenario.id === ref.scenario.id);
      return entry ? { hash: map.hash, text: entry.text } : undefined;
    },
    rerun: options.rerun, diagnose: options.diagnose,
  }, options.targets);
  receipt.next.push(...coverageNotes(receipt.scenarios.map(scenario => scenario.id)));
  await saveReceipt(options.dir, join(options.dir, "receipt.json"), receipt);
  return receipt;
}
