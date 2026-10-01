---
name: diagnosis-cloud-scenario
description: Draft and run a working cloud scenario that simulates a bug on real AWS or Azure resources — map code to its infrastructure, pick the cheapest faithful fidelity, reproduce the symptom, validate a fix. Use to simulate, reproduce in the cloud, or write a test scenario for an escalation.
disable-model-invocation: true
---

# Diagnosis Cloud Scenario

Goal: one **working** scenario file — every phase run on real resources, every **Expected:** met. Simulate the cheapest behavior that still exercises the bug's mechanism, not the full flow.

**Write-through:** scenario file and log are saved to disk as each step, phase, or correction happens — before the next action, never batched to the end. Never invent a resource name, flag, setting, or expected result not traceable to user input, ticket/summary doc, or real source/IaC.

## Inputs

| Input | Required | Effect |
|---|---|---|
| Symptom | yes | Red signal the symptom check asserts |
| Root cause / mechanism | no | Narrows Resource map |
| Workaround / fix option | no | Present → add Apply fix + Verify; absent → reproduce-only |
| Ticket / summary doc | no | Real resource names, evidence, fix-option caveats |
| Existing scenario file | no | Present → skip Draft; Run with new log |

Accept any mix of free text/docs. Ask only when symptom missing; existing scenario file supplies it.

## Redact

Commands, outputs, scenario file, log **MUST** show secrets and tenant identifiers as `<REDACTED>`: keys, tokens, connection strings, signed URLs, account/subscription/tenant IDs, IDs inside ARNs/resource IDs. Credentials stay in CLI profile/env vars, referenced by name. Quote only signal lines.

## Cloud CLI

Use target cloud's own CLI: `az` (Azure), `aws` (AWS). Load existing aws/azure cloud skills for environment info. Per phase, find exact subcommand/flags via CLI help/docs (create from image vs. raw/imported source, attach/detach volume, swap boot volume, stop/start, console/boot output, teardown, …); check against the real code path from Ground mechanism. Command names differ per cloud — never copy across.

## Fidelity ladder

Pick **lowest** rung preserving every load-bearing setting in Resource map:

1. Single CLI/API call with code's exact operation + parameters.
2. Broken end-state built directly via CLI.
3. Replay of code's exact SDK operation from throwaway script.
4. Only affected component deployed from real IaC into isolated stack/resource group.
5. Real product flow end to end.

Climb only when lower rung drops/changes a load-bearing setting, operation type, or ordering/timing the bug needs. Load-bearing settings = production exactly; rest = smallest/cheapest (size, count, storage, region unless region matters).

## Scenario log

*Run `diagnosis-session-log` skill to open or resume the diagnosis log, write shared log events, and mark it blocked.* Write each event the moment it occurs, before the next step or command.

**One log per run.** `runNumber :=` last Run history run + 1 (first → `1`). Open log with `bugSlug := {{bugSlug}}-run{{runNumber}}`. Draft + first Run share one log; each Run of an existing scenario file opens a **new** log, never resumes an old one. Read earlier runs from Run history, not logs.

Extra events:

| Log event | Write |
|---|---|
| Resource map row / mechanism grounded | `L`: resource, IaC `path:line`, caller `path:line`, load-bearing settings |
| Fidelity rung chosen | `L`: rung, rejected lower rung + setting it breaks |
| Phase runs | `P`: phase, command, redacted signal line, pass/fail vs **Expected:** |
| Fix applied | `F`: change, command |
| Scenario corrected (failure or user request) | `L`: what changed, why, phases re-run |
| Cleanup / leftover check runs | `K`: command, remaining resources |

Status: drafting → `building-loop`; Reproduce → `reproducing`; Verify → `confirming`; working → `done`.

## Draft

Write whole scenario to **one file** `{{bugSlug}}-scenario.md` beside ticket/summary doc (none → ask folder), per Output skeleton. Create file at step 1 with Status `Draft`; save each section as its step completes. **MUST** save the full draft (step 12 passed) before any cloud CLI call, Preflight included.

1. **Target cloud** from input site/platform info. *Done when* one cloud named; ambiguous → ask; never mix clouds.
2. **Map resources**: symptom → code path → cloud SDK call (service + operation) → IaC definition (Terraform, CloudFormation, CDK, SAM, Bicep/ARM, serverless config) → applied settings, via semantic/symbol search, not text search alone. IaC/code missing → ask path. *Done when* Resource map has resource, IaC `path:line`, caller `path:line`, SDK op, CLI op, load-bearing settings.
3. **Ground mechanism**: exact creation semantics of operation under test — operation type (e.g. import-from-source vs. create-from-image), which branch sets which properties. *Done when* "must match the real code path" section cites file + line range and why a naive alternative command diverges.
4. **Fidelity**: apply Fidelity ladder. *Done when* Fidelity choice names rung + load-bearing setting the rung below breaks.
5. **Scope**: symptom reproduced; exclude unfixed root cause, naming its tracking ticket. *Done when* reader can tell which rung builds the broken state.
6. **Target environment**: variable block — account/subscription, resource group/equivalent, region, image, size, `scenarioTag` (e.g. `dig-scenario={{bugSlug}}`); non-load-bearing values minimal. *Done when* phases use variables, not literals.
7. **Naming convention**: table test resource → ticket analog → role; names mirror real ones so phases read like the incident. *Done when* every later-named resource appears here first; every create applies `scenarioTag` (prerequisites: `prereqTag`).
8. **Prerequisites**: reusable resources needed but not exercised, created once, reused across runs (e.g. bucket/container phases write blobs to; network, base image, key pair). Qualifies only if no setting is load-bearing and no phase mutates its settings; else per-run phase resource. Each: idempotent ensure command (exists check → create if missing), tagged `prereqTag` (e.g. `dig-scenario-prereq={{bugSlug}}`), settings check vs. Target environment. *Done when* each is in Naming convention and ensure is re-run safe.
9. **Phases**: one **symptom check** command asserting the user's exact symptom, reused across phases. Each `## Phase N — <name>` has exact commands, verification, **Expected:** pass criterion:
   - **Preflight** — print active identity, account/subscription, region (`aws sts get-caller-identity`, `az account show`); stop unless intended non-production target.
   - **Prerequisites** — run ensures; reuse existing; verify settings.
   - **Baseline** — symptom check green on healthy state; skip only when Verify exists.
   - **Reproduce** — build broken state at chosen rung; symptom check red with exact symptom.
   - **Apply fix** + **Verify** — only with fix option; same symptom check green.
   - **Cleanup** — step 10.

   Use CLI dry-run/what-if before first-time creates where available. *Done when* every **Expected:** checkable from command output alone.
