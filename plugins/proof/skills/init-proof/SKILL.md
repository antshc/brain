---
name: init-proof
description: "Install the proof kit (mole CLI, receipts, evidence adapters, scenario builders, feature maps, verify-<app> skill) into a repository in TypeScript (pnpm) or Python, research the codebase, ask the language and which surfaces to prove (web, api, both), and generate starter proof cases. Use when the user explicitly asks to set up proof, mole, or agent verification in a repo."
disable-model-invocation: true
---

# Initialize proof

Run on explicit user invocation. `skillDir :=` the parent of this `SKILL.md`'s absolute path. Read [references/concept.md](references/concept.md) first: it defines features, scenarios, evidence, receipts and revisions, and the rules for good checks.

Outcome: `proof/kit/` (the proof lib), `mole/` (the runner), `proof/` (app seams, features), the single agent skill `verify-<app>` (`<app>` is the app name lowercased, non-alphanumerics to `-`; the JSON `skill` field) with its feature maps in `.github/skills/verify-<app>/`, the language's commands (below), and `proof/.runs/` gitignored, with the chosen starter cases passing against the repo's running app.

Commands by language (`<mole>`, `<run>`, `<prove>`, `<test>`, `<typecheck>` below):

| | typescript | python |
|---|---|---|
| mole | `pnpm mole` | `python3 -m mole` |
| run (a `<mole>` verb) | `run` | `run` |
| prove (throwaway browser) | `pnpm prove` | `python3 -m mole.prove_cli` |
| test | `pnpm test:proof` | `python3 -m pytest proof/test_features.py` |
| typecheck | `pnpm typecheck:proof` | `python3 -m mypy --strict proof mole` |
| app config | `proof/app.ts` | `proof/app.py` |
| registry | `proof/features/index.ts` | `proof/features/__init__.py` |
| feature files | `.ts` | `.py` |
| install Chromium | `pnpm exec playwright install chromium` | `python3 -m playwright install chromium` |

## 1. Resolve the repository

`REPO_PATH := git rev-parse --show-toplevel` from cwd. Stop if cwd is not inside a Git repository. Requires at least one commit.

## 2. Ask language and surfaces

Use `ask_user` (never ask in plain text), one form:

- `language`: `typescript` / `python`. Hint: typescript when the repo is a pnpm repository (`package.json` plus `pnpm-lock.yaml`, `pnpm-workspace.yaml` or `packageManager: pnpm@…`, Node 20.12 or newer); otherwise python (Python 3.10 or newer; the app under test may be any stack). typescript is refused in a non-pnpm repo.
- `surfaces`: `web` / `api` / `both`. Offer a research hint: web if the repo renders pages or has a frontend; api if it exposes HTTP routes; both when it has each. Respect the choice, even against the hint.
- `app_name`: default the `package.json` name (or repo folder name).

## 3. Scaffold

```bash
python3 "<skillDir>/scripts/scaffold.py" --repo "$REPO_PATH" --language "<typescript|python>" --surfaces "<web|api|both>" --app-name "<name>"
```

It copies the independent proof lib to `proof/kit/` and the runner that uses it to `mole/`, renders the app seams (`proof/` app config, `proof/features/`, `proof/AGENT.md`, and for the chosen surfaces `proof/adapters/`, `pages/`, `flows/`, `checks/`, `proof/README.md`) and the verify-<app> skill from the one shared `templates/verify-mole/` (the only skill it creates; never a `verify-mole` one). `proof/AGENT.md` holds the scenario-authoring rules; the skill's `references/component-extractor.md` is the subagent prompt for missing UI controls, and gitignores `proof/.runs/`. It never overwrites: existing files are returned in `skipped`.

