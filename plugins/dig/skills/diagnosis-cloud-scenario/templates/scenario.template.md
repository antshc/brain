# {{scenarioSlug}} — {{title|one-line scenario title}}: cloud scenario ({{optionUnderTest|fix option under test, or reproduce-only}})

**Status:** {{status|Draft | Working — verified <date> | Blocked — <reason>}}
**Purpose:** Reproduce {{symptom}} from [{{ticketDocName}}]({{ticketDocPath|relative path to input ticket/summary doc}}) on real {{cloud|AWS or Azure}} resources<!-- @: append ", and validate <option> from [<doc>](<path>)" only when a fix option exists -->.

## Scope

{{scope|symptom reproduced; root cause excluded and its tracking ticket}}

## Scenario flow

<!-- @: product flow under diagnosis as found in code; mark the step where the symptom appears -->

1. {{step|entry point or step, SDK call if any — path:line}}

## Resource map

| Resource | Definition | Caller | SDK operation | CLI operation | Load-bearing settings |
| --- | --- | --- | --- | --- | --- |
| {{resource}} | {{definitionRef|IaC or SDK-call path:line}} | {{callerRef|path:line}} | {{sdkOperation}} | {{cliOperation}} | {{loadBearingSettings}} |

## {{mechanismTitle|operation under test}} (must match the real code path)

{{mechanism|file + line-range citation, exact API/CLI operation type, canonical provider doc URL, why a naive alternative command diverges}}

## Fidelity choice

{{fidelity|rung N; load-bearing setting rung N-1 would break}}

## Target environment

| Item | Value |
| --- | --- |
| {{item|account/subscription, resource group, region, image, size, scenarioTag, prereqTag}} | {{value}} |

## Naming convention

| Test resource | Ticket analog | Role |
| --- | --- | --- |
| {{testResource}} | {{ticketAnalog}} | {{role}} |

## Prerequisites (reusable)

<!-- @: omit section when the scenario needs no reusable resource -->

| Resource | Why not load-bearing | Ensure command | Settings check |
| --- | --- | --- | --- |
| {{prerequisite}} | {{whyNotLoadBearing}} | {{ensureCommand|idempotent exists-check → create, tagged prereqTag}} | {{settingsCheck}} |

## Symptom check

```bash
{{symptomCheck|one command asserting the user's exact symptom; reused by Baseline, Reproduce, Verify}}
```

<!-- @: repeat per phase; each phase has numbered commands, verification, and one **Expected:** checkable from output alone -->

## Phase 0 — Preflight

1. {{command|print active identity, account/subscription, region}}

**Expected:** {{expected|intended non-production target}}

## Phase 1 — Prerequisites

## Phase 2 — Baseline

<!-- @: omit only when Verify exists -->

## Phase 3 — Reproduce

1. {{command}}

**Expected:** {{expected|symptom check red with the user's exact symptom}}

## Phase 4 — Apply fix

<!-- @: omit Apply fix and Verify when reproduce-only -->

## Phase 5 — Verify

**Expected:** {{expected|same symptom check green}}

## Phase {{n}} — Cleanup

**Requires explicit confirmation before running** (destructive):

```bash
{{cleanupCommands|per-run deletes in the cloud's real dependency order, then leftover query on scenarioTag}}
```

### Prerequisite teardown

**Run only on user request; requires explicit confirmation** (destructive):

```bash
{{teardownCommands}}
```

## Caveats carried over from {{optionUnderTest}}

<!-- @: omit when reproduce-only -->

- {{caveat}}

## Open items for review

- {{openItem|unconfirmed naming, region, size, or fidelity choice; needed code fix}}

## Run history

| Run | Date | Phase | Verdict | Signal line |
| --- | --- | --- | --- | --- |
