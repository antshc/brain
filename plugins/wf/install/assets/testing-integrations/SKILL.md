---
name: testing-integrations
description: >-
  Pick the minimal seam to test the current repo (DB or cloud component tests, functional slice on mock, real cloud, local app via REST or GUI) and prove it with evidence. Use for 'integration test', 'functional slice', 'flaky test', 'reproduce a bug', or 'regression test'.
---

# testing-integrations

Integration-test orchestrator. Discover repo facts, pick a **kind** (what runs) and optional **strategy** (how to test), prove with evidence.

**Args start with `help`** → follow [help.md](help.md) before anything else: `help` alone prints usage examples (no Discover); `help <request>` offers 3 reasoned options to test the request and runs nothing.

## Actions

*Load and follow the `principles` skill to load indexed engineering principles by name*. Pass action, claim, boundary and available runtime facts. Select `Test behavior, not implementation` for assertions, `Prove it works` for execution/reporting and `Explain the number` for speed claims. Select remains read-only; estimated costs stay labelled estimated, and existing commands remain preferred.

Default → Discover, Choose the kind — ladder, Route, execute and Report. Explicit `select <claim>` or **Select** → read-only selection below; **Run selected** → execute the supplied selection after checking applicability. Neither action invokes Prove or builds throwaway probes; unknown behavior returns to the caller.

| Input | Meaning |
|---|---|
| Claim/criteria, boundary | Expected behavior and the real mechanism the selected check must exercise. |
| Target and roots | Pinned revision/dirty inputs, original launch/harness root (`@repoRoot`), explicit source/proof checkout. |
| Discovery/runtime | Fresh cited `suites`, commands, available services, environment/version and readiness facts; inspect gaps/stale facts only. |
| Limits/output/ownership | Permitted scope/resources, report destination or inline, writable checkout and cleanup owner. |

## Select

1. Apply Discover read-only, reusing supplied facts and roots. Inspect docs/config/fixtures to establish available suites and assertions; do not run tests or state-changing preflight. Done when candidate commands and prerequisites have sources or explicit unknowns.
2. Exclude candidates that cannot decide the claim: identify real versus mocked boundaries; a fake/emulator cannot settle absent provider behavior. Compare remaining candidates by total time to deciding evidence, including build, startup/provisioning and repeats. Prefer ready local infrastructure when sufficient. Use the ladder as default ordering; select a higher ready seam when demonstrably cheaper overall. Label measured versus estimated costs; do not benchmark every candidate. Done when the fastest sufficient candidate and rejected faster alternatives have reasons, or none is suitable.
3. Return inline or to the supplied destination: status (`selected | no suitable test | blocked`), kind/rung, suite/test or runtime scenario, exact command/working directory, narrowest filter, environment, prerequisites, cited command source, speed rationale, boundary coverage/limits, target identity and reusable discovery. Missing prerequisites → blocker and exact next check, not an invented run. Select makes no changes, installations, account changes, provisioning or cleanup. Done when the caller can authorize/run the selected check or see what prevents it.

## Run selected

Check supplied selection against claim, target, suite/config and environment. Reuse valid discovery/selection; stale facts → Select again. Execute only the selected kind, without adding diagnosis/fix or adversarial strategies. Preserve the explicit checkout, filter, output and cleanup ownership; apply existing Autonomy and Cloud Safety gates. Do not replace its assertions with success-exit checks or infer success from zero collected tests. Stop with required observation/blocker when unknown behavior prevents a valid assertion. Report actual results per Completion criteria and Report; preserve caller-owned runnable state until coordinator verification and declared follow-up finish. Done when observation and leftovers/retention are explicit.

## Discover (automatic, always first)

Repo facts come from the repo, never from this skill. Reuse caller-supplied discovery for the same checkout/revision/environment; inspect only missing or stale facts before selection/execution. The caller may supply the original launch/harness root and an explicit source/proof checkout; preserve both rather than inferring them from worker CWD.

