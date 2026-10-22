---
name: verify-mole
description: Drive and prove {{APP_NAME}} with the mole CLI. Use to reproduce a bug, verify a change, or show proof that it works. TODO(proof): name the app's folders here so the skill triggers on them.
---

# Verify {{APP_NAME}}

`{{MOLE}}` drives the running app<!-- surface: web+api --> in a real Chrome through the DevTools protocol, and over HTTP<!-- /surface: web+api --><!-- surface: web-only --> in a real Chrome through the DevTools protocol<!-- /surface: web-only --><!-- surface: api-only --> over HTTP<!-- /surface: api-only -->. A feature has sub-features; a sub-feature has scenarios; a scenario is user flows plus proof checks, each check bound to the evidence it observes. Commands print JSON on stdout; errors say what to do next. `{{MOLE}} help` lists every command. Details: [proof/README.md](../../../proof/README.md).

## The loop

1. **Doctor.** Run `{{MOLE}} doctor`. Done when `ok` is true. Nothing running: start it and leave it running with `{{MOLE}} up --start` (in the background if no human is watching). If the app already runs, attach with `{{MOLE}} up`. Build STALE: the source moved past the running build, so `{{MOLE}} down` and `up` again.
2. **Read the map.** Run `{{MOLE}} features --changed` to see which features your files touch, or start from the [feature map](features/README.md). Open only those maps. Each lists sub-features, how a user gets there, and one paragraph per scenario with its proof and evidence.
3. **Author.** Missing or changed scenario: read [scripts/agent.md](scripts/agent.md) and follow it before writing flows, checks or map paragraphs.
4. **Reproduce.** Run the scenario that covers the bug: `{{MOLE}} run <feature.sub-feature.scenario>`. Look around with `snapshot`, `console`, `network`<!-- surface: api -->, `api get`<!-- /surface: api -->, and replay a flow with `{{MOLE}} flow <id>`. Done when you can name the observation that is wrong.
5. **Fix** the source, then restart the app so the build is fresh.
6. **Prove.** Run `{{MOLE}} run <target>` for each feature, sub-feature or scenario you touched, then `{{MOLE}} run` with no target before you report: a fix in one feature can break another, and a scenario that did not run is not proved. Done when the verdict is PASS for the current revision. FAIL lists what to fix. Exit 2 (ERROR or STALE) means the proof could not be made, so fix the environment, not the app.
7. **Read the evidence.** `{{MOLE}} receipts` lists each check's artifacts. Open them: a PASS covers only what its checks observed.<!-- surface: web --> A screenshot proves nothing alone; read it, and check `pageErrors` is empty.<!-- /surface: web -->
8. **Report** the receipt: verdict, revision, scenarios, evidence paths.

## Proof bar

- <!-- surface: web -->Exercise the user path in the browser. Use `eval` only to read state after the path ran.<!-- /surface: web --><!-- surface: api-only -->Exercise the real HTTP contract through the evidence adapter, never by calling app internals.<!-- /surface: api-only -->
- Every proof check names its evidence in the map and declares it in code. A PASS without an artifact for each declared source is rejected.
- The revision is `git HEAD` plus a hash of uncommitted changes under `APP.sourcePaths` in `{{APP_FILE}}`. Evidence belongs to one revision; after any edit the old receipt proves nothing, and `doctor` reports it as STALE.
- `proof/features/`, `proof/kit/`, `mole/` and the feature maps define done. Never weaken a check to make it pass. If one looks wrong, report it and stop.
- TODO(proof): what is out of scope for this proof (auth, other services, data the app needs).

## When to stop

- PASS for the current revision, evidence read: done.
- The same check still fails after two repairs: stop and hand a human the receipt and what you tried.
- `doctor` red or `run` exit 2: fix the environment or ask. Missing evidence is "can't tell", never "probably fine".

Stop only what you started: `{{MOLE}} down` (it also stops an app that `--start` ran). Receipts and evidence stay in `proof/.runs/mole/`.
