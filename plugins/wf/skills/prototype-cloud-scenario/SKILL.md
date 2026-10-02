---
name: prototype-cloud-scenario
description: Draft a cloud scenario simulating a bug on isolated AWS or Azure test resources, never the real application, from codebase and provider docs, then run and self-correct it until the symptom reproduces and a fix validates. Use to simulate, reproduce in the cloud, or write a test scenario for an escalation.
disable-model-invocation: true
---

# Diagnosis Cloud Scenario

Goal: one **working** scenario file — every phase run on isolated cloud test resources, every **Expected:** met. Simulate the cheapest behavior that still exercises the bug's mechanism, not the full flow.

Two phases: **Draft** — agent drafts the runnable scenario from codebase + official provider docs, user reviews open choices (HITL), agent re-explores after each answer; **Run** — execute phases, auto-correct the scenario on failure, re-run until working.

**Write-through:** scenario file and log are saved to disk as each section, phase, or correction happens — before the next action, never batched to the end. Never invent a resource name, flag, setting, or expected result not traceable to user input, ticket/summary doc, real source/IaC, or official provider docs.

**Codebase is read-only:** **MUST NOT** edit source/IaC or fix the bug in code — only the scenario file, log, and prototype scripts are written. Apply fix acts on scenario test resources only; a needed code fix → Open item.

**Isolated from the real application:** **MUST NOT** run, invoke, deploy, or modify the real application instance or any of its resources (roles/policies, VMs, volumes, queues, functions, app-level IDs) — even when the request describes the real flow or names real IDs. Treat that description as the behavior to simulate: every target is a `scenarioTag`/`prereqTag` test resource, and the application's actions are reproduced by the CLI or a throwaway Python prototype using the cloud SDK (`boto3`, Azure SDK for Python) that mirrors the code's exact operations, parameters, and ordering.

## Location

`scenarioSlug :=` short kebab-case name of the simulated scenario; prefix ticket id when one exists.

| File | Path | Template |
|---|---|---|
| Scenario | `repository root/docs/tmp/{{scenarioSlug}}/{{scenarioSlug}}-scenario.md` | `templates/scenario.template.md` |
| Log | `repository root/docs/tmp/{{scenarioSlug}}/{{scenarioSlug}}-log.md` | `templates/scenario-log.template.md` |
| Prototype | `repository root/docs/tmp/{{scenarioSlug}}/prototype/*.py` | — |

Resolve `templates/` from this skill's base directory.

## Inputs

| Input | Required | Effect |
|---|---|---|
| Symptom | yes | Red signal the symptom check asserts |
| Root cause / mechanism | no | Narrows Resource map |
| Workaround / fix option | no | Present → add Apply fix + Verify; absent → reproduce-only |
| Ticket / summary doc | no | Real resource names → Ticket analog only, evidence, fix-option caveats |
| Existing scenario file | no | Present → skip Draft; Run as next run |

Accept any mix of free text/docs. Ask only when symptom missing; existing scenario file supplies it.

## Sources

- **Codebase:** only through the `Explore` subagent — read-only lookups returning `path:line`; semantic/symbol search, not text search alone. Discover the scenario under diagnosis itself from code: entry point (API handler, job, event consumer, workflow, script) and the ordered steps and SDK calls that lead to the symptom. Resources and their settings may come from IaC (Terraform, CloudFormation, CDK, SAM, Bicep/ARM, serverless config) **or** from application code calling cloud SDKs at runtime (create/update/attach/delete calls, request parameters, config/env-driven values, scripts, workflows); trace both. Code missing → ask path.
- **Cloud provider:** verify every operation's semantics, CLI subcommand/flag, default, limit, and consistency behavior against official provider documentation — AWS Documentation (AWS Documentation MCP) for AWS, Microsoft Learn (Microsoft Learn MCP) for Azure; cite the canonical URL in the scenario file. CLI `--help` confirms flag syntax only.
- **User:** decisions only; never ask for a fact the codebase or provider docs supply.

## Cloud CLI

Use target cloud's own CLI: `az` (Azure), `aws` (AWS). Load existing aws/azure cloud skills for environment info. Per phase, find exact subcommand/flags per Sources (create from image vs. raw/imported source, attach/detach volume, swap boot volume, stop/start, console/boot output, teardown, …); check against the real code path from the mechanism. Command names differ per cloud — never copy across.

## Fidelity ladder

Pick **lowest** rung preserving every load-bearing setting in Resource map; every rung runs against test resources only:

1. Single CLI/API call with code's exact operation + parameters.
2. Broken end-state built directly via CLI.
3. Throwaway Python SDK script replaying code's exact operation(s).
4. Throwaway Python prototype simulating the Scenario flow — the application's steps, ordering, loops, timing — via the SDK.

