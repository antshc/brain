import type { Page } from "@playwright/test";
import type { Feature, Surface } from "../proof/kit";

/** One `mole <feature> <verb> ...` call, handed to the feature's `drive` hook. */
export type DriveCall = {
  /** Every token after the feature name (the verb first), with --surface removed. Parse flags with node:util parseArgs. */
  argv: string[];
  /** The surface to drive on: web unless told otherwise (or the feature has no web). */
  surface: Surface;
  /** The attached page on the web surface, otherwise null. */
  page: Page | null;
  /** The API base URL on the api surface, otherwise null. */
  apiUrl: string | null;
};

/** A proof feature the mole can also drive by hand. */
export type MoleFeature = Feature & {
  /** Optional: lets `pnpm mole <feature> <verb>` drive the feature by hand. Return JSON-able data; throw SurfaceError for user mistakes. */
  drive?: { usage: string; summary: string; run(call: DriveCall): Promise<object> };
};
