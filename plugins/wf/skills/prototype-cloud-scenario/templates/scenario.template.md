# {{scenarioSlug}} — {{title|one-line scenario title}}: cloud scenario ({{optionUnderTest|fix option under test, or reproduce-only}})

**Status:** {{status|Draft | Working — verified <date> | Blocked — <reason>}}
**Purpose:** Reproduce {{symptom}} from [{{ticketDocName}}]({{ticketDocPath|relative path to input ticket/summary doc}}) on isolated {{cloud|AWS or Azure}} test resources<!-- @: append ", and validate <option> from [<doc>](<path>)" only when a fix option exists -->.

## Scope

{{scope|symptom reproduced; real application excluded; root cause excluded and its tracking ticket}}

## Scenario flow

<!-- @: optional; omit when no product flow is found in code or the flow is one SDK call already in Resource map -->
<!-- @: Given–When–Then one-liners in flow order; extend with And; link each code keyword as [`keyword`](path#Lline); suffix the symptom line with **(symptom)** -->

- **Given** {{precondition|state/config, e.g. [`AutoAttach`](path#Lline) is true}}
- **When** {{action|entry point or SDK call, e.g. [`CreateVolumeAsync`](path#Lline) runs with [`SnapshotId`](path#Lline)}}
- **Then** {{outcome|resulting state, e.g. volume lacks [`Encrypted`](path#Lline)}} **(symptom)**

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
| {{testResource|scenarioTag'd test resource; never a real app resource}} | {{ticketAnalog|real resource/ID it stands in for; never a command target}} | {{role}} |

## Prerequisites (reusable)

<!-- @: omit section when the scenario needs no reusable resource -->

| Resource | Why not load-bearing | Ensure command | Settings check |
| --- | --- | --- | --- |
| {{prerequisite}} | {{whyNotLoadBearing}} | {{ensureCommand|idempotent exists-check → create, tagged prereqTag}} | {{settingsCheck}} |

## Packages

| Package | Version | Source |
| --- | --- | --- |
| {{package}} | {{version}} | {{source|path:line in csproj/Directory.Packages.props, or nuget.org for LightBDD.XUnit3/xunit.v3}} |

<!-- @: repeat per stage; each stage has exact commands or a scenario-code link, verification, and one **Expected:** checkable from output alone -->

## Phase 0 — Preflight

**Mode:** {{mode|in code (link method) or manual CLI}}

1. {{command|print active identity, account/subscription, region}}

**Expected:** {{expected|intended non-production target}}

## Phase 1 — Prerequisites

**Mode:** {{mode|in code (link method) or manual CLI}}

## Scenario

**Code:** [`{{scenarioSlug}}.cs`]({{scenarioSlug}}.cs)
**Run:** `dotnet run {{scenarioSlug}}.cs` (env vars per Target environment)

| Stage | Step method | Mirrors code | Expected |
| --- | --- | --- | --- |
| Build broken state | `Given_{{step}}` | [`keyword`](path#Lline) | {{expected|resource reaches the broken end-state}} |
| Reproduce | `Then_{{step}}` | [`keyword`](path#Lline) | {{expected|symptom check red with the user's exact symptom}} |
| Apply remediation | `When_{{step}}` | [`keyword`](path#Lline) | {{expected}} |
<!-- @: omit Apply remediation and Validation rows when reproduce-only -->
| Validation | `Then_{{step}}` | [`keyword`](path#Lline) | {{expected|same symptom check green}} |

## Phase {{n}} — Cleanup

**Mode:** {{mode|manual CLI or link to a separate code path, never the `[Scenario]`}}

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

| Run | Date | Stage | Verdict | Signal line |
| --- | --- | --- | --- | --- |
