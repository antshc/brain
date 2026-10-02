---
name: prototype-cloud-scenario
description: Draft a cloud scenario reproducing a bug as a throwaway LightBDD.XUnit3 .NET 10 file-based C# script on isolated AWS or Azure test resources, never the real application, then run and self-correct it until the symptom reproduces and a fix validates. Use to simulate, reproduce in the cloud, or write a test scenario for an escalation.
disable-model-invocation: true
---

# Diagnosis Cloud Scenario

Goal: one **working** scenario — every stage run on isolated cloud test resources, every **Expected:** met. Simulate the cheapest behavior that still exercises the bug's mechanism, not the full flow.

Two phases: **Draft** — agent drafts the runnable scenario and scenario code from codebase + official provider docs, user reviews open choices (HITL), agent re-explores after each answer; **Run** — execute stages, auto-correct on failure, re-run until working.

**Write-through:** scenario file, log, and `{{scenarioSlug}}.cs` are saved to disk as each section, stage, or correction happens — before the next action, never batched to the end. Never invent a resource name, flag, setting, or expected result not traceable to user input, ticket/summary doc, real source/IaC, or official provider docs.

**Codebase is read-only:** **MUST NOT** edit source/IaC or fix the bug in code — only the scenario file, log, and scenario code are written. Apply remediation acts on scenario test resources only; a needed code fix → Open item.

**Isolated from the real application:** **MUST NOT** run, invoke, deploy, or modify the real application instance or any of its resources (roles/policies, VMs, volumes, queues, functions, app-level IDs) — even when the request describes the real flow or names real IDs. Treat that description as the behavior to simulate: every target is a `scenarioTag`/`prereqTag` test resource, and the application's actions are reproduced by CLI, or by a throwaway C# scenario file using the cloud SDK NuGet packages the codebase already uses, mirroring the code's exact operations, parameters, and ordering.

## Location

`scenarioSlug :=` short kebab-case name of the simulated scenario; prefix ticket id when one exists.

| File | Path | Template |
|---|---|---|
| Scenario | `repository root/tmp/{{scenarioSlug}}/{{scenarioSlug}}-scenario.md` | `templates/scenario.template.md` |
| Log | `repository root/tmp/{{scenarioSlug}}/{{scenarioSlug}}-log.md` | `templates/scenario-log.template.md` |
| Scenario code | `repository root/tmp/{{scenarioSlug}}/{{scenarioSlug}}.cs` | `templates/script-app.template.cs` (Shape A for rungs 2–4, Shape B for rung 1) |

Resolve `templates/` from this skill's base directory.

## Inputs

| Input | Required | Effect |
|---|---|---|
| Symptom | yes | Red signal the symptom check asserts |
| Root cause / mechanism | no | Narrows Resource map |
| Workaround / fix option | no | Present → add Apply remediation + Validation; absent → reproduce-only |
| Ticket / summary doc | no | Real resource names → Ticket analog only, evidence, fix-option caveats |
| Existing scenario file | no | Present → skip Draft; Run as next run |

Accept any mix of free text/docs. Ask only when symptom missing; existing scenario file supplies it.

## Sources

- **Codebase:** only through the `Explore` subagent — read-only lookups returning `path:line`; semantic/symbol search, not text search alone. Discover the scenario under diagnosis itself from code: entry point (API handler, job, event consumer, workflow, script) and the ordered steps and SDK calls that lead to the symptom. Resources and their settings may come from IaC (Terraform, CloudFormation, CDK, SAM, Bicep/ARM, serverless config) **or** from application code calling cloud SDKs at runtime (create/update/attach/delete calls, request parameters, config/env-driven values, scripts, workflows); trace both. Code missing → ask path.
- **Cloud provider:** verify every operation's semantics, CLI subcommand/flag, default, limit, and consistency behavior against official provider documentation — AWS Documentation (AWS Documentation MCP) for AWS, Microsoft Learn (Microsoft Learn MCP) for Azure; cite the canonical URL in the scenario file. CLI `--help` confirms flag syntax only.
- **User:** decisions only; never ask for a fact the codebase or provider docs supply.

## Cloud CLI

Use target cloud's own CLI: `az` (Azure), `aws` (AWS). Load existing aws/azure cloud skills for environment info. For stages run as manual CLI (Preflight, Prerequisites, Cleanup, or a rung-1 single-call check), find exact subcommand/flags per Sources (create from image vs. raw/imported source, attach/detach volume, swap boot volume, stop/start, console/boot output, teardown, …); check against the real code path from the mechanism. Command names differ per cloud — never copy across.

## Fidelity ladder

Pick **lowest** rung preserving every load-bearing setting in Resource map; every rung runs against test resources only:

