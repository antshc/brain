---
name: maintain-proof
description: Keep a repository's proof kit honest as the app changes — update feature maps, adapters and proofs when source changes, detect drift, and re-prove. Use after changing app code in a repo that has proof/ and .github/skills/verify-<app>/, or when proof checks, maps or the registry look out of date.
---

# Maintain proof

Applies to a repo scaffolded by `init-proof` (it has `proof/app.ts` or `proof/app.py`, `proof/features/` and `.github/skills/verify-<app>/`). Concepts: `init-proof/references/concept.md` in this plugin. Run from the repo root.

Commands below use the TypeScript form. Python kit (`proof/app.py`): `pnpm mole` = `python3 -m mole`; `pnpm prove` = `python3 -m mole.prove_cli`; `pnpm test:proof` = `python3 -m pytest proof/test_features.py`; `pnpm typecheck:proof` = `python3 -m mypy --strict proof mole`; `features/index.ts` = `features/__init__.py`; `APP.sourcePaths` = `APP.source_paths`.

Both kits use the scenario model (feature builder, flows, proof checks, evidence, four-section maps). A repo still on v1 (Python `prove(kit)`, `drive` hooks, `Contract`/`Driving it` maps, `prove --feature NAME`; TypeScript `FEATURES`) is not upgraded in place: scaffold skips existing files, so move its features aside, delete `proof/kit/`, `mole/` and `proof/features/`, re-run `init-proof`, and rewrite each feature as scenarios.

## Loop

1. **Find what moved.** `pnpm mole features --changed` lists the features whose `touches` prefixes your uncommitted changes hit. No feature selected but behavior changed: a feature's `touches` is stale or the behavior has no feature yet (step 4).
2. **Read the maps** of those features (`.github/skills/verify-<app>/features/<name>.md`). The map is the contract; code that now contradicts it is either a regression or a contract change.
3. **Decide per change**:
   - *Regression*: fix the app, leave the proof alone.
   - *Intended contract change*: Update the map's scenario paragraph first, then the scenario's flows and proof checks, constants and hints, then page objects only if the page changed (selectors, routes). One edit per layer; never weaken a check to make it pass.
   - *Seed or data change*: update the named constants and the hint that cites the seed file.
4. **New or moved behavior.** New user-facing feature: add map and feature file and register it, as in `proof/README.md` "Add a feature". Moved or renamed source folders: update `touches` in the feature (TypeScript: `feature.touches(...)`; Python: `feature(..., touches=[...])`), and `APP.sourcePaths` in `proof/app.ts` if the build inputs moved. Removed feature: delete the code, the map, its row in `features/README.md` and its registry entry.
5. **Keep it in step.** `pnpm typecheck:proof && pnpm test:proof` must pass. It fails on a map with no feature, a feature with no map, a scenario whose paragraph and `.proof()` evidence disagree, a check that declares no evidence or a screenshot alone, and a map that names selectors or routes.
6. **Re-prove on a fresh build.** Restart the app so the build matches the source (`pnpm mole down; pnpm mole up --start`; `pnpm mole doctor` must show no STALE). `pnpm mole run <feature-or-scenario>` per touched feature, then `pnpm mole run` with no target before reporting.

## Drift to look for

- A receipt older than the source: `doctor` reports `STALE`. A STALE receipt proves nothing.
- A check that passes for the wrong reason (a constant copied from the current output, a selector that matches more than intended). Tie each constant to its source.
- `APP.sourcePaths` missing a folder that now affects the app: the revision stays unchanged after real edits, so `run` never refuses.
- A feature that only runs on one surface after the repo gained the other: add the adapter and extend `surfaces` in the registry, the map frontmatter and the map's contract.
- `pageErrors` in a PASS receipt: not a failure by itself, but read them.
- A receipt that reports partial coverage (a feature with scenarios that did not run). A subset is not a full proof.

## Rules

- Never edit `proof/kit/` or `mole/`. To change their behavior, change the `proof/app.ts` (or `proof/app.py`) hooks or report the gap.
- Never fix a failing proof by loosening it. Report what the check observed.
- Report: the receipt verdict, revision, features and surfaces proved, and any map or constant you changed and why.