Climb only when lower rung drops/changes a load-bearing setting, operation type, or ordering/timing the bug needs. Load-bearing settings = production exactly; rest = smallest/cheapest (size, count, storage, region unless region matters).

**Prototype rules:** propose only when CLI commands alone cannot faithfully simulate the behavior — e.g. multi-step ordering, loops/polling, timing or concurrency, reacting to intermediate state, SDK-only parameters with no CLI equivalent; name which one in the proposal. Proposed in Draft as a `❓` question, never written in Draft; scripts written in Run only after the user approved the prototype. `python3`; one script per role (e.g. `simulate_app.py`, `symptom_check.py`); read every value from Target environment variables, never literals; tag every create with `scenarioTag`; each SDK call cites the mirrored code as a `# path:line` comment; no import from the application codebase.

## Scenario log

Problem log rendered from `templates/scenario-log.template.md`.

- One log per scenario: `## Draft`, then one `## Run {{runNumber}} — {{date}}` section per run, appended. `runNumber :=` last Run history run + 1 (first → `1`).
- Content: only problems faced and their solutions, as `**Problem:** … → **Solution:** …` bullets; blocked → `**Unblocker:**` instead of Solution.
- Group bullets under `### Phase N — <name>` when the problem belongs to a phase; omit phases without problems.
- Write each bullet once the problem is solved or blocked, before the next action. Phase verdicts go to Run history, not the log.

## Draft

Goal: a runnable scenario — every phase with exact commands and **Expected:** — drafted by the agent, confirmed by the user. **MUST** finish Draft (step 5 passed) before any cloud CLI call, Preflight included.

