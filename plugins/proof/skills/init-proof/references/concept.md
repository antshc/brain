# The proof concept

Read this once before generating features. The kit exists so an agent can prove a change with evidence instead of saying "it should work".

The kit ships in two languages with one behavior, one receipt shape and one set of feature maps. Names below are TypeScript; Python equivalents: `app.py`, `features/__init__.py`, `snake_case` (`APP.source_paths`, `kit.api_url`, `StartConfig.timeout_s`), sync Playwright, `python3 -m mole` for `pnpm mole`.

Two parts, one direction: `proof/kit/` is the independent proof lib (types, `runProof`, receipt, feature selection; no app, no CLI); `mole/` is the runner at the repo root that starts, drives and inspects the app and calls the kit to prove. The kit never imports the mole or `proof/app`; the mole hands it everything.

## Terms

- **Feature**: a behavior contract in the user's words ("a page lists up to N items, pages count from 1"). It is proved on one or more surfaces.
- **Surface**: how a feature reaches a user. `web` is the app in a real Chrome over CDP; `api` is HTTP. A repo supports the surfaces in `APP.surfaces` (`proof/app.ts` or `proof/app.py`).
- **Surface adapter**: one per surface (`proof/features/surfaces/web.ts`/`web.py`, `api.ts`/`api.py`). It turns one feature call (`items.list({ page: 2 })`) into that surface's wire details (selectors and URLs on web; routes, versioning, 0-based paging, ids on api) and returns the same shape. A rule is written once in the feature and checked on every surface. All selectors, routes and wire details live in adapters, never in a feature or a map.
- **Check**: one recorded fact, `kit.check(name, actual, expected, hint)`. It never throws: a failed check is evidence. Name it `feature/surface: rule`. The hint says what to fix, because the receipt's `next` repeats it.
- **observe(kit, label, step)**: runs an adapter call and turns a thrown `SurfaceError` into a failed `<label>: observed` check, so an unreachable surface is a finding, not a crash (a crash is exit 2, "can't tell").
- **Receipt**: `PASS`/`FAIL`/`ERROR` (exit 0/1/2) with `revision`, `features`, `surfaces`, `checks`, `pageErrors`, `screenshot` (web), `next`. Exit 2 means missing evidence, never "probably fine".
- **Revision**: `git HEAD` plus a hash of uncommitted changes under `APP.sourcePaths`. If it changes while proving, the verdict is ERROR. If it differs from what the running app was started on, `prove` refuses and `doctor` says STALE.
- **mole**: a long-lived Chrome session (`up`/`down`/`doctor`) plus drive and look commands (`open`, `snapshot`, `console`, `network`, `eval`, `api get`), `features --changed`, and `prove`. A feature with a `drive` hook adds `pnpm mole <feature> <verb>`.
- **Feature map**: `.github/skills/verify-mole/features/<feature>.md`. States the contract, how to drive it, and what usually lies. Never selectors or routes. `pnpm test:proof` keeps maps and registry in step.

## Rules for good features

1. One contract rule, one check per surface. Prefer facts a user would state ("page 2 shares no item with page 1") over implementation facts.
2. A rule that holds on every surface goes in the shared loop. Behavior that exists on one surface only (URL state, empty-state page, HTTP status codes) goes in a block guarded by `kit.surfaces.includes(...)`.
3. Seed-dependent numbers (a total of 101) belong in the feature as named constants with a hint naming where the seed lives. If the repo has no stable seed, check relations (page 2 shares nothing with page 1, total >= items shown) instead of constants.
4. Read-only. A proof must not create, change or delete data unless the repo has a disposable test environment, and then the map says so.
5. Every hint names what to look at. "Check that X is seeded" beats "expected 9, got 0".
6. A fresh visitor each run: no cookies, no storage. Auth-dependent features need a documented test account and go in a separate feature with its own map; skip them rather than guessing credentials.

## Worked example

`references/eshop-example/` is a real feature set from eShop (a .NET Aspire AppHost with a Blazor storefront and a catalog API): `app.ts` (everything eShop-specific: the AppHost start command, the .NET SDK prerequisite, `aspire describe` API discovery, Blazor streaming settle), `catalog.ts` (the feature), `web.ts`/`api.ts`/`types.ts` (adapters and shapes), `catalog.md` (the map). They are reference only and import from the kit and mole paths the scaffold uses.