1. Preserve caller-supplied `@repoRoot` (original launch/harness root) when present; otherwise set it to the output of `git rev-parse --show-toplevel`, run from the agent session's launch folder, not the current CWD. Resolve every path below from `@repoRoot`. **MUST NOT** re-resolve `@repoRoot` from a git worktree or nested repo (e.g. code repo under `workspace/`) after a `cd`; those are code roots named by repo instructions, not the Discover root.
2. Read repo agent instructions first (`AGENTS.md`, `.github/copilot-instructions.md`, path-scoped instructions): they name the code root, build root, and safety rules.
3. Scan root-level `*.md` and `docs/` for prose describing **how to run integration tests**, **testing framework**, **functional / E2E tests**, and **how to run the project locally** (local instance, stack, compose, emulator, mock). Prefer a dedicated integration-testing doc when present; fall back to `README*` run sections, then test projects, build scripts, compose files, CI pipelines.
4. Scan repo skills (`.github/skills/`, `.claude/skills/`, `.agents/skills/`) and user skills for ones that run tests, start the local stack, or run the cloud CLI against dev/test account profiles. Record their names; invoke them by name later, do not copy their content.
5. Build the `suites` table (one row per suite, plus one `localInstance` row) and keep it in context:

| Field | Meaning |
| --- | --- |
| `suite` | test project / scope |
| `environments` | local (mock, emulator, docker, in-process) and cloud variants; how selected (env var, flag, config) |
| `runFrom` | working directory for commands |
| `preflight` | readiness checks (docker, creds, artifacts) |
| `filter` | syntax for one test, ticket/trait, area, smoke |
| `run` | exact command per environment; scripts + args |
| `overrides` | where per-run settings live |
| `results` | summary / report location |
| `cloudAccount` | doc or skill that names the dev/test account profile and region |
| `localInstance` | doc or skill that runs the app locally: start, health/status, endpoints, logs, stop, drive tools (API / UI scenarios) |
| `level` | ladder rung: component-db / component-cloud / functional-slice / local-runtime |
| `gotchas` | documented traps |

**Done when:** every field is filled from a cited file, or marked `unknown` with the files checked. Unknown `run` or `environments` → read the test project and its fixtures before proceeding; never invent commands.

## Choose the kind — ladder

Default runs use the minimal seam that reproduces the problem or covers the regression; stop at the first sufficient rung. Select compares total time across sufficient candidates; Run selected preserves that choice.

1. **component — database.** Accessor/repository integration test against the local DB emulator. Existing test, or update/add one to reproduce.
2. **component — cloud.** Cloud SDK/proxy integration test against the dev account. Runs without approval (single narrow filter, fixtures self-clean). Existing test, or update/add one.
3. **functional-slice — mock / fake config.** Integration testing framework run: the test project starts its own mocked platform with fake configuration and asserts end to end through the public API. Fast. Not the local app instance.
4. **functional-slice — in-process / real SDK.** Same integration testing framework tests; the framework hosts the app in-process and makes real SDK calls. Still a test run, not the local app instance.
5. **functional-slice — real environment.** Integration testing framework E2E test that either creates a real instance in the dev account, or targets an existing real deployment; cost + cleanup.
6. **local-runtime — REST API.** Only when real user behavior must be shown on a running app; drive the REST API.
7. **local-runtime — web GUI.** Last: only when the behavior is UI-only or the user-visible GUI outcome is the question.

No suitable test or unknown expected behavior → return the missing observation and next check to the caller. Do not invoke Prove or create throwaway probes.

**Select autonomously.** Never ask the user which rung, kind, environment, suite, or test scope to use: walk the ladder, pick the lowest rung that can show the behavior, and the narrowest filter (single test; for several matching tests, the cheapest one that proves the behavior) that answers the request. Ask only when the request itself is unintelligible, or for the safety confirmations in **Autonomy**. Widen scope only on user request.

State the chosen rung and why each lower rung cannot show the behavior. **Done when:** rung + one-line reason per skipped rung written.

## Route

Pick one **kind** via the ladder, then add a **strategy** when the task asks for one. Kind + strategy combine: e.g. reproduce on component, regression on functional-slice.

### Kinds (what runs)

| Kind | Seam | Playbook |
| --- | --- | --- |
| component | One accessor/adapter against its real dependency: DB emulator or cloud SDK. Smallest seam. | [kinds/component.md](kinds/component.md) |
| functional-slice | Integration testing framework: test project owns and starts its environment (mock / fake config / in-process / real cloud: new instance or existing deployment) and asserts end to end through the public API. Distinct from local-runtime. | [kinds/functional-slice.md](kinds/functional-slice.md) |
| local-runtime | Separately started local app instance (local stack) exercised like a user, no test framework: REST API first, web GUI last. | [kinds/local-runtime.md](kinds/local-runtime.md) |

