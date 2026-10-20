import type { AppConfig } from "../mole/config";

// The one file that says what this app is. The mole reads it; every value comes from the codebase, not a guess.
// Resolve each TODO(proof) from the repo (see the init-proof research checklist), then delete the marker.
export const APP: AppConfig = {
  name: {{APP_NAME_JSON}},
  // TODO(proof): the URL the app answers on locally. PROOF_URL overrides it.
  url: process.env.PROOF_URL ?? "http://localhost:3000",
  surfaces: [{{SURFACES_LIST}}],
  // TODO(proof): repo-relative folders whose changes alter the running build. The revision is derived from them.
  sourcePaths: ["src"],
  // TODO(proof): how `pnpm mole up --start` runs the app, and how it knows the app is ready (seeded, first render done).
  start: {
    command: "pnpm",
    args: ["dev"],
    // prerequisites: () => { throw new Error("What is missing and how to install it"); },
    // ready: async url => (await fetch(url)).ok,
    timeoutMs: 120_000,
  },
  // <surface: api>
  api: {
    // TODO(proof): where the API answers. The default is the app URL; PROOF_API_URL overrides it.
    discover: () => process.env.PROOF_URL ?? "http://localhost:3000",
    // probe: async baseUrl => (await fetch(new URL("/health", baseUrl))).ok,
  },
  // </surface: api>
  // <surface: web>
  web: {
    // settle: async page => { await page.waitForLoadState("load"); await page.locator("main").waitFor(); },
    // snapshot: async page => ({ /* what a user sees on this app's pages */ }),
  },
  // </surface: web>
};
