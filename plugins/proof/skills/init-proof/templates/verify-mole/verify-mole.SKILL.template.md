---
name: verify-mole
description: Drive and prove {{APP_NAME}} with the mole CLI. Use to reproduce a bug, verify a change, or show proof that it works. TODO(proof): name the app's folders here so the skill triggers on them.
---

# Verify {{APP_NAME}}

`pnpm mole` drives the running app<!-- surface: web+api --> in a real Chrome through the DevTools protocol, and over HTTP. A feature can be driven on a `--surface`: `web` (default) or `api`<!-- /surface: web+api --><!-- surface: web-only --> in a real Chrome through the DevTools protocol<!-- /surface: web-only --><!-- surface: api-only --> over HTTP<!-- /surface: api-only -->. Commands print JSON on stdout; errors say what to do next. `pnpm mole help` lists every command. Details: [proof/README.md](../../../proof/README.md).

## The loop

1. **Doctor.** Run `pnpm mole doctor`. Done when `ok` is true. Nothing running: start it and leave it running with `pnpm mole up --start` (in the background if no human is watching). If the app already runs, attach with `pnpm mole up`. Build STALE: the source moved past the running build, so `pnpm mole down` and `up` again.
2. **Read the map.** Run `pnpm mole features --changed` to see which features your files touch, or start from the [feature map](features/README.md). Open only those maps. Each states the behavior contract, how to drive it, and what usually lies.
3. **Reproduce.** Drive the feature (`pnpm mole <feature> <verb>` when it has a drive hook) and look (`snapshot`, `console`, `network`, `api get`). <!-- surface: web+api -->A bug seen on one surface: run the same call on the other with `--surface web|api` to see where it starts. <!-- /surface: web+api -->Done when you can name the observation that is wrong.
4. **Fix** the source, then restart the app so the build is fresh.
5. **Prove.** Run `pnpm mole prove --feature <name>` for each feature you touched<!-- surface: web+api -->, and `--surface web` or `--surface api` to iterate on one surface<!-- /surface: web+api -->, then `pnpm mole prove` with no flag before you report: a fix in one feature can break another, and a surface that did not run is not proved. The receipt lists `surfaces`. Done when the verdict is PASS for the current revision. FAIL lists what to fix. Exit 2 means the evidence is missing, so fix the environment, not the app.
6. **Read the evidence.** <!-- surface: web -->Read the screenshot named in the receipt, and check `pageErrors` is empty: a PASS does not fail on them.<!-- /surface: web --><!-- surface: api-only -->Read each check's `expected` and `actual`: a PASS covers only what its checks state.<!-- /surface: api-only -->
7. **Report** the receipt: verdict, revision, surfaces, checks<!-- surface: web -->, screenshot path<!-- /surface: web -->.

## Proof bar

- <!-- surface: web -->Exercise the user path in the browser. Use `eval` only to read state after the path ran.<!-- /surface: web --><!-- surface: api-only -->Exercise the real HTTP contract through the surface adapter, never by calling app internals.<!-- /surface: api-only -->
- The revision is `git HEAD` plus a hash of uncommitted changes under `APP.sourcePaths` in `proof/app.ts`. Evidence belongs to one revision; after any edit the old receipt proves nothing, and `doctor` reports it as STALE.
- `proof/features/` (one proof per feature), `proof/engine/` and the feature maps define done. If one looks wrong, report it and stop.
- TODO(proof): what is out of scope for this proof (auth, other services, data the app needs).

## When to stop

- PASS for the current revision<!-- surface: web --> and the screenshot read<!-- /surface: web -->: done.
- The same check still fails after two fixes: stop and hand a human the receipt and what you tried.
- `doctor` red or `prove` exit 2: fix the environment or ask. Missing evidence is "can't tell", never "probably fine".

Stop only what you started: `pnpm mole down` (it also stops an app that `--start` ran). Receipts<!-- surface: web --> and screenshots<!-- /surface: web --> stay in `proof/.runs/mole/`.
