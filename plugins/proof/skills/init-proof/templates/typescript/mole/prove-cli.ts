// Usage: pnpm prove [--url URL] [--feature NAME] [--surface web|api]
// Exit 0 PASS, 1 FAIL, 2 can't tell. Receipts and screenshots go to proof/.runs/.
// Runs against an app you already started, in its own throwaway browser. `pnpm mole prove` does the same in mole's browser.
import { mkdir, writeFile } from "node:fs/promises";
import { join } from "node:path";
import { parseArgs } from "node:util";
import { chromium } from "@playwright/test";
import { APP } from "../proof/app";
import { FEATURES } from "../proof/features";
import { exitCode, proveFeatures, runProof, selectFeatures, surfacesFor } from "../proof/kit";
import { DEFAULT_URL, ROOT, discoverApi, sourceRevision } from "./runtime";

async function main() {
  const { values } = parseArgs({ options: {
    url: { type: "string", default: DEFAULT_URL },
    feature: { type: "string", multiple: true },
    surface: { type: "string", multiple: true },
  } });
  const selected = selectFeatures(FEATURES, values.feature);
  const surfaces = surfacesFor(FEATURES, selected, APP.surfaces, values.surface);
  const apiUrl = surfaces.includes("api") ? await discoverApi() : null;
  if (surfaces.includes("api") && !apiUrl) {
    throw new Error(`The API of ${APP.name} was not found. Start the app, or set PROOF_API_URL, or make APP.api.discover return it${APP.surfaces.includes("web") ? ", or prove the web surface only: --surface web" : ""}`);
  }
  const dir = join(ROOT, "proof", ".runs");
  await mkdir(dir, { recursive: true });

  const browser = await chromium.launch();
  try {
    const receipt = await runProof(browser, values.url!, proveFeatures(FEATURES, selected), {
      screenshot: join(dir, `proof-${Date.now()}.png`), revision: sourceRevision, surfaces, apiUrl, features: selected,
      rerun: "pnpm prove (or pnpm mole prove)", diagnose: "Run pnpm mole doctor (or check the app is running at --url)",
    });
    await writeFile(join(dir, "last-receipt.json"), JSON.stringify(receipt, null, 2));
    console.log(JSON.stringify(receipt, null, 2));
    process.exitCode = exitCode(receipt);
  } finally {
    await browser.close();
  }
}

main().catch(error => {
  console.error(error);
  process.exitCode = 2;
});
