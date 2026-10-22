---
name: verify-mole
description: Drive and prove {{APP_NAME}} with the mole CLI. Use to reproduce a bug, verify a change, or show proof that it works. TODO(proof): name the app's folders here so the skill triggers on them.
---

# Verify {{APP_NAME}}

`{{MOLE}}` drives the running app<!-- surface: web+api --> in a real Chrome through the DevTools protocol, and over HTTP<!-- /surface: web+api --><!-- surface: web-only --> in a real Chrome through the DevTools protocol<!-- /surface: web-only --><!-- surface: api-only --> over HTTP<!-- /surface: api-only -->. Commands print JSON on stdout; errors say what to do next. `{{MOLE}} help` lists every command. Details: [proof/README.md](../../../proof/README.md).

A feature has sub-features; a sub-feature has scenarios. A scenario is flows (what a user does) and checks (what must be true), and every check names the evidence that proves it. Ids: `feature`, `feature.sub-feature`, `feature.sub-feature.scenario`.

## The loop

1. **Doctor.** Run `{{MOLE}} doctor`. Done when `ok` is true. Nothing running: start it and leave it running with `{{MOLE}} up --start` (in the background if no human is watching). If the app already runs, attach with `{{MOLE}} up`. Build STALE: the source moved past the running build, so `{{MOLE}} down` and `up` again.
2. **Read the map.** Run `{{MOLE}} features --changed` to see which features your files touch, or start from the [feature map](features/README.md). Open only those maps.
3. **Author or change scenarios.** Read [scripts/agent.md](scripts/agent.md) first, then write the Python in `proof/`.
4. **Reproduce.** Run a flow with `{{MOLE}} flow <id>` and look (`snapshot`, `console`, `network`<!-- surface: api -->, `api get`<!-- /surface: api -->). Done when you can name the observation that is wrong.
5. **Fix** the source, then restart the app so the build is fresh.
6. **Prove.** Run `{{MOLE}} run <id>` for each scenario you touched, then `{{MOLE}} run` with no id before you report: a fix in one feature can break another. Done when every receipt is PASS for the current revision. FAIL lists what to fix. Exit 2 means the evidence is missing, so fix the environment, not the app.
7. **Read the evidence.** Open the artifacts each check cites in its receipt<!-- surface: web -->, the screenshot, and check `pageErrors` is empty: a PASS does not fail on them<!-- /surface: web -->. A PASS covers only what its checks state.
8. **Report** the receipts: verdict per scenario, revision, the checks and the evidence they cite.

## Proof bar

- <!-- surface: web -->Exercise the user path in the browser. Use `eval` only to read state after the path ran.<!-- /surface: web --><!-- surface: api-only -->Exercise the real HTTP contract, never app internals.<!-- /surface: api-only -->
- A check passes only on its own evidence, captured for it and kept on disk. No evidence means ERROR, never PASS.
- The revision is `git HEAD` plus a hash of uncommitted changes under `APP.source_paths` in `{{APP_FILE}}`. Evidence belongs to one revision; after any edit the old receipt proves nothing, and `doctor` reports it as STALE.
- `proof/` (features, flows, checks, pages, components), `proof/kit/`, `mole/` and the feature maps define done. If one looks wrong, report it and stop.
- TODO(proof): what is out of scope for this proof (auth, other services, data the app needs).

## When to stop

- Every receipt PASS for the current revision<!-- surface: web --> and the screenshots read<!-- /surface: web -->: done.
- The same check still fails after two repairs: stop and hand a human the receipt and what you tried.
- `doctor` red or `run` exit 2: fix the environment or ask. Missing evidence is "can't tell", never "probably fine".

Stop only what you started: `{{MOLE}} down` (it also stops an app that `--start` ran). Receipts and evidence stay in `proof/.runs/mole/`.
