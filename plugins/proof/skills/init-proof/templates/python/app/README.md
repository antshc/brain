# Proof kit and mole

Verifies {{APP_NAME}} like a user, scenario by scenario, and writes a receipt with a verdict. It complements the repo's own tests: those assert and stop at the first failure, while a scenario records every check with its evidence and tells you what to fix.

## Layout

| Path | Owner | What it is |
|---|---|---|
| `kit/` | the kit | The independent proof lib: `types.py`, `builder.py`, `surfaces.py`, `features.py`, `evidence.py`, `receipt.py`, `run.py`. It imports nothing from the app or the mole. Do not edit; an upgrade replaces this folder. |
| `../mole/` | the kit | The runner at the repository root: `mole.py` (CLI), `commands.py`, `runner.py`, `receipts.py`, `prove_cli.py`, `runtime.py`, `config.py`, `selftest.py`. It uses the kit, never the reverse. Do not edit; an upgrade replaces this folder. |
| `app.py` | you | `APP`: the URL, start command, source paths, API discovery and page hooks. The only place the mole learns about this app. |
| `features/` | you | One module per feature: sub-features and scenarios, registered in `features/__init__.py`. |
| `flows/`, `pages/`, `components/` | you | Reusable user steps, page objects and widget helpers (dropdown, table, modal) the scenarios call. |
| `checks/` | you | Named checks. Each declares the evidence it needs. |
| `adapters/` | you | Evidence sources beyond the browser: database and logs. |
| `features/surfaces/` | you | One adapter per surface. Turns a call into that surface's wire details and returns one shape. |
| `.github/skills/verify-mole/` | you | The agent skill and one map per feature. |

## Concepts

- A **feature** groups **sub-features**; a **scenario** is `feature.sub-feature.scenario`: Given, When, Then, written in Python by the builder, proved on {{SURFACES_TEXT}}.
- A scenario is **steps** (flows, page and component calls) and **checkpoints**. Each **check** declares the **evidence** it needs (screenshot, network log, API response, database, logs) and passes only when every declared source is cited and on disk.
- A failing or erroring step stops the scenario: later steps are `not_reached`; the other checks in the same checkpoint still run.
- A **receipt** per scenario is PASS, FAIL or ERROR (exit 0, 1, 2), with the revision, steps, checks with hints and evidence paths. Latest receipts are in `proof/.runs/receipts/latest/`, history beside them.
- The **revision** is `git HEAD` plus a hash of uncommitted changes under `APP.source_paths`. A stale build makes `run` refuse, and a revision change mid-run is an ERROR.

## Run it

Run every command from the repository root.

```bash
python3 -m pip install -r proof/requirements.txt
python3 -m playwright install chromium   # once
{{MOLE}} up --start      # own terminal: runs the app, waits until it is ready, opens Chrome
{{MOLE}} up              # or attach to an app you already run (--url for another URL)
{{MOLE}} doctor          # is this instance worth driving?
{{MOLE}} features        # feature, sub-feature and scenario ids; --changed: only features your edits touch
{{MOLE}} run             # every scenario; give feature, sub-feature or scenario ids to narrow it
{{MOLE}} flow <id>       # run one flow to explore a state
{{MOLE}} receipts        # latest verdicts, STALE when the source moved on
{{MOLE}} down            # stop what up started
{{PROVE}}                # the same run in a throwaway browser against a running app
{{TEST_PROOF}}           # maps and registry in step; your adapter tests
{{TYPECHECK_PROOF}}
```

`{{MOLE}} help` lists every command. The agent loop is in [.github/skills/verify-mole/SKILL.md](../.github/skills/verify-mole/SKILL.md).

## Add a scenario

1. Write the map in `.github/skills/verify-mole/features/<feature>.md` (four sections; one `(sub | scenario): **Given** … **When** … **Then** … **Proof** check (Evidence labels)` line per scenario; update `features/README.md`).
2. Add the flows, page and component calls it needs under `flows/`, `pages/`, `components/`; add checks under `checks/` with their evidence.
3. Write `features/<feature>.py` with the builder and register it in `features/__init__.py`.
4. Run `{{TEST_PROOF}}`, then `{{MOLE}} run <feature>.<sub-feature>.<scenario>`.

Environment: `PROOF_URL` (app URL), `PROOF_API_URL` (API base URL), `MOLE_DIR` (isolates a second mole instance); a `.env` at the repository root is read too. Receipts and artifacts go to `proof/.runs/` (gitignored). Needs Python 3.10 or newer and Linux or macOS.
