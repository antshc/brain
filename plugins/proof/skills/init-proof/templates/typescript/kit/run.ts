import { isDeepStrictEqual } from "node:util";
import type { Browser, Page } from "@playwright/test";
import type { Check, Prove, Receipt, Surface } from "./types";

const parse = (value: string) => { try { return JSON.parse(value); } catch { return value; } };

export async function readStorage(page: Page): Promise<Record<string, unknown>> {
  const cdp = await page.context().newCDPSession(page);
  try {
    await cdp.send("DOMStorage.enable");
    const { entries } = await cdp.send("DOMStorage.getDOMStorageItems", {
      storageId: { securityOrigin: new URL(page.url()).origin, isLocalStorage: true },
    });
    return Object.fromEntries(entries.map(([key, value]) => [key, parse(value)]));
  } finally { await cdp.detach(); }
}

/** The caller supplies a revision of the code under proof, or it stays null. */
export type Revision = () => Promise<string | null>;

export type RunOptions = {
  /** Where to save a full-page screenshot (web surface only). */
  screenshot?: string;
  revision?: Revision;
  /** The surfaces this run proves. Default: web. */
  surfaces?: Surface[];
  apiUrl?: string | null;
  /** The feature names this run proves, recorded on the receipt. */
  features?: string[];
  /** How to run the proof again, quoted in a FAIL receipt. */
  rerun?: string;
  /** What to do when the verdict is "can't tell" or a surface cannot be observed. */
  diagnose?: string;
};

const show = (value: unknown) => JSON.stringify(value);

// Runs a `prove()` against a running app and returns a receipt. If the revision changes while
// proving, the evidence belongs to two builds and the verdict is "can't tell".
export async function runProof(browser: Browser, app: string, prove: Prove, options: RunOptions = {}): Promise<Receipt> {
  const { screenshot, revision = async () => null, apiUrl = null, features } = options;
  const surfaces = options.surfaces ?? ["web"];
  const rerun = options.rerun ?? "Run the proof again";
  const diagnose = options.diagnose ?? "Check that the app is running and the build is fresh";
  const checks: Check[] = [];
  const pageErrors = new Set<string>();
  const receipt: Receipt = { verdict: "ERROR", revision: null, app, at: new Date().toISOString(), checks, pageErrors: [], next: [], ...(features ? { features } : {}), surfaces };
  const context = await browser.newContext({ ignoreHTTPSErrors: true }); // fresh visitor: no storage, no cookies
  try {
    const page = await context.newPage();
    page.setDefaultTimeout(2500);
    page.on("pageerror", error => pageErrors.add(error.message));
    page.on("console", message => { if (message.type() === "error") pageErrors.add(message.text()); });
    receipt.revision = await revision();
    if (surfaces.includes("web")) await page.goto(app, { waitUntil: "load", timeout: 5000 });
    await prove({
      page, surfaces, apiUrl, diagnose, storage: () => readStorage(page),
      check: (name, actual, expected, hint) =>
        checks.push({ name, pass: isDeepStrictEqual(actual, expected), expected, actual, ...(hint ? { hint } : {}) }),
    });
    const now = await revision();
    if (now !== receipt.revision) {
      receipt.error = `The source changed while proving (started on ${receipt.revision}, now ${now}). Evidence from two builds proves neither.`;
    } else if (!checks.length) {
      receipt.error = "prove() recorded no checks. Call check(name, actual, expected) for each fact you observe.";
    } else {
      receipt.verdict = checks.every(check => check.pass) ? "PASS" : "FAIL";
    }
    // A run with no web surface has no page worth a picture.
    if (screenshot && surfaces.includes("web")) {
      try {
        await page.screenshot({ path: screenshot, fullPage: true });
        receipt.screenshot = screenshot;
      } catch (error) {
        // The receipt tells the agent to read the screenshot, so a missing one can't pass.
        receipt.verdict = "ERROR";
        receipt.error = `Couldn't save the screenshot (${error instanceof Error ? error.message.split("\n")[0] : String(error)}). A receipt without its screenshot can't be read.`;
      }
    }
  } catch (error) {
    receipt.error = "prove() threw: " + (error instanceof Error ? error.message.split("\n")[0] : String(error)) +
      ". If something is missing, that is a finding: record it with check() instead of throwing.";
  } finally {
    await context.close();
  }
  receipt.pageErrors = [...pageErrors];
  if (receipt.verdict === "PASS") {
    receipt.next = [surfaces.includes("web")
      ? "These checks passed on this revision. They cover nothing else: read the screenshot for anything they missed."
      : "These checks passed on this revision. They cover nothing else."];
  } else if (receipt.verdict === "FAIL") {
    receipt.next = [...checks.filter(check => !check.pass).map(check =>
      check.hint ?? `Fix "${check.name}": expected ${show(check.expected)}, got ${show(check.actual)}.`),
      `Then re-run: ${rerun}`];
  } else {
    receipt.next = [receipt.error ?? "Unknown error.", `Can't tell is not the same as broken. ${diagnose}, then prove again.`];
  }
  return receipt;
}