10. **Cleanup**: delete every per-run resource in target cloud's real dependency order (e.g. detach NICs before deleting the SG/NSG they reference), incl. data phases left in prerequisites (e.g. test blobs); then list leftovers carrying `scenarioTag` via tag/label query. Prerequisites stay; separate **Prerequisite teardown** block runs only on user request. Mark both **destructive — requires explicit confirmation before running**. *Done when* each per-run resource has a delete, leftover query present, each prerequisite has teardown, account/resource group untouched unless input asks.
11. **Caveats + Open items**: fix option's documented limitations → Caveats; unconfirmed naming/region/size/fidelity choices → Open items. *Done when* no overlap and no caveat resolvable now.
12. **Check** draft against Quality Check.

## Run

Loop run → improve → re-run until working.

1. No saved draft → stop, finish Draft first. Existing scenario file → read whole, open new log, re-check Quality Check.
2. Show Preflight output + resources Prerequisites/Reproduce will create (existing prerequisites reused, not listed); get **explicit confirmation before first create**.
3. Run phases in order; after each, before the next phase, save Run history row tagged `runNumber` + log `P`.
4. On failure: save fix to scenario file in place + log `L` **before** re-running; re-run from earliest invalidated phase:
   - Command error (wrong flag, missing dependency, async unfinished) → fix command.
   - Reproduce stays green / shows different symptom → re-check Resource map, then climb one rung.
   - **MUST NOT** rewrite **Expected:** or symptom check to match observed output without user agreement.
5. Repeat 3–4 until Done.
6. Get explicit confirmation, run Cleanup, log leftover query result.

*Done when* Reproduce red with user's exact symptom, Verify (if present) green, Cleanup leaves no `scenarioTag` resources, Status `Working — verified {{date}}`. Unresolvable → log `blocked` with unblocker, Status `Blocked — {{reason}}`, stop.

## Revise

User correction → save edit to same file in place + log `L` before any cloud call, then re-run from earliest invalidated phase (with create/cleanup confirmations), update Run history. *Done when* Run Done holds again.

## Gotchas

- Long-running ops return early → CLI wait/poll before verifying.
- IAM/RBAC assignments and tags eventually consistent → retry before concluding red/green.
- CLI region/account/subscription default from active profile → pass explicitly from variable block on every command.
- Tag/label indexes lag deletes → re-query before declaring leftovers.

## Quality Check

- Commands name only Naming convention resources; per-run creates apply `scenarioTag`, prerequisites `prereqTag`.
- No prerequisite load-bearing or mutated by a phase.
- Resource map + mechanism cite real source/IaC, not input prose alone.
- Fidelity choice justifies rejecting lower rung.
- Reproduce + Verify share symptom check; every **Expected:** checkable from output.
- Cleanup follows target cloud's real delete-dependency order.
- Every create/delete behind its confirmation gate.
- File and log match what was actually run — no command executed that isn't saved in the file first.
- No unredacted secret or tenant identifier.

## Output skeleton

````markdown
# <bugSlug> — <one-line title>: cloud scenario (<option under test | reproduce-only>)

**Status:** Draft | Working — verified <date> | Blocked — <reason>
**Purpose:** Reproduce <symptom> from [<bugSlug>.md](<bugSlug>.md) on real <cloud> resources<, and validate <option> from [<bugSlug>-summary.md](<bugSlug>-summary.md)>.

## Scope

<symptom reproduced; root cause excluded and its tracking ticket>

## Resource map

| Resource | IaC | Caller | SDK operation | CLI operation | Load-bearing settings |
| --- | --- | --- | --- | --- | --- |

## <Mechanism section title> (must match the real code path)

<file+line citation, exact API/CLI operation type, why a naive alternative would diverge>

## Fidelity choice

<rung N; what rung N-1 would break>

## Target environment

| Item | Value |
| --- | --- |

## Naming convention

| Test resource | Ticket analog | Role |
| --- | --- | --- |

## Prerequisites (reusable)

| Resource | Why not load-bearing | Ensure command | Settings check |
| --- | --- | --- | --- |

## Symptom check

```bash
...
```

## Phase 0 — Preflight

## Phase 1 — Prerequisites

## Phase 2 — Baseline

## Phase 3 — Reproduce

1. ...

**Expected:** ...

## Phase 4 — Apply fix

## Phase 5 — Verify

## Phase N — Cleanup

**Requires explicit confirmation before running** (destructive):

```bash
...
```

### Prerequisite teardown

**Run only on user request; requires explicit confirmation** (destructive):

```bash
...
```

## Caveats carried over from <option>

- ...

## Open items for review

- ...

## Run history

| Run | Date | Phase | Verdict | Signal line |
| --- | --- | --- | --- | --- |
````
