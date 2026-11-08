// Usage: pnpm prove [--url URL] [target...]    target: feature | feature.sub-feature | feature.sub-feature.scenario
// Exit 0 PASS, 1 FAIL, 2 can't tell. Receipts and artifacts go to proof/.runs/.
// Runs against an app you already started, in its own throwaway browser. `pnpm mole run` does the same in mole's browser.
import { mkdir } from "node:fs/promises";
import { join } from "node:path";
import { parseArgs } from "node:util";
import { chromium } from "@playwright/test";
import { exitCode } from "../proof/kit";
import { proveScenarios } from "./prove";
import { DEFAULT_URL, MoleError, ROOT, discoverApi } from "./runtime";

async function main() {
  const { values, positionals } = parseArgs({ allowPositionals: true, options: { url: { type: "string", default: DEFAULT_URL } } });
  const dir = join(ROOT, "proof", ".runs");
  await mkdir(dir, { recursive: true });
  const browser = await chromium.launch();
  try {
    const receipt = await proveScenarios({
      browser, appUrl: values.url!, apiUrl: await discoverApi(), dir, targets: positionals,
      rerun: "pnpm prove (or pnpm mole run)", diagnose: "Run pnpm mole doctor (or check the app is running at --url)",
    });
    console.log(JSON.stringify(receipt, null, 2));
    process.exitCode = exitCode(receipt);
  } finally {
    await browser.close();
  }
}

main().catch(error => {
  const known = error instanceof MoleError;
  console.error(known ? JSON.stringify({ ok: false, error: error.message, next: error.next }, null, 2) : error);
  process.exitCode = known ? error.code : 2;
});
