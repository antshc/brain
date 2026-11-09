# research Explore route evaluations

Live routing eval for the `research` skill's Explore route. `scenarios.json` holds each case's Request, `excludedTools`, expected route, and checks; `results.json` holds the baseline scoreboard and post-fix runs. `test_explore_contracts.py` guards the scenario file shape offline; it does not run models.

## Live runner

Needs a workspace with:

- `ARCHITECTURE.md` with a `Deployables` table;
- at least one local checkout under `workspace/`;
- a built `graphify-out/` covering two deployables, and `graphify` on `PATH`;
- one Deployables row whose repository has no local checkout (`github_no_checkout`).

The runner reads `EXPLORE_EVAL_REPO` (workspace root) and skips when unset. Fill the `scenarios.json` placeholders from that workspace, send each Request verbatim to a fresh agent with the case's `excludedTools` removed, and classify the transcript with the trace classifier. Copy the classifier from `zic-board/tools/shared/utils/copilot_trace.py` into this folder rather than importing across repositories.

Apply `commonChecks` to every case plus the case's own `checks`. The verdict's first line must match `routeLinePattern` and name the case's `expectedRoute`.

## Recording results

Append one entry to `results.json` `runs` per eval run: label, skill revision, runs per case, cases, and per-model `passing/total`. Acceptance for the E1–E6/R1 revision (`SKILL_EVAL_RUNS=3`):

- `gpt-5.3-codex` 12/12.
- `claude-haiku-5.5` ≥ 11/12 with `@shape` sent.
- `claude-sonnet-5` loads the skill on every case.
- No run writes `graphify-out/` outside `cache/`; no `rg` install while `rg` is on `PATH`.