### Strategies (how to test)

| Strategy | Use when | Playbook |
| --- | --- | --- |
| reproduce | Failing or flaky test / behavior → red, root cause, green | [strategies/reproduce.md](strategies/reproduce.md) |
| regression | Area / category / full run before merge or release; report delta vs baseline | [strategies/regression.md](strategies/regression.md) |
| (none) | Single run of the kind | — |

`help` / `help <request>` → [help.md](help.md).

## Principles

- **Minimal seam first.** Follow the ladder; a lower rung with a real assertion beats a higher rung with a manual check.
- **Update tests to reproduce.** No test shows the problem → update or add one at the lowest rung that can; it stays as the regression guard.
- **Repo docs win.** Commands, env vars, filters, and settings come from Discover findings; cite the file for each command you run.
- **Config in force is what the run uses.** Per-run config files and script args beat defaults read in source.
- **One run, one question.** Narrowest filter that answers it; widen only after it passes.
- **Never by hand.** Use repo scripts and test projects; no ad-hoc replacements.

## Autonomy

- Just run: local environments (DB emulator, mock, in-process, local app), read-only cloud calls (identity, list, describe).
- Just run: rung 2 (component — cloud) test runs on the dev/test account, narrow filter, excluding `CleanUp` categories. Still do **Cloud Safety** steps 1–2 and 4–5 (account check, preflight, leftover report).
- **MUST** confirm first: rung 5 real-environment runs (cost, leaked resources), cloud writes outside a rung 2 test run, cleanup deletes, `sudo`. Cloud steps: **Cloud Safety**. The confirmation is a single go/no-go on the already-chosen run (account, region, command, cost); do not bundle rung, scope, or environment questions into it.
- Long runs (cloud, full regression) → extended timeout or monitored background process; never assume completion from silence.

## Cloud Safety

Shared by every kind that touches a real cloud account. Each step has a checkable completion.

1. **Resolve account.** Use `suites.cloudAccount` from Discover. Find and follow the repo or user skill / doc that runs the cloud CLI against dev or test account profiles; take profile, account ID, region, test networks from it. Never guess a profile. **Done when:** identity call (e.g. `aws sts get-caller-identity --profile <p>`) returns the expected account.
2. **Preflight.** Creds, image / artifact IDs, accounts files, deployment URL, required env vars per `suites.preflight`. Resolve missing IDs via repo scripts named in docs. **Done when:** every input present.
3. **Confirm.** Show account, region, command, expected cost/duration, resources that may be created or changed. **MUST** get explicit confirmation, except rung 2 (component — cloud) test runs, which skip this step. **Done when:** confirmed, or skipped for rung 2.
4. **Run long.** Extended timeout or monitored background process; record start time and run identifiers (name prefixes, tags). **Done when:** process exited.
5. **Clean up.** List resources created by the run (tag / name / start time) via the cloud-account skill. Leftovers → show list, confirm, delete; or the repo's documented cleanup suite on request. Existing shared deployment → verify only test data was added and remove it if the repo documents how. **Done when:** leftovers `none` or reported with IDs.

Read-only calls (identity, list, describe) and rung 2 test runs skip step 3.

## Completion criteria

- component / functional-slice test run: command exited **and** total / passed / failed summary read and reported, with environment, filter, results path.
- local-runtime: evidence artifact (response, receipt, screenshot, log line, CLI output) captured for each claim.

Exit code alone, environment startup, or appliance creation is not completion.

## Report

- Kind + strategy, environment, filter, command (cited source doc)
- Test runs: total / passed / failed / skipped; failing test names + first assertion or exception line; results path
- local-runtime: what was exercised, evidence paths or quotes, stack state (stopped / kept)
- Cloud runs: account + leftover resources, or `none`

## Gotchas

- Scoped search empty ≠ absent; re-scan unscoped within `@repoRoot` before reporting a suite or doc missing.
- CWD drifts after `cd` into a worktree or nested repo; `git rev-parse --show-toplevel` there returns that sub repo, hiding launch-folder docs and skills. Keep the launch-folder `@repoRoot`.
- `sudo` resets env; repo env vars (accounts files, selectors) vanish. Use the normal user; if forced, `sudo -E`.
- Scripts that `cd` relative to `$0` break when invoked via relative path; call them by absolute path.
