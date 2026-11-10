# GitHub skill tests

Tests for `plugins/wf/skills/github/scripts/` (`github.py`, `github_cli`) and the split `plugins/wf/skills/git/scripts/` (`git.py`, `git_cli`). Read before adding, changing or running them.

## Layout

| File | Covers | Runs |
|---|---|---|
| `test_gh.py` | refs, `Gh` wrapper, pagination, GraphQL, `run_cmd` | in-process |
| `test_git.py` | separate Git CLI: branch, commit, push, fetch, remote identity (real git, bare remote) | in-process |
| `test_issues.py` | issue, label, comment, assignment, sub-issue (fake `gh`) | in-process |
| `test_pulls.py` | PR open, snapshot, diff, fetch, checkout, checks, comments | in-process |
| `test_specs.py` | design spec, issue artifacts | in-process |
| `test_reviews.py` | inline findings, reply, resolve, discussion gate | in-process |
| `test_worktrees.py` | separate Git CLI: worktree lifecycle and ownership (real git) | in-process |
| `test_implement_spec_units.py` | validation, PR body, checkout resolution, close, evidence, checkpoint, planner graph | in-process |
| `test_cli_routing.py`, `test_cli.py` | two entry points, routing, exit codes, repo read/search | in-process |
| `test_*_integration.py` | the same commands against the real `antshc/brain` | live, gated |

`tests/wf/implement/` (spec flow) and `tests/wf/review/` (discussion marker routing) also cover this code; do not duplicate them.

## Run

In-process, always, after any change to the scripts:

```
python3 -m pytest tests/wf/github -q -m "not integration"
python3 -m pytest tests/wf/github -q -m "not integration" -n auto   # parallel (pytest-xdist)
```

Live, only when a risk below applies. Without `BRAIN_GH_LIVE` every live test is skipped:

```
BRAIN_GH_LIVE=pulls python3 -m pytest tests/wf/github -m integration -n 4 -q
BRAIN_GH_LIVE=issues,specs python3 -m pytest tests/wf/github -m integration -n 4 -q
BRAIN_GH_LIVE=all python3 -m pytest tests/wf/github -m integration -n 4 -q
```

`python3 .github/scripts/run-python-tests.py --unit-only` skips every `*_integration.py` file.

## Discover the risk before going live

Run the in-process suite first. Go live only for a risk the fake cannot prove, then select the narrowest area.

| Change touches | Risk the fake cannot show | `BRAIN_GH_LIVE` |
|---|---|---|
| REST path, query string, payload, `--paginate`/`--slurp`, API version header in `issues.py`, `pulls.py`, `reviews.py`, `specs.py`, `implement_spec.py` | endpoint or field GitHub rejects or shapes differently | the area of the module |
| GraphQL text in `reviews.py` | schema, thread fields, mutation names | `pulls` |
| `gh` flags or output parsing (`pr diff`, `pr checks`, `issue artifact`, `label`, `search code`) | CLI version drift | `pulls`, `issues`, `specs`, `repo` |
| idempotent create or reconcile logic | read-after-write lag (label-filtered lists lag 2-4 s) | `issues`, `specs` |
| push, fetch, remote URL checks, credentials in `git_cli/branches.py` | real transport and auth | `pulls`, `repo` |
| `github_cli/gh.py`, `github_cli/cli.py` GitHub helpers | GitHub surface | `all` |
| `git_cli/core.py`, `git_cli/cli.py` Git helpers | Git operations | local Git tests first; `repo`/`pulls` live only for auth or transport changes |
| docs, tests only, pure validation in `implement_spec.py`, `worktrees.py` | none | skip live |

Areas: `repo` (read-only), `issues`, `specs`, `pulls`. Report which area ran and why; report a skipped live run as not run.

## Parallel design (mandatory)

Every test must pass alone, in any order, on any xdist worker.

- In-process: build state from `tmp_path`, the `fake`/`repo` fixtures and `run`. No module-level mutable state, no fixed ports or paths, no reliance on test order.
- Live: each xdist worker is its own session, so `run_id` is unique per worker. Name every resource with `ident(run_id)`; never reuse a name across tests.
- Live: no module- or session-scoped fixture may create a resource that a test mutates or lists. Create it per test (`label`, `live_branch`, `live_pr`, `spec_graph`).
- Live: schedule deletion the moment a resource exists (`live_issue`, `track_issue`, `cleanup`). The `live` fixture also sweeps issues titled `[<run_id>]` or `<RUN_ID>…` at session end.
- Shared resources are allowed only when idempotent, race-safe and never deleted: `repo:target:antshc/brain`, `repo:base:main` (`routing_labels`).
- Poll GitHub's eventually consistent reads with `eventually(...)`; never `sleep`.
- Cap live workers at `-n 4`: more risks GitHub secondary rate limits on content creation.

## Live safety

- Target is always `antshc/brain` (`LIVE_REPO`); never point live tests at another repository.
- Live tests create issues, labels, `it/<id>` branches and draft PRs, then delete or close them. PRs cannot be deleted: closed `[IT-…]` PRs remain by design.
- After an aborted live run, remove leftovers: `gh api "repos/antshc/brain/issues?state=all&per_page=30" --jq '.[]|select(.title|test("it-|IT-"))|[.number,.title]|@tsv'`, `gh api repos/antshc/brain/branches --paginate --jq '.[].name' | grep '^it/'`, `gh label list -R antshc/brain | grep '^it-'`. Issue list reads lag; verify a deletion with `gh api repos/antshc/brain/issues/N` (410 = gone).
- Push uses the `gh` credential helper through `GIT_CONFIG_*` env in the `live` fixture; do not change global git config.
- A missing `gh`, no auth or no push access skips the live tests; it never fails them. Issue artifacts are a preview API: those tests skip when unavailable.

## Known defects pinned by `xfail(strict=True)`

- `test_diff_split_accepts_a_qualified_short_reference` (pinned and unpinned): `pr diff-split --pr owner/repo#N` passes the short ref to `gh pr diff`, which reads it as a branch name. Only a PR URL works; pinned mode parses the short ref then fails anyway. Remove the marker when fixed.

## Known GitHub behavior the tests absorb

- Label-filtered issue lists lag 2-4 s after a write. `issue create` reconcile and `spec create --profile design` duplicate detection read them, so an immediate retry can duplicate. Live tests wait with `eventually(...)` before asserting dedupe.
- `git push` is occasionally rejected under parallel load; the `live_branch` fixture retries `branch push`, which is retry-safe by design.

## Adding tests

- Cover logic in-process first. Extend `FakeGitHub` in `conftest.py` for a new REST route; stub other `gh` commands with `fake.stub((...), response)`. Git runs for real; `fake.remote_url` makes a local repository look like a GitHub remote.
- Model failure honestly: `fake.fail` (no write), `fake.lose` (write applied, response lost). Assert no write happened with `fake.writes() == []` for guards.
- Add a live test only for behavior GitHub decides. Mark the module `pytest.mark.integration` and `pytest.mark.live("<area>")`; name it `test_<area>_integration.py`.
- Argparse rejects option-like values after a flag; pass them as `--flag=value`.
