---
name: init-proof
description: "Install the proof kit (mole CLI, receipts, surface adapters, feature maps, verify-mole skill) into a pnpm repository, research the codebase, ask which surfaces to prove (web, api, both), and generate starter proof cases. Use when the user explicitly asks to set up proof, mole, or agent verification in a repo."
disable-model-invocation: true
---

# Initialize proof

Run on explicit user invocation. `skillDir :=` the parent of this `SKILL.md`'s absolute path. Read [references/concept.md](references/concept.md) first: it defines features, surfaces, adapters, receipts and revisions, and the rules for good checks.

Outcome: `proof/` (engine, app seams, features), the `verify-mole` skill with feature maps in `.github/skills/verify-mole/`, `pnpm mole` / `prove` / `test:proof` / `typecheck:proof` scripts, and `proof/.runs/` gitignored, with the chosen starter cases passing against the repo's running app.

## 1. Resolve the repository

`REPO_PATH := git rev-parse --show-toplevel` from cwd. Stop if cwd is not inside a Git repository. Stop unless it is a pnpm repository (`package.json` plus `pnpm-lock.yaml`, `pnpm-workspace.yaml` or `packageManager: pnpm@…`); for any other stack point the user to the `create-verification-skill` skill and stop. Requires Node 20.12 or newer and at least one commit.

## 2. Ask which surfaces

Use `ask_user` (never ask in plain text), one form:

- `surfaces`: `web` / `api` / `both`. Offer a research hint: web if the repo renders pages or has a frontend; api if it exposes HTTP routes; both when it has each. Respect the choice, even against the hint.
- `app_name`: default the `package.json` name (or repo folder name).

## 3. Scaffold

```bash
python3 "<skillDir>/scripts/scaffold.py" --repo "$REPO_PATH" --surfaces "<web|api|both>" --app-name "<name>"
```

It copies the engine to `proof/engine/`, renders the app seams (`proof/app.ts`, `proof/features/`, adapters only for chosen surfaces, `proof/README.md`, `proof/tsconfig.json`) and the verify-mole skill, adds the pnpm scripts, runs `pnpm add -D` for missing `tsx @playwright/test @types/node typescript` (approving esbuild's build script), and gitignores `proof/.runs/`. It never overwrites: existing files are returned in `skipped`. A non-zero exit means the repo was refused; relay `error`. If `install` is not `installed`/`nothing to install`, fix it (`pnpm add -D …`) before step 7. Keep the JSON: it feeds the final report.

Install Chromium once if `pnpm mole doctor` later says it is missing: `pnpm exec playwright install chromium`.

## 4. Research the codebase

Work through [references/research-checklist.md](references/research-checklist.md) and fill `proof/app.ts` from what the repo says: `url`, `sourcePaths`, `start` (command, env, `ready`, `prerequisites`, `timeoutMs`), `api.discover`/`probe` and `web.settle`/`snapshot` for chosen surfaces. Existing e2e and API tests are hints for cases. Ask the user (one `ask_user` form) only for facts the repo does not state. Resolve every `TODO(proof)` in `proof/app.ts`; delete the marker with it.

## 5. Ask which cases

Offer a multi-select of starter cases via `ask_user`: pre-fill candidates the research found (real routes, real endpoints, e2e-backed behaviors) and otherwise this generic menu for the chosen surfaces:

- **api**: health, list with paging, get by id, 404 for a missing id, validation error.
- **web**: home loads, navigation between pages, list page and detail page, not-found page.
- **both**: the same contract proved on web and api through adapters (for example the list and the detail).
- **none**: keep only the `example` smoke feature.

## 6. Generate the cases

For each chosen case, in this order, following the "Add a feature" steps in `proof/README.md`:

1. Write the map `.github/skills/verify-mole/features/<feature>.md` (frontmatter `feature`, `prove`, `touches`, `surfaces`; `## Contract`, `## Driving it`, then web-only and Gotchas sections as needed) and add its row to `features/README.md`. Contracts in user words; no selectors, routes or wire details.
2. Extend the adapters in `proof/features/surfaces/` (`types.ts` shapes, then `web.ts` and/or `api.ts`) so one call returns one shape on each surface.
3. Write `proof/features/<feature>.ts`: loop `kit.surfaces`, call adapters through `observe()`, record `kit.check(name, actual, expected, hint)`; surface-only behavior in guarded blocks. Add a `drive` hook when a by-hand call helps.
4. Register in `proof/features/index.ts` with `surfaces` and `touches`.

Use only routes, selectors, ids and counts you read from the repo, and read-only requests. Remove the `example` feature (code, map, README row, registry entry) once a real feature covers the same surfaces; keep it when the user chose none. Then fill the `TODO(proof)` markers in `.github/skills/verify-mole/SKILL.md` (trigger words, scope exclusions). Confirm no placeholders are left: `grep -rn "TODO(proof)" proof .github/skills/verify-mole` returns nothing.

## 7. Verify

Run from `REPO_PATH`; fix what fails or report it precisely (command, output, cause):

```bash
pnpm typecheck:proof && pnpm test:proof
pnpm mole up --start --headless      # own background process; wait for "ok": true
pnpm mole doctor                     # ok must be true
pnpm mole prove                      # exit 0 (PASS)
pnpm mole down
```

If `up --start` cannot start the app (missing database, container runtime, credentials), do not invent a workaround: report it and run what can run (`typecheck:proof`, `test:proof`). A FAIL on a freshly generated case is a bug in the case until the app is shown wrong: read the check's `hint`, `expected` and `actual`, fix the adapter or the constant, and re-run. Stop only what you started.

## Rules

- Never overwrite repository files; scaffold reports `skipped`. Never edit `proof/engine/` (an upgrade replaces it).
- No real feature is wired by scaffold; every real case comes from step 6.
- The eShop files in `references/eshop-example/` are examples, never copied verbatim into a repo.

**Emit**: `REPO_PATH=<path>. Surfaces: <list>. Created: <paths>. Skipped: <existing paths or none>. Features: <names>. Receipt: <PASS|FAIL|ERROR|not run> (<revision>). Open items: <TODOs, unknowns, failures or none>.`
