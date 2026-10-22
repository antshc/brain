---
name: {{MAINTAIN_SKILL_NAME}}
description: Keep {{APP_NAME}}'s proof kit honest as the app changes — update feature maps, adapters and proofs when source changes, detect drift, and re-prove. Use after changing {{APP_NAME}} code, or when proof checks, maps or the registry look out of date.
---

# Maintain verify {{APP_NAME}}

Keeps `proof/` and the [{{SKILL_NAME}}](../{{SKILL_NAME}}/SKILL.md) skill in step with the source. Concepts and the "Add a feature" steps: [proof/README.md](../../../proof/README.md); scenario-authoring rules: [proof/AGENT.md](../../../proof/AGENT.md). Run from the repo root.

A repo still on v1 (<!-- lang: python -->Python `prove(kit)`<!-- /lang: python --><!-- lang: typescript -->TypeScript `FEATURES`<!-- /lang: typescript -->, `drive` hooks, `Contract`/`Driving it` maps, `prove --feature NAME`) is not upgraded in place: scaffold skips existing files, so move its features aside, delete `proof/kit/`, `mole/` and `proof/features/`, re-run `init-verify`, and rewrite each feature as scenarios.

## Loop

1. **Find what moved.** `{{MOLE}} features --changed` lists the features whose `touches` prefixes your uncommitted changes hit. No feature selected but behavior changed: a feature's `touches` is stale or the behavior has no feature yet (step 4).
2. **Read the maps** of those features (`{{SKILL_DIR}}/features/<name>.md`). The map is the contract; code that now contradicts it is either a regression or a contract change.
3. **Decide per change**:
   - *Regression*: fix the app, leave the proof alone.
   - *Intended contract change*: Update the map's scenario paragraph first, then the scenario's flows and proof checks, constants and hints, then page objects only if the page changed (selectors, routes). One edit per layer; never weaken a check to make it pass.
   - *Seed or data change*: update the named constants and the hint that cites the seed file.
4. **New or moved behavior.** New user-facing feature: add map and feature file and register it in `{{REGISTRY_FILE}}`, as in `proof/README.md` "Add a feature". Moved or renamed source folders: update `touches` in the feature (`{{TOUCHES}}`), and `{{SOURCE_PATHS}}` in `{{APP_FILE}}` if the build inputs moved. Removed feature: delete the code, the map, its row in `features/README.md` and its registry entry.
5. **Keep it in step.** `{{TYPECHECK_PROOF}} && {{TEST_PROOF}}` must pass. It fails on a map with no feature, a feature with no map, a scenario whose paragraph and proof evidence disagree, a check that declares no evidence or a screenshot alone, and a map that names selectors or routes.
6. **Re-prove on a fresh build.** Restart the app so the build matches the source (`{{MOLE}} down; {{MOLE}} up --start`; `{{MOLE}} doctor` must show no STALE). `{{MOLE}} run <feature-or-scenario>` per touched feature, then `{{MOLE}} run` with no target before reporting.

## Drift to look for

- A receipt older than the source: `doctor` reports `STALE`. A STALE receipt proves nothing.
- A check that passes for the wrong reason (a constant copied from the current output, a selector that matches more than intended). Tie each constant to its source.
- `{{SOURCE_PATHS}}` missing a folder that now affects the app: the revision stays unchanged after real edits, so `run` never refuses.
- A feature that only runs on one surface after the repo gained the other: add the adapter and extend `surfaces` in the registry, the map frontmatter and the map's contract.
- `pageErrors` in a PASS receipt: not a failure by itself, but read them.
- A receipt that reports partial coverage (a feature with scenarios that did not run). A subset is not a full proof.

## Rules

- Never edit `proof/kit/` or `mole/`. To change their behavior, change the `{{APP_FILE}}` hooks or report the gap.
- Never fix a failing proof by loosening it. Report what the check observed.
- Report: the receipt verdict, revision, features and surfaces proved, and any map or constant you changed and why.
