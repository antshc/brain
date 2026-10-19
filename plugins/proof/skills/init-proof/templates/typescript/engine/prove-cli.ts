// Usage: pnpm prove [--url URL] [--feature NAME] [--surface web|api]
// Exit 0 PASS, 1 FAIL, 2 can't tell. Receipts and screenshots go to proof/.runs/.
// Runs against an app you already started, in its own throwaway browser. `pnpm mole prove` does the same in mole's browser.
import { mkdir, writeFile } from "node:fs/promises";
import { join } from "node:path";
import { parseArgs } from "node:util";
import { chromium } from "@playwright/test";
import { APP } from "../app";
import { runProof } from "./proof";
import { proveFeatures, selectFeatures, surfacesFor } from "./registry";
import { DEFAULT_URL, ROOT, discoverApi, sourceRevision } from "./runtime";

async function main() {
  const { values } = parseArgs({ options: {
    url: { type: "string", default: DEFAULT_URL },
    feature: { type: "string", multiple: true },
    surface: { type: "string", multiple: true },
  } });
  const selected = selectFeatures(values.feature);
  const surfaces = surfacesFor(selected, values.surface);
  const apiUrl = surfaces.includes("api") ? await discoverApi() : null;
  if (surfaces.includes("api") && !apiUrl) {
    throw new Error(`The API of ${APP.name} was not found. Start the app, or set PROOF_API_URL, or make APP.api.discover return it${APP.surfaces.includes("web") ? ", or prove the web surface only: --surface web" : ""}`);
  }
  const dir = join(ROOT, "proof", ".runs");
  await mkdir(dir, { recursive: true });

  const browser = await chromium.launch();
  try {
    const receipt = await runProof(browser, values.url!, proveFeatures(selected), join(dir, `proof-${Date.now()}.png`), sourceRevision, { surfaces, apiUrl });
    receipt.features = selected;
    receipt.surfaces = surfaces;
    await writeFile(join(dir, "last-receipt.json"), JSON.stringify(receipt, null, 2));
    console.log(JSON.stringify(receipt, null, 2));
    process.exitCode = receipt.verdict === "PASS" ? 0 : receipt.verdict === "FAIL" ? 1 : 2;
  } finally {
    await browser.close();
  }
}

main().catch(error => {
  console.error(error);
  process.exitCode = 2;
});
