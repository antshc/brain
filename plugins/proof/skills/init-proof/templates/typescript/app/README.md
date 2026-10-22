# Proof kit and mole

Verifies {{APP_NAME}} like a user, scenario by scenario, and writes a receipt with a verdict and the evidence behind it. It complements the repo's own tests: those assert and stop at the first failure, while a proof records evidence and tells you what to fix.

## Layout

| Path | Owner | What it is |
|---|---|---|
| `kit/` | the kit | The independent proof lib: `types.ts`, `surfaces.ts`, `evidence.ts`, `features.ts`, `map.ts`, `receipt.ts`, `run.ts`. Knows nothing of the app or the mole. Do not edit; an upgrade replaces this folder. |
| `../mole/` | the mole | The runner at the repo root: `mole.ts` (CLI), `prove.ts`, `prove-cli.ts`, `maps.ts`, `artifacts.ts`, `receipts.ts`, `runtime.ts`, `config.ts`, `commands.ts`, `selftest.ts`. It uses the kit. Do not edit; an upgrade replaces this folder. |
| `app.ts` | you | `APP`: the URL, start command, source paths, API discovery and page hooks. The only place the mole learns about this app. |
| `features/` | you | One `defineFeature` per feature, registered in `features/index.ts`. |
| `pages/`, `components/` | you | Page objects and reusable parts. All selectors and routes live here. |
| `flows/` | you | User actions. A flow acts and returns variables; it never decides acceptance. |
| `checks/` | you | Proof checks. A check observes through declared evidence and returns a finding. |
| `adapters/` | you | Project evidence sources (`ADAPTERS`). A source with a built-in's id replaces it. |
| `.github/skills/verify-mole/` | you | The agent skill and one map per feature. |

## Concepts

- A **feature** has **sub-features**; each owns **scenarios**: Given/When/Then paths a user takes, on one surface of {{SURFACES_TEXT}}.
- A scenario composes **flows** and attaches **proof checks**. Each check names the **evidence** it proves itself with: DOM assertion, screenshot, API response, network, console, storage. A PASS or FAIL needs an artifact for every declared source; without one the verdict is ERROR.
- The **feature map** (`.github/skills/verify-mole/features/<feature>.md`) states each scenario and its proofs in words. `pnpm test:proof` keeps maps and registry in step.
- A **receipt** carries a verdict per scenario (PASS, FAIL, ERROR, STALE), the checks with their evidence artifacts, and a `next` hint. Exit 0 for PASS, 1 for FAIL, 2 for ERROR or STALE.
- The **revision** is `git HEAD` plus a hash of uncommitted changes under `APP.sourcePaths`. A receipt is bound to it: a stale build makes `run` refuse, and a change mid-run gives STALE.
- Evidence artifacts are written under `proof/.runs/artifacts/<revision>/<run>/<scenario>/`.

## Run it

```bash
pnpm install
pnpm exec playwright install chromium   # once
pnpm mole up --start      # own terminal: runs the app, waits until it is ready, opens Chrome
pnpm mole up              # or attach to an app you already run (--url for another URL)
pnpm mole doctor          # is this instance worth driving? lists evidence sources
pnpm mole features        # features and scenarios; --changed for those touching your edits
pnpm mole flow <id>       # run one flow to reach a state (--var k=v)
pnpm mole run [target...] # prove scenarios; a target is a feature, sub-feature or scenario id
pnpm mole receipts        # the saved receipts for this revision
pnpm mole down            # stop what up started
pnpm prove [target...]    # the same proof in a throwaway browser against a running app
pnpm test:proof           # maps and registry in step; the mole's self-tests
pnpm typecheck:proof
```

`pnpm mole help` lists every command. The agent loop is in [.github/skills/verify-mole/SKILL.md](../.github/skills/verify-mole/SKILL.md).

## Add a feature

1. Write the map in `.github/skills/verify-mole/features/<name>.md`: four sections, one paragraph per scenario ending in `**Proof:** check (Evidence); ...`. Update `features/README.md`.
2. Put selectors in `pages/` (and `components/`), user actions in `flows/`, and acceptance checks in `checks/`.
3. Write `features/<name>.ts` with `defineFeature`: `touches`, `surfaces`, then `subFeature` and `scenario` with `.flow(...)` and `.proof(...)` in the map's order.
4. Register it in `features/index.ts`.
5. Run `pnpm test:proof`, then `pnpm mole run <name>`.

## Upgrading from the v1 kit

v1 had `FEATURES` entries with `prove(kit)`, `features/surfaces/`, `kit.check` and `drive` hooks, and `pnpm mole prove --feature`. There is no compatibility mode: re-run `/init-proof`, which replaces `kit/` and `mole/`, then move each v1 check into a `defineProof`, each adapter call into a page object or flow, and each map into the four-section format.

Environment: `PROOF_URL` (app URL), `PROOF_API_URL` (API base URL), `MOLE_DIR` (isolates a second mole instance). Receipts go to `proof/.runs/` (gitignored). Needs Node 20.12 or newer.
