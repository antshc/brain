---
name: research
description: >-
  Investigates a question against primary sources (codebase, NuGet packages, AWS and Azure docs and CLIs, or the web) via subagents and discovered research-* specialists, saving cited findings as Markdown. Use to research a topic, gather docs or API facts, inspect a system as-built (behavior inside one deployable, a flow across deployables, or a data boundary, cited to file and line), or inspect cloud service constraints (APIs, SDK, IAM/RBAC, quotas, throttling, networking).
---

# Research

## Inputs

- `@question` — what to research.
- `@outputShape` [optional] — user-requested document count, diagram type, file path, framing.

## Constraints

- **MUST** delegate all reading to a subagent; this session only routes, briefs, and verifies. Rationale: keeps raw reading out of parent context. If delegation is unavailable, report the blocker; **MUST NOT** research directly. Loading a matched specialist's `SKILL.md`, **Codebase lookups** in [system-inspection.md](system/system-inspection.md), or **Framing** and **Dimensions** in [cloud-inspection.md](cloud/cloud-inspection.md), to brief it (Load specialist contracts) is briefing, not research.
- **MUST** pass `@outputShape` to every subagent **verbatim**, as a constraint the specialist's defaults do not override. Paraphrase drops shape requirements.
- Discover specialists from the roster, never hardcode them: scan available skills across every scope for names matching `research-*`, then judge each by its `description` and `compatibility` line.

## Workflow

### 1. Classify sources

Split `@question` by the source that owns each part's answer:

| Source | Covers |
|---|---|
| **codebase** | this repo, any deployable or supporting repo, installed NuGet packages — what existing code, config, or a dependency actually does; as-built behavior, flow, or data → **Codebase inspection** |
| **cloud** | provider service behavior, APIs, SDKs, IAM/RBAC, quotas, resource state — AWS, Azure → **Cloud inspection**; other providers |
| **web** | other external docs, specs, standards, libraries |

Done when every part of `@question` maps to one source.

### 2. Match specialists

For each cloud or web part, pick the `research-*` specialist whose description covers it. A codebase part asking how this system behaves as-built uses **Codebase inspection**, never a `research-*` specialist; other codebase parts (dependency API facts, isolated lookups) use the Generic brief. An AWS or Azure part uses **Cloud inspection**, never a `research-*` specialist; split a part spanning both into one part per provider. A specialist owns its sources, evidence rules, template, and output path. No match → that part uses the Generic brief.

Best match lists a tool or server in `compatibility` the session lacks → state which is missing, then continue that part with the Generic brief.

### 3. Load specialist contracts

Before dispatch, load each matched specialist skill and read its search contract: inputs or Request fields, scope and mode framing, lookup kinds, source and evidence priority. Read `SKILL.md` only; never its references, templates, or the sources it names. Codebase inspection part → read **Codebase lookups** in [system-inspection.md](system/system-inspection.md) only. Cloud inspection part → read **Framing** and **Dimensions** in [cloud-inspection.md](cloud/cloud-inspection.md) only. Rationale: a brief already shaped to the specialist's contract lets the subagent route each lookup to the right tool and scope on its first search instead of re-classifying the question and searching broadly.

Fill a **search brief** per part from `@question` only:

| Specialist | Search brief |
|---|---|
| **Codebase inspection** | axis (`Behavior` \| `Flow` \| `Data`) per **Codebase inspection**; deployables or repositories as named; planned lookups, each tagged `@shape` and `@depth` from the lookup table in [system-inspection.md](system/system-inspection.md) **Codebase lookups**, literals and symbols quoted exactly, names unknown said so |
| **Cloud inspection** | provider (`aws` \| `azure`); mode (`question` \| `implementation`); services and operations; region and account or subscription; dimensions the answer turns on; whether applied (live CLI) values are needed or documented defaults suffice |
| other `research-*` | its declared inputs, scope, and mode fields |

Unknown field → `unknown`; never guess names, symbols, or accounts. The brief is a starting plan: the specialist's contract wins on conflict, and it may add lookups the brief missed. Done when every specialist, Codebase inspection, and Cloud inspection part has a brief.

### 4. Dispatch by source

One subagent per part; parts with no dependency run in parallel, each writing its own file. Pass each specialist subagent its part's search brief verbatim beside the question.