1. **Gather facts** per Sources; ask nothing yet:
   - **Target cloud** from input site/platform info; ambiguous → ask before drafting; never mix clouds.
   - **Scenario flow** (optional; skip when no product flow is found in code or it is one SDK call): symptom → entry point → ordered steps and SDK calls in the product that produce it, incl. branches/conditions taken; written as Given–When–Then one-liners. *Done when* every code keyword links to its source as [`keyword`](path#Lline) and the symptom line is marked.
   - **Resource map**: per SDK call on the symptom's code path (from Scenario flow when present) (service + operation + request parameters) → where the resource and its settings are defined (IaC, or the SDK call itself when code creates/mutates it) → applied settings. *Done when* each row has resource, definition `path:line` (IaC or SDK call), caller `path:line`, SDK op, CLI op, load-bearing settings.
   - **Mechanism**: exact creation semantics of the operation under test — operation type (e.g. import-from-source vs. create-from-image), which branch sets which properties. *Done when* "must match the real code path" section cites file + line range, provider doc URL, and why a naive alternative command diverges.
2. **Draft the scenario**: write every section below into the scenario file, choosing each value yourself from facts; cite `path:line` or provider doc URL per choice. A choice facts cannot settle → pick the safest/cheapest default and mark it `❓` inline. *Done when* every section is filled and every unconfirmed choice carries `❓`.
   1. **Scope** — symptom reproduced; real application excluded; unfixed root cause excluded, naming its tracking ticket; fix option under test or reproduce-only.
   2. **Fidelity** — apply Fidelity ladder; name rung + load-bearing setting the rung below breaks. Rung 3–4 (CLI alone cannot simulate it, per Prototype rules) → always `❓`: add a Prototype section listing each proposed script (what it simulates, mirrored code), why CLI alone falls short, and the closest CLI-only alternative; **MUST NOT** write any `.py` file in Draft.
   3. **Phase list** — Preflight, Prerequisites, Baseline (skip only when Verify exists), Reproduce (Scenario flow steps, when present, kept at chosen rung), Apply fix + Verify (only with fix option), Cleanup.
   4. **Target environment** — variable block: account/subscription, resource group/equivalent, region, image, size, `scenarioTag` (`dig-scenario={{scenarioSlug}}`), `prereqTag` (`dig-scenario-prereq={{scenarioSlug}}`); non-load-bearing values minimal; phases use variables, not literals.
   5. **Naming convention** — test resource → ticket analog → role; names mirror real ones so phases read like the incident; every later-named resource appears here first.
   6. **Prerequisites** — reusable resources needed but not exercised, created once, reused across runs (e.g. bucket/container phases write blobs to; network, base image, key pair). Qualifies only if no setting is load-bearing and no phase mutates its settings; else per-run phase resource. Each: idempotent ensure (exists check → create if missing), tagged `prereqTag`, settings check vs. Target environment.
   7. **Symptom check** — one command asserting the user's exact symptom, reused by Baseline, Reproduce, Verify.
   8. **Phase commands + Expected:** — each `## Phase N — <name>` has exact commands, verification, **Expected:** checkable from command output alone. Preflight prints active identity, account/subscription, region (`aws sts get-caller-identity`, `az account show`) and stops unless intended non-production target; Reproduce builds broken state at chosen rung → symptom check red; Verify → same check green. Use CLI dry-run/what-if before first-time creates where available.
   9. **Cleanup** — delete every per-run resource in target cloud's real dependency order (e.g. detach NICs before deleting the SG/NSG they reference), incl. data phases left in prerequisites (e.g. test blobs); then leftover query on `scenarioTag`. Prerequisites stay; separate **Prerequisite teardown** runs only on user request. Mark both **destructive — requires explicit confirmation before running**. Account/resource group untouched unless input asks.
3. **Review with the user**, in rounds:
   - Show the draft path and a short summary: scope, fidelity rung, phase list, resources to be created.
   - Ask every `❓` choice as a numbered question with options, your recommended answer, and its citation. Ask a choice that depends on another open one in a later round.
   - Ask only decisions; never ask a fact Sources can supply.
   - After each answer round, **re-explore before editing**: run Gather facts again for whatever the answers touch (new resource, branch, operation, region, setting) and verify affected commands per Sources; then update affected sections, remove resolved `❓`, and log a Draft problem bullet when an answer invalidated a drafted choice.
   - *Done when* no `❓` remains and the user confirms the draft.
4. **Caveats + Open items**: fix option's documented limitations → Caveats; choices the user deferred, needed code fix → Open items. *Done when* no overlap and no caveat resolvable now.
5. **Check** draft against Quality Check.

## Run

Loop run → auto-correct → re-run until working.

1. Draft not finished → stop, finish Draft first. Existing scenario file → read whole, append `## Run {{runNumber}} — {{date}}` to log, re-check Quality Check.
2. Approved prototype in the scenario file → write its scripts per Prototype rules, matching the Prototype section; log a problem bullet if a script must diverge from it.
3. Show Preflight output + resources Prerequisites/Reproduce will create (existing prerequisites reused, not listed); get **explicit confirmation before first create**.
4. Run phases in order; after each, before the next phase, save Run history row tagged `runNumber`.
5. On failure, auto-correct: save fix to scenario file in place + log problem/solution bullet under current run/phase **before** re-running; re-run from earliest invalidated phase:
   - Command error (wrong flag, missing dependency, async unfinished) → fix command, verified per Sources.
   - Reproduce stays green / shows different symptom → re-check Resource map, then climb one rung; climbing to rung 3–4 without an approved prototype → ask the user first.
   - **MUST NOT** rewrite **Expected:** or symptom check to match observed output without user agreement.
6. Repeat 4–5 until Done.
7. Get explicit confirmation, run Cleanup, save leftover query result to Run history; leftovers → log problem bullet.

*Done when* Reproduce red with user's exact symptom, Verify (if present) green, Cleanup leaves no `scenarioTag` resources, Status `Working — verified {{date}}`. Unresolvable → log `**Unblocker:**` bullet, Status `Blocked — {{reason}}`, stop.

## Revise

User correction → save edit to scenario file in place + log problem/solution bullet (current run/phase, or Draft) before any cloud call, then re-run from earliest invalidated phase (with create/cleanup confirmations), update Run history. *Done when* Run Done holds again.

## Gotchas

- Long-running ops return early → CLI wait/poll before verifying.
- IAM/RBAC assignments and tags eventually consistent → retry before concluding red/green.
- CLI region/account/subscription default from active profile → pass explicitly from variable block on every command.
- Tag/label indexes lag deletes → re-query before declaring leftovers.
- Request names a real app action or ID → simulate, never apply: build test analogs (role, resource, tag/ID), apply the action to them, reproduce the app's calls with the prototype, assert the symptom on test resources only.

## Quality Check

- Commands name only Naming convention resources; per-run creates apply `scenarioTag`, prerequisites `prereqTag`.
- No prerequisite load-bearing or mutated by a phase.
- Resource map + mechanism cite real source/IaC, not input prose alone; provider-behavior claims cite canonical doc URL.
- No `❓` left; every agent-chosen value confirmed by the user in Review.
- Fidelity choice justifies rejecting lower rung.
- Reproduce + Verify share symptom check; every **Expected:** checkable from output.
- Cleanup follows target cloud's real delete-dependency order.
- Every create/delete behind its confirmation gate.
- File matches what was actually run — no command executed that isn't saved in the file first.
- Log holds only problem → solution bullets, grouped by run and phase.
- No command or prototype call targets the real application or its resources; every target is a Naming convention test resource.
- No prototype script written before the user approved it in Review.
- No source/IaC file changed; code exploration went through `Explore` subagent.
- No unredacted secret or tenant identifier.
