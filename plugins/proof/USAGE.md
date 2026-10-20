# Proof kit and the mole

The **proof kit** is the evidence library. It defines what a proof is and records its evidence. The **mole** is the CLI agents use to run the app. It drives the app, inspects it and runs the proofs. The kit sits in `proof/engine/` (`proof.ts` or `proof.py`) and the mole in `proof/engine/mole.ts` (or `python3 -m proof.engine.mole`).

## Proof kit

The kit defines the contract for a proof:

- A `Prove` function receives a `ProofKit`: a fresh `page`, the `surfaces` being proved, the `apiUrl`, `check(name, actual, expected, hint)` and `storage()`.
- `check` records a fact and never throws, so a failed check is evidence rather than a crash.
- `storage()` reads localStorage over the DevTools protocol.
- It defines the `Receipt` shape: the verdict (PASS, FAIL or ERROR), the app revision, the checks, the features and surfaces proved, page errors, a screenshot and next steps.
- `runProof` executes a proof against a fresh visitor and builds the receipt. If the revision changes mid-run, the verdict is "can't tell".

## The mole

The mole launches the app and a Chrome over CDP, then drives it, inspects it and proves it. Its commands fall into four groups:

- **Health:** `up` (`--start` also runs the app), `down`, `doctor`.
- **Drive:** `open`, `reload`, `reset`, plus one `<feature> <verb>` command per feature that defines one.
- **Look:** `snapshot`, `storage`, `console`, `network`, `screenshot`, `eval`, `api get`.
- **Prove:** `features [--changed]` and `prove [--feature NAME] [--surface web|api]`.

It outputs JSON, and its errors say what to do next. `mole help [command]` lists everything.

`mole prove` loads the feature proofs from `proof/features/` and runs each through the proof kit on a fresh visitor. It then writes the receipt to `proof/.runs/` and exits 0 for PASS, 1 for FAIL and 2 when it can't tell. With no flag it runs every feature on every surface; a subset is not a full proof.

## In short

The proof kit defines what a proof is and records its evidence. The mole runs the app and the browser and invokes the proofs. The `verify-mole` skill tells an agent how to use the mole, with one map per feature.
