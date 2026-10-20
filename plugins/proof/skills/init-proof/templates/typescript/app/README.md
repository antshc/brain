# Proof kit and mole

Drives {{APP_NAME}} like a user, records facts, and writes a receipt with a verdict. It complements the repo's own tests: those assert and stop at the first failure, while a proof records every fact and tells you what to fix.

## Layout

| Path | Owner | What it is |
|---|---|---|
| `kit/` | the kit | The independent proof lib: `types.ts`, `surfaces.ts`, `features.ts`, `receipt.ts`, `run.ts` (`runProof`). Knows nothing of the app or the mole. Do not edit; an upgrade replaces this folder. |
| `../mole/` | the mole | The runner at the repo root: `mole.ts` (CLI), `prove-cli.ts`, `runtime.ts`, `config.ts`, `feature.ts`, `receipts.ts`, `selftest.ts`. It uses the kit. Do not edit; an upgrade replaces this folder. |
| `app.ts` | you | `APP`: the URL, start command, source paths, API discovery and page hooks. The only place the mole learns about this app. |
| `features/` | you | One proof per feature, registered in `features/index.ts`. |
| `features/surfaces/` | you | One adapter per surface. Turns a feature call into that surface's wire details and returns one shape. |
| `.github/skills/verify-mole/` | you | The agent skill and one map per feature. |

## Concepts

- A **feature** is a behavior contract, proved on one or more **surfaces**: `web` (the app in a real Chrome over CDP) and `api` (HTTP). Supported here: {{SURFACES_TEXT}}.
- A **surface adapter** returns the same shape on every surface, so a rule is written once and checked everywhere. `check()` never throws; a check is named `feature/surface: rule`.
- A **receipt** is PASS, FAIL or ERROR (exit 0, 1, 2) with the revision, features, surfaces, checks with hints, `pageErrors` and a screenshot.
- The **revision** is `git HEAD` plus a hash of uncommitted changes under `APP.sourcePaths`. A stale build makes `prove` refuse.

## Run it

```bash
pnpm install
pnpm exec playwright install chromium   # once
pnpm mole up --start      # own terminal: runs the app, waits until it is ready, opens Chrome
pnpm mole up              # or attach to an app you already run (--url for another URL)
pnpm mole doctor          # is this instance worth driving?
pnpm mole prove           # every feature on every surface; --feature, --surface narrow it
pnpm mole down            # stop what up started
pnpm prove                # the same proof in a throwaway browser against a running app
pnpm test:proof           # maps and registry in step; your adapter tests
pnpm typecheck:proof
```

`pnpm mole help` lists every command, including `pnpm mole <feature> <verb>` for features with a `drive` hook. The agent loop is in [.github/skills/verify-mole/SKILL.md](../.github/skills/verify-mole/SKILL.md).

## Add a feature

1. Write the contract in `.github/skills/verify-mole/features/<name>.md` (frontmatter: `feature`, `prove`, `touches`, `surfaces`; sections `## Contract` and `## Driving it`; update `features/README.md`).
2. Extend the adapters in `features/surfaces/` with the calls the contract needs, returning one shape per surface.
3. Write `features/<name>.ts`: loop over `kit.surfaces`, call the adapter through `observe()`, and `kit.check(name, actual, expected, hint)`.
4. Register it in `features/index.ts` with its `surfaces` and `touches`.
5. Run `pnpm test:proof`, then `pnpm mole prove --feature <name>`.

Environment: `PROOF_URL` (app URL), `PROOF_API_URL` (API base URL), `MOLE_DIR` (isolates a second mole instance). Receipts and screenshots go to `proof/.runs/` (gitignored). Needs Node 20.12 or newer.
