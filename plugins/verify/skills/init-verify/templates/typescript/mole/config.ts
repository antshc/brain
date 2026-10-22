import type { Page } from "@playwright/test";
import type { Surface } from "../proof/kit";

/** Everything the mole needs to know about this repo's app. proof/app.ts fills it in. */
export type AppConfig = {
  name: string;
  /** Where the app answers by default. `--url` overrides it. */
  url: string;
  /** The surfaces this repo supports. Features may only use these. */
  surfaces: Surface[];
  /** Repo-relative paths whose changes alter the running build. The revision is derived from them. */
  sourcePaths: string[];
  /** Where the feature maps live: <the verify-<app> skill folder>/features. */
  featureMaps: string;
  /** Extra patterns a feature map must not contain (selectors, routes, wire details). */
  mapBanned?: RegExp[];
  /** How `mole up --start` runs the app. Omit when the app is always started by hand. */
  start?: {
    command: string;
    args: string[];
    env?: Record<string, string>;
    cwd?: string;
    /** Throws with an actionable message when a tool is missing. May return extra environment for the command. */
    prerequisites?: () => NodeJS.ProcessEnv | void;
    /** The app has answered `url`; return true once it is really ready (seed loaded, first render done). */
    ready?: (url: string) => Promise<boolean>;
    timeoutMs?: number;
  };
  api?: {
    /** The API base URL, when it is not the app URL or PROOF_API_URL. */
    discover?: () => string | null | Promise<string | null>;
    /** Whether the API really answers at this base URL. Default: any answer below 500. */
    probe?: (baseUrl: string) => boolean | Promise<boolean>;
  };
  web?: {
    /** Wait until a page has finished rendering. Default: the load event. */
    settle?: (page: Page) => Promise<void>;
    /** What a user sees, merged into `mole snapshot`. Default: url, title, h1, aria. */
    snapshot?: (page: Page) => Promise<Record<string, unknown>>;
  };
};
