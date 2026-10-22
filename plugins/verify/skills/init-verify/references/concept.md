# The proof concept

Read this once before generating features. The kit exists so an agent can prove a change with evidence instead of saying "it should work".

Both kits use the scenario model described here. Python names: `app.py`, `features/__init__.py`, `snake_case`, sync Playwright, `python3 -m mole` for `pnpm mole`, the `feature(...).sub_feature(...).scenario(...).flow(...).proof(...).build()` builder for `defineFeature`, `@flow` for `defineFlow`, `ProofCheck(name, evidence, assess)` for `defineProof`, and evidence classes (`BrowserSnapshot` for the DOM assertion, `NetworkLog`, `ApiResponse`, `Screenshot`, `ConsoleLog`, `StorageState`) for evidence sources.

Two parts, one direction: `proof/kit/` is the independent proof lib (types, features, evidence, receipt, run; no app, no CLI); `mole/` is the runner at the repo root that starts, drives and inspects the app and calls the kit to prove. The kit never imports the mole or `proof/app`; the mole hands it everything.

## Terms

- **Feature**: a behavior contract in the user's words ("a page lists up to N items, pages count from 1"), split into sub-features.
- **Scenario**: one user path through a sub-feature on one surface, written Given/When/Then. Its id is `feature.sub-feature.scenario`. `web` is the app in a real Chrome over CDP; `api` is HTTP. A repo supports the surfaces in `APP.surfaces` (`proof/app.ts`).
- **Flow**: a user action (`defineFlow`). It acts and returns variables for later steps; it never decides acceptance. Selectors, routes and wire details live in `pages/`, `components/` and `adapters/`, never in a feature or a map.
- **Proof check**: an acceptance assertion (`defineProof`). It declares the evidence it uses, observes through `ctx.observe`, and returns a finding (`pass`, `expected`, `actual`, `hint`). It never navigates. The hint says what to fix, because the receipt's `next` repeats it.
- **Evidence**: the artifact a check observed: DOM assertion, screenshot, API response, network, console, storage. A project can add sources in `proof/adapters/`. A PASS or FAIL without an artifact per declared source is ERROR, and a screenshot alone is rejected.
- **Receipt**: per scenario `PASS`/`FAIL`/`ERROR`/`STALE` (exit 0/1/2/2) with `revision`, the checks with their evidence artifacts, per-step results, coverage and `next`. After the first step that does not pass, the rest are NOT_REACHED. Exit 2 means missing evidence or a changed revision, never "probably fine".
- **Revision**: `git HEAD` plus a hash of uncommitted changes under `APP.sourcePaths`. If it changes while a scenario runs, that scenario is STALE. If it differs from what the running app was started on, `run` refuses and `doctor` says STALE.
- **mole**: a long-lived Chrome session (`up`/`down`/`doctor`) plus drive and look commands (`open`, `snapshot`, `console`, `network`, `eval`, `api get`), `flow <id>`, `features --changed`, `run [target...]` and `receipts`.
- **Feature map**: `.github/skills/verify-<app>/features/<feature>.md`, four sections: Sub-features, How to get to it (user POV), Driving it with Mole (one paragraph per scenario ending in its proofs and their evidence), Gotchas. Never selectors or routes. `pnpm test:proof` keeps maps and registry in step.

## Rules for good features

1. One scenario, one user path. Prefer facts a user would state ("page 2 shares no item with page 1") over implementation facts.
2. A rule that holds on every surface gets one scenario per surface, reusing the same wording. Behavior that exists on one surface only (URL state, empty-state page, HTTP status codes) gets a scenario on that surface only.
3. Prove with the strongest evidence that fits: what the user sees (DOM assertion) and what the server said (API response, network). Add a screenshot only next to a check that reads state.
4. Seed-dependent numbers (a total of 101) belong in the check as named constants with a hint naming where the seed lives. If the repo has no stable seed, check relations (page 2 shares nothing with page 1, total >= items shown) instead of constants.
5. Read-only. A proof must not create, change or delete data unless the repo has a disposable test environment, and then the map says so.
6. Every hint names what to look at. "Check that X is seeded" beats "expected 9, got 0".
7. A fresh visitor each run: no cookies, no storage. Auth-dependent features need a documented test account and go in a separate feature with its own map; skip them rather than guessing credentials.

## Worked example

`references/eshop-example/` is a real feature set from eShop (a .NET Aspire AppHost with a Blazor storefront and a catalog API) in the scenario model: `app.ts` (everything eShop-specific: the AppHost start command, the .NET SDK prerequisite, `aspire describe` API discovery, Blazor streaming settle), `adapters/`, `components/`, `pages/`, `flows/`, `checks/`, `features/catalog.ts` and `catalog.md` (the map). `v1/` keeps the older per-surface adapter version. They are reference only and import from the kit paths the scaffold uses.
