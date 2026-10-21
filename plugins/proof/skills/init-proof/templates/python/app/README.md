# Proof kit and mole

Drives {{APP_NAME}} like a user, records facts, and writes a receipt with a verdict. It complements the repo's own tests: those assert and stop at the first failure, while a proof records every fact and tells you what to fix.

## Layout

| Path | Owner | What it is |
|---|---|---|
| `kit/` | the kit | The independent proof lib: `types.py`, `surfaces.py`, `features.py`, `receipt.py`, `run.py`. It imports nothing from the app or the mole. Do not edit; an upgrade replaces this folder. |
| `../mole/` | the kit | The runner at the repository root: `mole.py` (CLI), `prove_cli.py`, `runtime.py`, `receipts.py`, `config.py`, `feature.py`, `selftest.py`. It uses the kit, never the reverse. Do not edit; an upgrade replaces this folder. |
| `app.py` | you | `APP`: the URL, start command, source paths, API discovery and page hooks. The only place the mole learns about this app. |
| `features/` | you | One proof per feature, registered in `features/__init__.py`. |
| `features/surfaces/` | you | One adapter per surface. Turns a feature call into that surface's wire details and returns one shape. |
| `.github/skills/verify-mole/` | you | The agent skill and one map per feature. |

## Concepts

- A **feature** is a behavior contract, proved on one or more **surfaces**: `web` (the app in a real Chrome over CDP) and `api` (HTTP). Supported here: {{SURFACES_TEXT}}.
- The **kit** (`proof/kit/`) is a lib: it knows what a proof and a receipt are, and gets the features, surfaces, revision and commands to suggest passed in. The **mole** (`mole/`) is the runner: it starts and drives the app, supplies those, and saves the receipts.
- A **surface adapter** returns the same shape on every surface, so a rule is written once and checked everywhere. `check()` never raises; a check is named `feature/surface: rule`.
- A **receipt** is PASS, FAIL or ERROR (exit 0, 1, 2) with the revision, features, surfaces, checks with hints, `pageErrors` and a screenshot.
- The **revision** is `git HEAD` plus a hash of uncommitted changes under `APP.source_paths`. A stale build makes `prove` refuse.

## Run it

Run every command from the repository root.

```bash
python3 -m pip install -r proof/requirements.txt
python3 -m playwright install chromium   # once
{{MOLE}} up --start      # own terminal: runs the app, waits until it is ready, opens Chrome
{{MOLE}} up              # or attach to an app you already run (--url for another URL)
{{MOLE}} doctor          # is this instance worth driving?
{{MOLE}} prove           # every feature on every surface; --feature, --surface narrow it
{{MOLE}} down            # stop what up started
{{PROVE}}                # the same proof in a throwaway browser against a running app
{{TEST_PROOF}}           # maps and registry in step; your adapter tests
{{TYPECHECK_PROOF}}
```

`{{MOLE}} help` lists every command, including `{{MOLE}} <feature> <verb>` for features with a `drive` hook. The agent loop is in [.github/skills/verify-mole/SKILL.md](../.github/skills/verify-mole/SKILL.md).

## Add a feature

1. Write the contract in `.github/skills/verify-mole/features/<name>.md` (frontmatter: `feature`, `prove`, `touches`, `surfaces`; sections `## Contract` and `## Driving it`; update `features/README.md`).
2. Extend the adapters in `features/surfaces/` with the calls the contract needs, returning one shape per surface.
3. Write `features/<name>.py`: loop over `kit.surfaces`, call the adapter through `observe()`, and `kit.check(name, actual, expected, hint)`.
4. Register it in `features/__init__.py` as a `MoleFeature` with its `surfaces` and `touches`.
5. Run `{{TEST_PROOF}}`, then `{{MOLE}} prove --feature <name>`.

Environment: `PROOF_URL` (app URL), `PROOF_API_URL` (API base URL), `MOLE_DIR` (isolates a second mole instance); a `.env` at the repository root is read too. Receipts and screenshots go to `proof/.runs/` (gitignored). Needs Python 3.10 or newer and Linux or macOS.

## Saved evidence evaluation

Python also supports a separate offline mode. Live `run_proof()`, `mole prove` and `prove_cli` keep their behavior. The offline evaluator accepts reviewed contracts from `proof/tools/contracts.py`; it does not execute the live feature functions or start the app/browser/tests. Define/check contracts before implementing the feature, then collect final-revision observations. See [tools/README.md](tools/README.md) for manifests, trust, adapters and the Order example.

```bash
python3 -m mole evaluate --app app-name --run proof/.runs/run-id \
  --revision FULL_FINAL_GIT_SHA --contract-sha256 REVIEWED_CODE_TREE_DIGEST \
  --manifest-sha256 TRUSTED_COLLECTOR_DIGEST
```

Select contracts with repeated `--feature NAME`. To try the adapted Order example use `--contract-module proof.tools.order_example`. Keep registry keys aligned with live feature names; surfaces stay `web`/`api`, while DB/logs/tasks/tests are evidence sources. Every declared check must be recorded once. Missing/stale/invalid required evidence yields ERROR (2); observed mismatch yields FAIL (1); complete matching evidence yields PASS (0). Receipt/Check JSON stays unchanged; manifest/report details remain companion files. `receipt.json` is latest, `receipts/` retains every evaluation.