1. Single SDK/endpoint call with code's exact operation + parameters — plain .NET 10 file-based top-level-statements script, no LightBDD/xUnit.
2. Broken end-state built directly via one or more SDK calls — LightBDD Basic scenario, `Given`/`Then` only.
3. Scenario code replaying code's exact operation(s) in order — LightBDD Basic scenario, full stage list.
4. Scenario code simulating the Scenario flow — the application's steps, ordering, loops, timing — via the SDK.

Climb only when lower rung drops/changes a load-bearing setting, operation type, or ordering/timing the bug needs. Load-bearing settings = production exactly; rest = smallest/cheapest (size, count, storage, region unless region matters). Rung choice is a `❓` in Draft until the user confirms it.

## Scenario code

One throwaway `{{scenarioSlug}}.cs`, built from `templates/script-app.template.cs` — a .NET 10 file-based app (`#:sdk`/`#:package`/`#:property` directives, run with `dotnet run {{scenarioSlug}}.cs`). The template holds two shapes; keep the one matching the chosen rung and delete the other. Shape B (rung 1) has no LightBDD/xUnit; Shape A (rungs 2–4) uses `LightBDD.XUnit3` Basic scenarios (`Runner.RunScenario(...)`/`RunScenarioAsync(...)` with parameterless step methods, never lambdas).

**Stages** (Shape A, rungs 2–4), in order, each a step method:

1. **Build broken state** (`Given`) — create/mutate the resource into the broken end-state.
2. **Reproduce** (`When`/`Then`) — exercise the mechanism; `Then` asserts the symptom via a shared read helper.
3. **Apply remediation** (`When`, optional) — only with a fix option under test.
4. **Validation** (`Then`, optional) — same read helper, asserts the symptom is gone.

Preflight and Prerequisites run either as code before the `Runner` call (e.g. in the `LightBddScope` subclass) or as manual CLI — Draft marks the choice `❓` per item. Cleanup never runs automatically: it is manual CLI or a separate code path, outside the `[Scenario]`, behind a confirmation gate.

**Code shape:**

- The `[Scenario]` method comes first in the feature class; its body is only the ordered list of step names, so the stages read top-down.
- `#region Packages` — the `#:package`/`#:property` directives. `#region Usings` — `using` directives. `#region Implementation` — fields, step methods, helpers. Shape B (rung 1) uses the same three regions around its top-level statements and local functions.
- Keep only code that proves or disproves the assumption under test; delete anything that doesn't change the verdict.
- **MUST NOT** add production abstractions, layers, DI, interfaces, or reusable infrastructure, unless the experiment's mechanism needs one — state the reason in a `// @:` one-line comment when it does.
- Every value comes from `Target environment` variables, never literals. Every create is tagged `scenarioTag`. Each SDK call carries a `// path:line` comment citing the mirrored code. No import from the application codebase.

## Packages

Discover the cloud SDK package IDs and versions from the codebase (`PackageReference` in `*.csproj`, `Directory.Packages.props`) — never hardcode a package or version. Pin with `#:package Id@Version`; omit `@Version` only under central package management. Codebase isn't .NET → ask the user for the SDK/package set.

**`LightBDD.XUnit3`/`xunit.v3` pairing:** resolve the latest `LightBDD.XUnit3` version, read its `.nuspec` (nuget.org `v3-flatcontainer` or local cache) for its exact `xunit.v3.extensibility.core` dependency version, then pin `#:package xunit.v3@<that exact version>` — the full `xunit.v3` meta-package, not a newer one. A newer `xunit.v3` resolves a newer `xunit.v3.extensibility.core` transitively and breaks `LightBDD.XUnit3` at runtime (`TypeLoadException`). `TestPipelineStartupAttribute` needs `using Xunit.v3;`.

## Scenario log

Problem log rendered from `templates/scenario-log.template.md`.

- One log per scenario: `## Draft`, then one `## Run {{runNumber}} — {{date}}` section per run, appended. `runNumber :=` last Run history run + 1 (first → `1`).
- Content: only problems faced and their solutions, as `**Problem:** … → **Solution:** …` bullets; blocked → `**Unblocker:**` instead of Solution.
- Group bullets under `### <stage name>` (Preflight, Prerequisites, Build broken state, Reproduce, Apply remediation, Validation, Cleanup) when the problem belongs to one; omit stages without problems.
- Write each bullet once the problem is solved or blocked, before the next action. Stage verdicts go to Run history, not the log.

## Draft

Goal: a runnable scenario — every stage with exact commands/code and **Expected:** — drafted by the agent, confirmed by the user. **MUST** finish Draft (step 5 passed) before any cloud call, Preflight included.

