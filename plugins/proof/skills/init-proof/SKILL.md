---
name: init-proof
description: "Install the proof kit (mole CLI, receipts, surface adapters, feature maps, verify-mole skill) into a repository in TypeScript (pnpm) or Python, research the codebase, ask the language and which surfaces to prove (web, api, both), and generate starter proof cases. Use when the user explicitly asks to set up proof, mole, or agent verification in a repo."
disable-model-invocation: true
---

# Initialize proof

Run on explicit user invocation. `skillDir :=` the parent of this `SKILL.md`'s absolute path. Read [references/concept.md](references/concept.md) first: it defines features, surfaces, adapters, receipts and revisions, and the rules for good checks.

Outcome: `proof/kit/` (the proof lib), `mole/` (the runner), `proof/` (app seams, features), the `verify-mole` skill with feature maps in `.github/skills/verify-mole/`, the language's commands (below), and `proof/.runs/` gitignored, with the chosen starter cases passing against the repo's running app.

Commands by language (`<mole>`, `<prove>`, `<test>`, `<typecheck>` below):

| | typescript | python |
|---|---|---|
| mole | `pnpm mole` | `python3 -m mole` |
| prove | `pnpm prove` | `python3 -m mole.prove_cli` |
| test | `pnpm test:proof` | `python3 -m pytest proof/test_features.py` |
| typecheck | `pnpm typecheck:proof` | `python3 -m mypy --strict proof mole` |
| app config | `proof/app.ts` | `proof/app.py` |
| registry | `proof/features/index.ts` | `proof/features/__init__.py` |
| feature file, adapters | `.ts` | `.py` |
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

It copies the independent proof lib to `proof/kit/` and the runner that uses it to `mole/`, renders the app seams (`proof/` app config, `proof/features/`, adapters only for chosen surfaces, `proof/README.md`) and the verify-mole skill, and gitignores `proof/.runs/`. It never overwrites: existing files are returned in `skipped`.

- typescript: adds the pnpm scripts, `proof/tsconfig.json`, and runs `pnpm add -D` for missing `tsx @playwright/test @types/node typescript` (approving esbuild's build script).
- python: writes `proof/requirements.txt` (`playwright`, `pytest`, `mypy`) and runs `python3 -m pip install -r proof/requirements.txt` into the active environment; also gitignores `__pycache__/`. A repo that manages dependencies elsewhere (venv, uv, poetry) activates that environment first.

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

For each chosen case, in this order, following the "Add a feature" steps in `proof/README.md`:

1. Write the map `.github/skills/verify-mole/features/<feature>.md` (frontmatter `feature`, `prove`, `touches`, `surfaces`; `## Contract`, `## Driving it`, then web-only and Gotchas sections as needed) and add its row to `features/README.md`. Contracts in user words; no selectors, routes or wire details.
2. Extend the adapters in `proof/features/surfaces/` (`types` shapes, then `web` and/or `api`) so one call returns one shape on each surface.
3. Write `proof/features/<feature>` (`.ts` or `.py`): loop `kit.surfaces`, call adapters through `observe()`, record `kit.check(name, actual, expected, hint)`; surface-only behavior in guarded blocks. Add a `drive` hook when a by-hand call helps.
4. Register in the registry (`proof/features/index.ts` or `__init__.py`) with `surfaces` and `touches`.

Use only routes, selectors, ids and counts you read from the repo, and read-only requests. Remove the `example` feature (code, map, README row, registry entry) once a real feature covers the same surfaces; keep it when the user chose none. Then fill the `TODO(proof)` markers in `.github/skills/verify-mole/SKILL.md` (trigger words, scope exclusions). Confirm no placeholders are left: `grep -rn "TODO(proof)" proof .github/skills/verify-mole` returns nothing.

## Python durable evidence contracts

For new feature implementation, define and review `proof/tools/contracts.py` contracts **before coding**. Pin `contract_digest(Path("proof"))` through the trusted workflow. Reuse live feature names; keep mandatory check/artifact names explicit. Prefer partial business invariants over full response snapshots.

The coding agent runs existing tests on the clean final commit. Authorized project collectors save API/UI/task/browser/DB/log/test captures with `Capture`; the workflow verifies deployed/build SHA and retains the finalized manifest digest outside the artifact folder. Use API reads first; DB only if no suitable API exists by contract. Keep adapters in project-owned `proof/tools/`, never overwrite them.

Run `python3 -m mole evaluate --app <name> --run <folder> --revision <full-sha> --contract-sha256 <reviewed-digest> --manifest-sha256 <trusted-digest>`. This separate mode only evaluates saved evidence; it MUST NOT launch browsers/apps, issue HTTP/SQL or execute tests. Keep reviewed contract imports pure. Missing/incomplete/stale captures are ERROR; conclusive mismatches are FAIL. Preserve original receipt JSON/exit codes. Read `proof/tools/README.md` for schemas, trust requirements, retention and the opt-in Order example. TypeScript/live commands retain their existing behavior.

## 7. Verify

Run from `REPO_PATH`; fix what fails or report it precisely (command, output, cause):

```bash
<typecheck> && <test>
<mole> up --start --headless      # own background process; wait for "ok": true
<mole> doctor                     # ok must be true
<mole> prove                      # exit 0 (PASS)
<mole> down
```

If `up --start` cannot start the app (missing database, container runtime, credentials), do not invent a workaround: report it and run what can run (`<typecheck>`, `<test>`). A FAIL on a freshly generated case is a bug in the case until the app is shown wrong: read the check's `hint`, `expected` and `actual`, fix the adapter or the constant, and re-run. Stop only what you started.

## Rules

- Never overwrite repository files; scaffold reports `skipped`. Never edit `proof/kit/` or `mole/` (an upgrade replaces them; delete a leftover `proof/engine/` from an older scaffold).
- No real feature is wired by scaffold; every real case comes from step 6.
- The eShop files in `references/eshop-example/` are TypeScript examples, never copied verbatim into a repo; Python features follow the same shape.

**Emit**: `REPO_PATH=<path>. Language: <typescript|python>. Surfaces: <list>. Created: <paths>. Skipped: <existing paths or none>. Features: <names>. Receipt: <PASS|FAIL|ERROR|not run> (<revision>). Open items: <TODOs, unknowns, failures or none>.`
