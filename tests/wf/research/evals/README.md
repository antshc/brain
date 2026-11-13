# Hunter Explore evaluations

Live routing eval that sends each Explore request directly to Hunter. `scenarios.json` holds each case's Request, `excludedTools`, expected route, and checks; `results.json` holds historical runs from before Hunter owned the procedure. `test_explore_contracts.py` guards the scenario file shape offline; it does not run models.

## Live runner

Needs a workspace with:

- `ARCHITECTURE.md` with a `Deployables` table;
- at least one local checkout under `workspace/`;
- a built `graphify-out/` covering two deployables, `graphify-out/.graphify_python`, and the WF plugin's `research/how/graphify.md` and `research/scripts/focused_query.py`, plus an optional root `GRAPHIFY.md`;
- one Deployables row whose repository has no local checkout (`missing_local_checkout`);
- a restored NuGet dependency with a known member (`nuget_restored_package`).

The runner reads `EXPLORE_EVAL_REPO` (workspace root) and skips when unset. Fill the `scenarios.json` placeholders from that workspace, send each Request verbatim to a fresh Hunter agent with the case's `excludedTools` removed, and classify the transcript with the trace classifier. Copy the classifier from `zic-board/tools/shared/utils/copilot_trace.py` into this folder rather than importing across repositories.

Apply `commonChecks` to every case plus the case's own `checks`. The verdict's first line must match `routeLinePattern` and name the case's `expectedRoute`.

## Recording results

Append one entry to `results.json` `runs` per eval run: label, agent revision, runs per case, cases, and per-model `passing/total`. Historical acceptance for the E1–E6/R1 revision (`SKILL_EVAL_RUNS=3`):

- `gpt-5.3-codex` 12/12.
- `claude-haiku-5.5` ≥ 11/12 with `@shape` sent.
- `claude-sonnet-5` loads the skill on every case.
- No run writes `graphify-out/` outside `cache/`; no `rg` install while `rg` is on `PATH`.

## How orchestration evaluations

`how-scenarios.json` covers discovery, cross-repository evidence, package implementation, terminal/access gaps, provider/data uncertainty, and caller-owned destinations. These complement Hunter routing cases; offline contract tests validate structure, not model behavior.

Run each request in a fresh session with the Research skill and the caller context named in the case. Supply a representative read-only checkout or captured evidence when needed. Apply `commonChecks` plus each case’s checks to the transcript, requested writes, and produced explanation. Record the tested revision, supplied context, outcome, and evidence limits; do not report an unexecuted case as passed. For an Explainer-only check, supply the findings directly and use the bundled Explainer prompt and report contract.
