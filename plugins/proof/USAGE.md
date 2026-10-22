# Proof kit and the mole

The **proof kit** is the evidence library. It defines what a proof is and records its evidence. The **mole** is the CLI agents use to run the app. It drives the app, inspects it and runs the proofs. The kit is `proof/kit/` and knows nothing of the app or the mole. The mole is `mole/` at the repo root (`mole/mole.ts`, or `python3 -m mole`) and uses the kit: dependencies run mole → kit, never back. Whatever the kit needs (revision, surfaces, API URL, the features, the commands to suggest) the mole passes in.

Both kits use the scenario model below. The Python kit's differences are described last.

## Proof kit (TypeScript)

The kit defines what a verification is:

- A **feature** (`defineFeature`) has sub-features; each owns **scenarios** (Given/When/Then), on one surface (`web` or `api`).
- A scenario is an ordered list of steps: **flows** (`defineFlow`: user actions that act and return variables, never a verdict) and **proof checks** (`defineProof`: acceptance assertions that observe and return a finding).
- A proof check declares the **evidence** it uses: DOM assertion, screenshot, API response, network, console, storage. It captures each through `ctx.observe`, and the kit persists it as an artifact. PASS or FAIL without an artifact per declared source is ERROR. A screenshot alone never proves anything.
- After the first step that does not pass, the rest are NOT_REACHED.
- A **receipt** carries a verdict per scenario (PASS, FAIL, ERROR, STALE), each check with its evidence artifacts, the revision and a `next` hint. A change to the revision mid-scenario gives STALE.
- A **feature map** (Markdown, four sections) states each scenario and its proofs in words. The kit parses it and checks it against the registry.

## The mole

The mole launches the app and a Chrome over CDP, then drives it, inspects it and proves it. Its commands fall into four groups:

- **Health:** `up` (`--start` also runs the app), `down`, `doctor`.
- **Drive:** `open`, `reload`, `reset`, and `flow <id>` to reach a state.
- **Look:** `snapshot`, `storage`, `console`, `network`, `screenshot`, `eval`, `api get`.
- **Prove:** `features [--changed]`, `run [target...]` and `receipts [target]`.

It outputs JSON, and its errors say what to do next. `mole help [command]` lists everything.

`mole run` loads the maps and the feature registry from `proof/features/`, runs the selected scenarios through the kit on a fresh visitor each, writes the receipt and artifacts to `proof/.runs/`, and exits 0 for PASS, 1 for FAIL and 2 when it can't tell (ERROR or STALE). A target is a feature, sub-feature or scenario id. With no target it runs everything; a subset is reported as partial coverage, not a full proof. `pnpm prove` does the same in a throwaway browser against a running app.

## Python kit

Same model, in Python: `feature(...).sub_feature(...).scenario(...).flow(...).proof(...).build()` composes `@flow` functions and `ProofCheck(name, evidence, assess)` checks. A check declares evidence objects (`BrowserSnapshot`, `Screenshot`, `NetworkLog`, `ConsoleLog`, `StorageState`, `ApiResponse`, plus `DatabaseEvidence` and `LogEvidence` in `proof/adapters/`); `assess` receives what was captured and returns an `Assessment`. The builder refuses a check with no evidence. Differences from TypeScript:

- The verdict is PASS, FAIL or ERROR (exit 0, 1, 2). A revision change mid-run gives ERROR; `doctor` and `receipts` report a receipt older than the source as STALE.
- After a FAIL or ERROR, later steps are `not_reached`; the other checks in the same checkpoint still run.
- Receipts are saved per scenario in `proof/.runs/receipts/latest/` and `history/`; artifacts in `proof/.runs/runs/<time>-<revision>/<scenario-id>/`.
- `python3 -m mole run [id...]`, `flow <id>`, `receipts [id...]`, `features [--changed]`. `prove` is gone: use `run`. `python3 -m mole.prove_cli [id...]` is the throwaway-browser run.
- `--surface` and per-feature `drive` commands are gone; a scenario's surfaces come from its feature.

## In short

The proof kit defines what a proof is and records its evidence. The mole runs the app and the browser and invokes the proofs. The `verify-<app>` skill tells an agent how to use the mole, with one map per feature.
