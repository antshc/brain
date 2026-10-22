import type { Page } from "@playwright/test";
import { EvidenceError, type BrowserEvent, type RunEnv } from "./types";

const parse = (value: string) => { try { return JSON.parse(value); } catch { return value; } };

/** localStorage for the page's origin, read through the DevTools protocol. */
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

/** What a map writes in parentheses ("API response") and what a check declares ("api-response"). */
export const sourceId = (name: string) => name.trim().toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");

/**
 * One way to observe the app's state. A check captures through its adapter, and the artifact the adapter produces is
 * the evidence the receipt cites. The kit ships the browser and HTTP collectors; databases, logs and test results are
 * project-owned adapters in proof/adapters/.
 */
export interface EvidenceAdapter {
  /** The id a check declares and a map names, for example `api-response`. */
  readonly source: string;
  /** Can this source verify an outcome by itself? A screenshot cannot: it needs an assertive source beside it. */
  readonly assertive: boolean;
  readonly ext: "json" | "png" | "txt";
  /** Null when usable, otherwise why not. */
  unavailable(env: RunEnv): string | null;
  /** `result` goes back to the check; `artifact` is persisted. Bytes are stored as they are, anything else as JSON. */
  capture(env: RunEnv, query: any): Promise<{ result: unknown; artifact: unknown }>;
}

const needsPage = (env: RunEnv) => (env.surfaces.includes("web") ? null : "this repo has no web surface");

export type DomQuery = { describe: string; read: (page: Page) => Promise<unknown> };
/** Reads the DOM and keeps what was read next to the page's accessibility tree. */
export const domAssertion: EvidenceAdapter = {
  source: "dom-assertion", assertive: true, ext: "json", unavailable: needsPage,
  async capture(env, query: DomQuery) {
    if (!query?.describe || typeof query.read !== "function") throw new EvidenceError("dom-assertion needs { describe, read(page) }.");
    const value = await query.read(env.page);
    const aria = await env.page.locator("body").ariaSnapshot({ timeout: 1500 }).catch(() => null);
    return { result: value, artifact: { describe: query.describe, url: env.page.url(), value: value ?? null, aria } };
  },
};

/** A picture of the page. It never proves a requirement on its own. */
export const screenshot: EvidenceAdapter = {
  source: "screenshot", assertive: false, ext: "png", unavailable: needsPage,
  async capture(env) {
    const png = await env.page.screenshot({ fullPage: true });
    return { result: undefined, artifact: new Uint8Array(png) };
  },
};

export type ApiQuery = { path: string; params?: Record<string, string | number | undefined> };
export type ApiOptions = { headers?: Record<string, string>; fetcher?: typeof fetch };
/** GET a path on the API. Pass auth headers or a fake fetch from the project's adapter. */
export function apiResponseAdapter(options: ApiOptions = {}): EvidenceAdapter {
  const { headers, fetcher = fetch } = options;
  return {
    source: "api-response", assertive: true, ext: "json",
    unavailable: env => (env.apiUrl ? null : "no API URL is known for this run"),
    async capture(env, query: ApiQuery) {
      if (!query?.path) throw new EvidenceError("api-response needs { path }.");
      const url = new URL(query.path, env.apiUrl!);
      for (const [key, value] of Object.entries(query.params ?? {})) if (value !== undefined) url.searchParams.set(key, String(value));
      const response = await fetcher(url, { headers, signal: AbortSignal.timeout(10_000) }).catch(error => {
        throw new EvidenceError(`Can't reach ${url.origin}: ${error instanceof Error ? error.message : String(error)}`);
      });
      const text = await response.text();
      const body = parse(text);
      const result = { status: response.status, body };
      return { result, artifact: { request: { method: "GET", url: url.href }, ...result } };
    },
  };
}

export type EventQuery = { scope?: "step" | "run"; urlIncludes?: string; method?: string; level?: string };
const events = (types: BrowserEvent["type"][]) => (env: RunEnv, query: EventQuery = {}) => {
  const found = env.events.entries.filter(event => types.includes(event.type)
    && (query.scope !== "step" || event.step === env.events.step)
    && (!query.urlIncludes || (event.url ?? "").includes(query.urlIncludes))
    && (!query.method || event.method === query.method)
    && (!query.level || event.level === query.level));
  return { result: found, artifact: { query, events: found } };
};

/** Responses and failed requests the collector saw, from before the first action. */
export const network: EvidenceAdapter = {
  source: "network", assertive: true, ext: "json", unavailable: needsPage,
  capture: async (env, query: EventQuery) => events(["response", "requestfailed"])(env, query),
};

/** Console messages and uncaught errors the collector saw. */
export const consoleLog: EvidenceAdapter = {
  source: "console", assertive: true, ext: "json", unavailable: needsPage,
  capture: async (env, query: EventQuery) => events(["console", "pageerror"])(env, query),
};

export const storage: EvidenceAdapter = {
  source: "storage", assertive: true, ext: "json", unavailable: needsPage,
  async capture(env) {
    const value = await readStorage(env.page);
    return { result: value, artifact: { origin: new URL(env.page.url()).origin, localStorage: value } };
  },
};

/** The sources every repo has. */
export const builtinAdapters = (): EvidenceAdapter[] => [domAssertion, screenshot, apiResponseAdapter(), network, consoleLog, storage];

/** Project adapters replace built-ins with the same source id (auth headers, a different wire). */
export function mergeAdapters(base: readonly EvidenceAdapter[], project: readonly EvidenceAdapter[]): EvidenceAdapter[] {
  const merged = new Map(base.map(adapter => [adapter.source, adapter]));
  for (const adapter of project) merged.set(adapter.source, adapter);
  return [...merged.values()];
}
