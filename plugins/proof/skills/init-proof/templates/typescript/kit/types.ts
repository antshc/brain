import type { Page } from "@playwright/test";

// A surface is one way a feature reaches a user: `web` is the app in a real Chrome, `api` is HTTP.
export type Surface = "web" | "api";

export type Check = { name: string; pass: boolean; expected: unknown; actual: unknown; hint?: string };
export type ProofKit = {
  /** A fresh visitor (no storage) with the app already loaded. Blank when the run has no web surface. */
  page: Page;
  /** The surfaces this run proves. A feature checks its contract on each. */
  surfaces: Surface[];
  /** Where the API answers, or null when the run has no API. */
  apiUrl: string | null;
  /** What to tell the reader to do when a surface cannot be observed. Supplied by the caller of runProof. */
  diagnose: string;
  /** Record one fact. Never throws: a failed check is evidence, not a crash. */
  check(name: string, actual: unknown, expected: unknown, hint?: string): void;
  /** localStorage for the app's origin, read through the DevTools protocol. */
  storage(): Promise<Record<string, unknown>>;
};
export type Prove = (kit: ProofKit) => Promise<void>;
export type Receipt = {
  verdict: "PASS" | "FAIL" | "ERROR";
  revision: string | null;
  app: string;
  at: string;
  checks: Check[];
  /** The features this run proved. A subset is not a full proof. */
  features?: string[];
  /** The surfaces this run proved. A surface that did not run is not proved. */
  surfaces?: Surface[];
  pageErrors: string[];
  screenshot?: string;
  error?: string;
  next: string[];
};

/** A named proof: what it proves, on which surfaces, and which files it must be re-proved for. */
export type Feature = {
  prove: Prove;
  /** Repo-relative path prefixes whose changes this feature must be re-proved for. */
  touches: string[];
  /** The surfaces the feature is proved on. */
  surfaces: Surface[];
};