- typescript: also seeds `proof/components/`; adds the pnpm scripts, `proof/tsconfig.json`, and runs `pnpm add -D` for missing `tsx @playwright/test @types/node typescript` (approving esbuild's build script).
- python: also seeds `proof/components/`; writes `proof/requirements.txt` (`playwright`, `pytest`, `mypy`) and runs `python3 -m pip install -r proof/requirements.txt` into the active environment; also gitignores `__pycache__/`. A repo that manages dependencies elsewhere (venv, uv, poetry) activates that environment first.

A non-zero exit means the repo was refused; relay `error`. If `install` is not `installed`/`nothing to install`, fix it before step 7. Keep the JSON: it feeds the final report.

Install Chromium once if `<mole> doctor` later says it is missing.

## 4. Research the codebase

Work through [references/research-checklist.md](references/research-checklist.md) and fill the app config (`proof/app.ts` or `proof/app.py`) from what the repo says: `url`, `sourcePaths`, `start` (command, env, `ready`, `prerequisites`, `timeoutMs`), `api.discover`/`probe` and `web.settle`/`snapshot` for chosen surfaces (snake_case in Python). Existing e2e and API tests are hints for cases. Ask the user (one `ask_user` form) only for facts the repo does not state. Resolve every `TODO(proof)` in the app config; delete the marker with it.

## 5. Ask which cases

Offer a multi-select of starter cases via `ask_user`: pre-fill candidates the research found (real routes, real endpoints, e2e-backed behaviors) and otherwise this generic menu for the chosen surfaces:

- **api**: health, list with paging, get by id, 404 for a missing id, validation error.
- **web**: home loads, navigation between pages, list page and detail page, not-found page.
- **both**: the same contract proved on web and api through adapters (for example the list and the detail).
- **none**: keep only the `example` smoke feature.

## 6. Generate the cases

Use only routes, selectors, ids and counts you read from the repo, and read-only requests. Remove the `example` feature (code, map, README row, registry entry) once a real feature covers the same surfaces; keep it when the user chose none. Write the skill and the map index first (below). Then fill every other `TODO(proof)` marker in `.github/skills/verify-<app>/SKILL.md` (trigger words, scope exclusions). Confirm no placeholders are left: `grep -rn "TODO(proof)" proof .github/skills/verify-<app>` returns nothing.

### The verify-<app> skill and map index

Write the one project-local skill, aimed at a cold agent that has never seen the app, with the mole as the harness. It lives in the scaffolded `.github/skills/verify-<app>/` (never a second skill).

1. Interview the repo, ask the user only what you cannot observe: surface (web UI, API, both), run (the repo's own dev command, ports, env vars, seed data, auth), drive (existing Playwright or API tests first), observe (screenshots, response bodies, logs, DB state), isolate (can two instances run side by side?). The step 4 research answers most of it. A checkout that does not build or start is fixed or reported first, never documented around.
2. Fill the `## This app` section of `SKILL.md`, each item grounded in the repo with no placeholder left:
   - **Launch:** the `up --start` command, the ready signal, usable from an empty data dir (migrations, seed data done), teardown. Ready means usable, not just that a process answers.
   - **Doctor:** what `<mole> doctor` must show (URL, build revision, port owned by this run, auth valid).
   - **Drive:** real stable handles from this repo (ARIA names, routes, endpoints), not examples.
   - **Evidence:** what each surface captures and where it lands. Proof standards: the real user path, not internal setters or test-only endpoints; the action and the resulting state; side effects checked beside what is visible; mocks only at a production boundary. A dry-run or test mode is verified by observing what it skips, not by its name.
   - **Cleanup:** stop only what you started, never by process name. Cleanup removes instances and scratch state, never the evidence.
   - **Isolation:** if two instances cannot run side by side, say so and refuse to drive an instance this run did not start.
   Keep the frontmatter `name: verify-<app>` and a `description` that names the app, its surfaces and when to use it.
3. Fill the `features/README.md` index: Baseline preconditions, Driving conventions, Proof and skip reporting, and a row per feature. One map per chosen case in the four-section format, aiming at the top 3 to 5 user-facing features. A journey whose precondition the seed data lacks reports a failure; the reason goes in that map's Gotchas. Never weaken the journey to make it pass.
4. After step 7 passes, prove the skill once: launch, doctor, run one mapped scenario, clean up, and confirm the evidence is still in `proof/.runs/mole/`. Run the cleanup after every failed attempt so no process or port is stranded. A skill that was never executed is a draft.

### typescript

For each chosen case, following the "Add a feature" steps in `proof/README.md`:

1. Explore the running app when the UI exists: *Run `playwright-cli` skill to navigate, snapshot and confirm locators*. Read `proof/AGENT.md` in the repo and follow it.
2. Missing reusable UI parts (dropdown, modal, table, form): launch a subagent whose prompt is the body of `.github/skills/verify-<app>/references/component-extractor.md`; pass the capability needed and the inventory in `proof/components/README.md`. Review the files it returns.
3. Write the map `.github/skills/verify-<app>/features/<feature>.md` in the four-section format of `features/README.md`: sub-features, how a user gets there, one unbulleted `**(sub | scenario):**` paragraph per scenario with `**Proof:** check (evidence)`, gotchas. Add its row to `features/README.md`. User words only; no selectors, routes or wire details.
4. Write page objects, flows and checks in `proof/pages/`, `flows/`, `checks/`; evidence adapters in `proof/adapters/` only when the kit's sources (DOM assertion, API response, network, console, storage, screenshot) do not reach the result.
5. Write `proof/features/<feature>.ts` with `defineFeature`: `touches`, `surfaces`, sub-features, scenarios composing `.flow()` and `.proof()` in the map's order. Register it in `proof/features/index.ts`.

### python

For each chosen case, following the "Add a scenario" steps in `proof/README.md`:

1. Explore the running app when the UI exists: *Run `playwright-cli` skill to navigate, snapshot and confirm locators*. Read `proof/AGENT.md` in the repo and follow it.
2. Missing reusable UI parts (dropdown, modal, table, form): launch a new subagent session whose prompt is the body of `.github/skills/verify-<app>/references/component-extractor.md`; pass the control needed, the feature and page, and the `proof/components/` inventory. Review the components and scenario draft it returns.
3. Write the map `.github/skills/verify-<app>/features/<feature>.md` in the four-section format of `features/README.md`: sub-features, how a user gets there, one unbulleted `**(sub | scenario):**` paragraph per scenario with `**Proof** check (Evidence labels)`, gotchas. Add its row to `features/README.md`. User words only; no selectors, routes or wire details.
4. Write page objects, flows and checks in `proof/pages/`, `flows/`, `checks/`; evidence adapters in `proof/adapters/` only when the kit's sources (screenshot, network log, API response) do not reach the result.
5. Write `proof/features/<feature>.py` with the builder: `touches`, `surfaces`, sub-features, scenarios composing flows and checks in the map's order. Register it in `proof/features/__init__.py`.

## 7. Verify

Run from `REPO_PATH`; fix what fails or report it precisely (command, output, cause):

```bash
<typecheck> && <test>
<mole> up --start --headless      # own background process; wait for "ok": true
<mole> doctor                     # ok must be true
<mole> <run>                      # exit 0 (PASS)
<mole> down
```

If `up --start` cannot start the app (missing database, container runtime, credentials), do not invent a workaround: report it and run what can run (`<typecheck>`, `<test>`). A FAIL on a freshly generated case is a bug in the case until the app is shown wrong: read the check's `hint`, `expected` and `actual`, fix the adapter, page object or constant, and re-run. Stop only what you started.

## Rules

- Never overwrite repository files; scaffold reports `skipped`. Never edit `proof/kit/` or `mole/` (an upgrade replaces them; delete a leftover `proof/engine/` from an older scaffold).
- A v1 scaffold (typescript `FEATURES` record or python `prove(kit)`, `drive` hooks, `Contract`/`Driving it` maps) is not upgraded in place: scaffold never overwrites, so move its features aside, delete `proof/kit/`, `mole/` and `proof/features/`, re-scaffold, then rewrite each feature as scenarios (steps 5 and 6).
- No real feature is wired by scaffold; every real case comes from step 6.
- The eShop files in `references/eshop-example/` are TypeScript examples, never copied verbatim into a repo; Python scenarios follow the same shape with the builder.

**Emit**: `REPO_PATH=<path>. Language: <typescript|python>. Surfaces: <list>. Created: <paths>. Skipped: <existing paths or none>. Features: <names>. Receipt: <PASS|FAIL|ERROR|not run> (<revision>). Open items: <TODOs, unknowns, failures or none>.`
