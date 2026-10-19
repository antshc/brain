---
name: maintain-proof
description: Keep a repository's proof kit honest as the app changes — update feature maps, adapters and proofs when source changes, detect drift, and re-prove. Use after changing app code in a repo that has proof/ and .github/skills/verify-mole/, or when proof checks, maps or the registry look out of date.
---

# Maintain proof

Applies to a repo scaffolded by `init-proof` (it has `proof/app.ts`, `proof/features/` and `.github/skills/verify-mole/`). Concepts: `init-proof/references/concept.md` in this plugin. Run from the repo root.

## Loop

1. **Find what moved.** `pnpm mole features --changed` lists the features whose `touches` prefixes your uncommitted changes hit. No feature selected but behavior changed: a feature's `touches` is stale or the behavior has no feature yet (step 4).
2. **Read the maps** of those features (`.github/skills/verify-mole/features/<name>.md`). The map is the contract; code that now contradicts it is either a regression or a contract change.
3. **Decide per change**:
   - *Regression*: fix the app, leave the proof alone.
   - *Intended contract change*: update the map's `## Contract` first, then the check and its constants and hints, then the adapters only if the wire or the page changed (selectors, routes, versioning, paging). One edit per layer; never weaken a check to make it pass.
   - *Seed or data change*: update the named constants and the hint that cites the seed file.
4. **New or moved behavior.** New user-facing feature: add map, adapter calls, feature file and registry entry, as in `proof/README.md` "Add a feature". Moved or renamed source folders: update `touches` in `proof/features/index.ts` **and** the map's frontmatter (`pnpm test:proof` fails when they differ), and `APP.sourcePaths` in `proof/app.ts` if the build inputs moved. Removed feature: delete the code, the map, its row in `features/README.md` and its registry entry.
5. **Keep it in step.** `pnpm typecheck:proof && pnpm test:proof` must pass: it fails on a map with no feature, a feature with no map, mismatched `touches`/`surfaces`/`prove`, a map that names selectors or routes, and surfaces the repo does not support.
6. **Re-prove on a fresh build.** Restart the app so the build matches the source (`pnpm mole down; pnpm mole up --start`; `pnpm mole doctor` must show no STALE), run `pnpm mole prove --feature <name>` per touched feature, then `pnpm mole prove` with no flag before reporting.

## Drift to look for

- A receipt older than the source: `doctor` reports `STALE`. A STALE receipt proves nothing.
- A check that passes for the wrong reason (a constant copied from the current output, a selector that matches more than intended). Tie each constant to its source.
- `APP.sourcePaths` missing a folder that now affects the app: the revision stays unchanged after real edits, so `prove` never refuses.
- A feature that only runs on one surface after the repo gained the other: add the adapter and extend `surfaces` in the registry, the map frontmatter and the map's contract.
- `pageErrors` in a PASS receipt: not a failure by itself, but read them.

## Rules

- Never edit `proof/engine/`. To change engine behavior, change `proof/app.ts` hooks or report the gap.
- Never fix a failing proof by loosening it. Report what the check observed.
- Report: the receipt verdict, revision, features and surfaces proved, and any map or constant you changed and why.