1. **Gather facts** per Sources; ask nothing yet:
   - **Target cloud** from input site/platform info; ambiguous → ask before drafting; never mix clouds.
   - **Scenario flow** (optional; skip when no product flow is found in code or it is one SDK call): symptom → entry point → ordered steps and SDK calls in the product that produce it, incl. branches/conditions taken; written as Given–When–Then one-liners. *Done when* every code keyword links to its source as [`keyword`](path#Lline) and the symptom line is marked.
   - **Resource map**: per SDK call on the symptom's code path (from Scenario flow when present) (service + operation + request parameters) → where the resource and its settings are defined (IaC, or the SDK call itself when code creates/mutates it) → applied settings. *Done when* each row has resource, definition `path:line` (IaC or SDK call), caller `path:line`, SDK op, CLI op, load-bearing settings.
   - **Mechanism**: exact creation semantics of the operation under test — operation type (e.g. import-from-source vs. create-from-image), which branch sets which properties. *Done when* "must match the real code path" section cites file + line range, provider doc URL, and why a naive alternative command diverges.
   - **Packages**: resolve per Packages. *Done when* every SDK/LightBDD/xUnit package has an id + version cited to its source.
   - **Tagging convention**: the tag key(s) the codebase/IaC already applies to resources (e.g. `Name`, `Project`, `Owner` in Terraform/CloudFormation/SDK calls) — reuse that key for `scenarioTag`/`prereqTag` values. None found → fall back to `dig-scenario={{scenarioSlug}}`/`dig-scenario-prereq={{scenarioSlug}}` and mark it `❓`. *Done when* the key is cited to its source or marked `❓`.
2. **Draft the scenario**: write every section below into the scenario file, choosing each value yourself from facts; cite `path:line` or provider doc URL per choice. A choice facts cannot settle → pick the safest/cheapest default and mark it `❓` inline. *Done when* every section is filled and every unconfirmed choice carries `❓`.
   1. **Scope** — symptom reproduced; real application excluded; unfixed root cause excluded, naming its tracking ticket; fix option under test or reproduce-only.
   2. **Fidelity** — apply Fidelity ladder; name rung + load-bearing setting the rung below breaks; always `❓` until the user confirms it.
   3. **Stage list** — Preflight, Prerequisites (each `❓` code-or-CLI), Build broken state, Reproduce, Apply remediation + Validation (only with fix option), Cleanup (CLI or separate code path, never in the `[Scenario]`).
   4. **Target environment** — variable block: account/subscription, resource group/equivalent, region, image, size, `scenarioTag`, `prereqTag` (values per Tagging convention); non-load-bearing values minimal; stages read these, never literals.
   5. **Naming convention** — test resource → ticket analog → role; names mirror real ones so stages read like the incident; every later-named resource appears here first.
   6. **Prerequisites** — reusable resources needed but not exercised, created once, reused across runs (e.g. bucket/container stages write blobs to; network, base image, key pair). Qualifies only if no setting is load-bearing and no stage mutates its settings; else per-run resource. Each: idempotent ensure (exists check → create if missing), tagged `prereqTag`, settings check vs. Target environment.
   7. **Symptom check** — the `Then` step (or, rung 1, the exit code + printed signal line) asserting the user's exact symptom, reused by Reproduce and Validation.
   8. **Scenario code**: write `{{scenarioSlug}}.cs` from `templates/script-app.template.cs`, keeping only Shape A (rung 2–4) or Shape B (rung 1) per Scenario code and Packages; `dotnet build {{scenarioSlug}}.cs` must succeed. **MUST NOT** `dotnet run` or touch the cloud in Draft. The scenario md links to the file and lists its stages/steps with **Expected:**; it never embeds the code. Manual-mode Preflight/Prerequisites get exact CLI commands + **Expected:** instead.
   9. **Cleanup** — delete every per-run resource in target cloud's real dependency order (e.g. detach NICs before deleting the SG/NSG they reference), incl. data left in prerequisites (e.g. test blobs); then leftover query on `scenarioTag`. Prerequisites stay; separate **Prerequisite teardown** runs only on user request. Mark both **destructive — requires explicit confirmation before running**. Account/resource group untouched unless input asks.
3. **Review with the user**, in rounds:
   - Show the draft paths (`.md` and `.cs`) and a short summary: scope, fidelity rung, stage list, resources to be created.
   - Ask every `❓` choice as a numbered question with options, your recommended answer, and its citation. Ask a choice that depends on another open one in a later round.
   - Ask only decisions; never ask a fact Sources can supply.
   - After each answer round, **re-explore before editing**: run Gather facts again for whatever the answers touch (new resource, branch, operation, region, setting) and verify affected commands/code per Sources; then update affected sections, remove resolved `❓`, and log a Draft problem bullet when an answer invalidated a drafted choice.
   - *Done when* no `❓` remains and the user confirms the draft.
4. **Caveats + Open items**: fix option's documented limitations → Caveats; choices the user deferred, needed code fix → Open items. *Done when* no overlap and no caveat resolvable now.
5. **Check** draft against Quality Check.

## Run

Loop run → auto-correct → re-run until working.

1. Draft not finished → stop, finish Draft first. Existing scenario file → read whole, append `## Run {{runNumber}} — {{date}}` to log, re-check Quality Check.
2. Show Preflight output + resources Prerequisites/Build broken state will create (existing prerequisites reused, not listed); get **explicit confirmation before the first create**, then `dotnet run {{scenarioSlug}}.cs` with Target environment exported.
3. Record each stage's result as a Run history row tagged `runNumber`, as it completes.
4. On failure, auto-correct: save fix to `{{scenarioSlug}}.cs` and/or the scenario file in place + log problem/solution bullet under current run/stage **before** re-running; re-run from earliest invalidated stage:
   - Command/compile error (wrong flag, missing dependency, async unfinished) → fix it, verified per Sources.
   - Reproduce stays green / shows different symptom → re-check Resource map, then climb one rung.
   - **MUST NOT** rewrite **Expected:** or the symptom-check step to match observed output without user agreement.
5. Repeat 2–4 until Done.
6. Get explicit confirmation, run Cleanup, save leftover query result to Run history; leftovers → log problem bullet.

*Done when* Reproduce red with user's exact symptom, Validation (if present) green, Cleanup leaves no `scenarioTag` resources, Status `Working — verified {{date}}`. Unresolvable → log `**Unblocker:**` bullet, Status `Blocked — {{reason}}`, stop.

## Revise

User correction → save edit to `{{scenarioSlug}}.cs` and/or the scenario file in place + log problem/solution bullet (current run/stage, or Draft) before any cloud call, then re-run from earliest invalidated stage (with create/cleanup confirmations), update Run history. *Done when* Run Done holds again.

## Gotchas

- Long-running ops return early → poll before verifying.
- IAM/RBAC assignments and tags eventually consistent → retry before concluding red/green.
- CLI region/account/subscription default from active profile → pass explicitly from Target environment on every command; the `.cs` reads the same variables.
- Tag/label indexes lag deletes → re-query before declaring leftovers.
- Request names a real app action or ID → simulate, never apply: build test analogs (role, resource, tag/ID), apply the action to them, reproduce the app's calls in `{{scenarioSlug}}.cs`, assert the symptom on test resources only.
- A file-based app under `tmp/` inherits any `Directory.Build.props`/`Directory.Packages.props`/`global.json`/`nuget.config` from parent folders.
- `dotnet test` does not run file-based apps; use `dotnet run {{scenarioSlug}}.cs`.
- Basic scenario step methods can't be lambdas or take parameters.
- Concurrent `dotnet run` on the same file collides on the build cache — `dotnet build` once first.
- A newer `xunit.v3` than the one `LightBDD.XUnit3` was built against resolves anyway (NuGet floats to the highest transitive version) and fails at runtime, not at compile time — always pin the exact matching version per Packages.

## Quality Check

- Commands/code name only Naming convention resources; per-run creates apply `scenarioTag`, prerequisites `prereqTag`.
- No prerequisite load-bearing or mutated by a stage.
- Resource map + mechanism cite real source/IaC, not input prose alone; provider-behavior claims cite canonical doc URL.
- No `❓` left; every agent-chosen value confirmed by the user in Review.
- Fidelity choice justifies rejecting lower rung.
- Reproduce + Validation share the symptom-check step; every **Expected:** checkable from output.
- Cleanup follows target cloud's real delete-dependency order.
- Every create/delete behind its confirmation gate.
- Scenario file matches what was actually run; `{{scenarioSlug}}.cs` matches what was actually `dotnet run` — nothing executed that isn't saved first.
- Log holds only problem → solution bullets, grouped by run and stage.
- No command or scenario code call targets the real application or its resources; every target is a Naming convention test resource.
- `{{scenarioSlug}}.cs` has the `[Scenario]` first, the three regions, no production abstraction/DI without a stated reason, and only one Shape kept (the other deleted).
- Packages match the codebase's discovered SDK packages/versions, never hardcoded.
- Scenario md links to `{{scenarioSlug}}.cs`, never embeds its code.
- No source/IaC file changed; code exploration went through `Explore` subagent.
- No unredacted secret or tenant identifier.