- **codebase**, Codebase inspection → spawn one subagent with full tool access per part, passing the part's question, search brief, and `@outputShape` verbatim plus the absolute paths, resolved from this skill's base directory, of [system-inspection.md](system/system-inspection.md) and the brief axis's reference and template from **Codebase inspection**. Instruct it to **MUST** read those three files fully, act as the inspector they define, inspect the system as-built, and write one cited Markdown inspection document. The inspector owns its codebase lookups and output path.
- **codebase**, other → read `explore-codebase` skill's **Request**; form `@work` = the Generic brief, `@shape` and `@depth` per its **Route the lookup**, `@outputShape` = `@outputShape`, `@outputArtifact` = the brief's file; spawn a read-only subagent with that request verbatim, instructing it to *run `explore-codebase` skill for the read-only codebase lookup — multi-repo targets, installed NuGet packages, symbol, flow, and config evidence*. Skill unavailable → spawn the explore agent with the same request plus the read-only contract; **MUST NOT** search directly.
- **cloud**, Cloud inspection → spawn one general-purpose subagent with full tool access (CLI, MCP docs servers, web fetch) per provider part, passing the part's question, search brief, and `@outputShape` verbatim plus the absolute paths, resolved from this skill's base directory, of [cloud-inspection.md](cloud/cloud-inspection.md), the provider reference, and the template from **Cloud inspection**. Instruct it to **MUST** read those three files fully, act as the inspector they define, research read-only, and write one cited Markdown cloud inspection document.
- **cloud**, other provider → a `research-*` specialist when matched; otherwise the same subagent runs the Generic brief.
- **web** → delegate the Generic brief directly to a general-purpose subagent with full tool access, including web fetch — not a codebase-only explore agent.

Every subagent returns one final report: output path, cited findings summary, unknowns, and, from a codebase inspector, any Data, Behavior, or cloud follow-ups.

### 5. Verify delegated output

A subagent's summary is a claim, not the output. Open each artifact and check it against Completion criteria. Mechanical defect → repair directly. Needs research redone → re-dispatch with the violated constraint stated first. Inspector follow-up: Data or cloud → dispatch it as a new part; Behavior → offer it to the user and dispatch only on request.

## Codebase inspection

Inspect a system as-built along one axis, picked by the unit the question is about. Shared contract (lookups, evidence ladder, claim types, file references, runtime checks): [system-inspection.md](system/system-inspection.md).

| Axis | Unit; pick when | Reference | Template |
|---|---|---|---|
| **Behavior** | one deployable's contribution to a functional slice; how something works, where a decision is made, what a change touches, which implementation or double serves a call | [behavior-inspection.md](system/behavior-inspection.md) | [behavior-inspection-template.md](system/behavior-inspection-template.md) |
| **Flow** | cross-deployable slice chain; a flow crosses a process boundary, what handles a message next, where it ends, what contract crosses the wire | [flow-inspection.md](system/flow-inspection.md) | [flow-inspection-template.md](system/flow-inspection-template.md) |
| **Data** | one data boundary; key design, ownership, stale reads, attribute migration, concurrent writes, retention, deletion | [data-inspection.md](system/data-inspection.md) | [data-inspection-template.md](system/data-inspection-template.md) |

## Cloud inspection

Inspect provider constraints for one provider per document. Shared contract (framing, dimensions, evidence ladder, claim types, quotas, read-only probes, citations, output path): [cloud-inspection.md](cloud/cloud-inspection.md). Shared template: [cloud-inspection-template.md](cloud/cloud-inspection-template.md).

| Provider | Covers | Reference |
|---|---|---|
| **AWS** | AWS docs (AWS Documentation MCP when installed), `AWSSDK.*` via `inspect-nuget-source`, read-only AWS CLI | [aws.md](cloud/aws.md) |
| **Azure** | Microsoft Learn (Learn MCP when installed), Azure SDK samples then `inspect-nuget-source`, read-only Azure CLI | [azure.md](cloud/azure.md) |

## Generic brief

1. Investigate against primary sources — official docs, source code, specs, first-party APIs — never a secondary write-up. Trace every claim to the source that owns it.
2. Cite each claim's source; mark unverified statements as assumptions or unknowns.
3. Write one Markdown file where the repo keeps such notes (e.g. `docs/research/`); match the existing convention, otherwise pick a sensible path and report it.

## Completion criteria

- **Path and count** — each file sits where the chosen skill's contract (or the Generic brief) puts it; no extra files.
- **Diagram type** — every diagram is the type the user or the skill's contract named.
- **Citations** — inspection documents cite every repository claim per **File references** in [system-inspection.md](system/system-inspection.md); cloud inspection documents cite every claim in place per **Citations** in [cloud-inspection.md](cloud/cloud-inspection.md); every Mermaid block renders.
- **Placeholders** — no `{{…}}` token, `**Rules**` block, or unfilled template section remains.
- **Evidence** — every claim cites its source or is marked as an assumption/unknown.
- **Requested shape** — `@outputShape` constraints are satisfied.
- **Coverage** — every part from Classify sources has an artifact or a reported blocker.
