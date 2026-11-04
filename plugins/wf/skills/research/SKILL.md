---
name: research
description: >-
  Investigates a question against primary sources (codebase, NuGet packages, cloud docs and CLIs, or the web) via subagents and discovered research-* specialists, saving cited findings as Markdown. Use to research a topic, gather docs or API facts, or inspect a system as-built; behavior inside one deployable, a flow across deployables, or a data boundary, cited to file and line.
---

# Research

## Inputs

- `@question` — what to research.
- `@outputShape` [optional] — user-requested document count, diagram type, file path, framing.

## Constraints

- **MUST** delegate all reading to a subagent; this session only routes, briefs, and verifies. Rationale: keeps raw reading out of parent context. If delegation is unavailable, report the blocker; **MUST NOT** research directly. Loading a matched specialist's `SKILL.md`, or **Codebase lookups** in [system-inspection.md](system/system-inspection.md), to brief it (Load specialist contracts) is briefing, not research.
- **MUST** pass `@outputShape` to every subagent **verbatim**, as a constraint the specialist's defaults do not override. Paraphrase drops shape requirements.
- Discover specialists from the roster, never hardcode them: scan available skills across every scope for names matching `research-*`, then judge each by its `description` and `compatibility` line.

## Workflow

### 1. Classify sources

Split `@question` by the source that owns each part's answer:

| Source | Covers |
|---|---|
| **codebase** | this repo, any deployable or supporting repo, installed NuGet packages — what existing code, config, or a dependency actually does; as-built behavior, flow, or data → **Codebase inspection** |
| **cloud** | provider service behavior, APIs, SDKs, IAM/RBAC, quotas, resource state — AWS, Azure, etc. |
| **web** | other external docs, specs, standards, libraries |

Done when every part of `@question` maps to one source.

### 2. Match specialists

For each cloud or web part, pick the `research-*` specialist whose description covers it. A codebase part asking how this system behaves as-built uses **Codebase inspection**, never a `research-*` specialist; other codebase parts (dependency API facts, isolated lookups) use the Generic brief. A specialist owns its sources, evidence rules, template, and output path. No match → that part uses the Generic brief.

Best match lists a tool or server in `compatibility` the session lacks → state which is missing, then continue that part with the Generic brief.

### 3. Load specialist contracts

Before dispatch, load each matched specialist skill and read its search contract: inputs or Request fields, scope and mode framing, lookup kinds, source and evidence priority. Read `SKILL.md` only; never its references, templates, or the sources it names. Codebase inspection part → read **Codebase lookups** in [system-inspection.md](system/system-inspection.md) only. Rationale: a brief already shaped to the specialist's contract lets the subagent route each lookup to the right tool and scope on its first search instead of re-classifying the question and searching broadly.

Fill a **search brief** per part from `@question` only:

| Specialist | Search brief |
|---|---|
| **Codebase inspection** | axis (`Behavior` \| `Flow` \| `Data`) per **Codebase inspection**; deployables or repositories as named; planned lookups, each tagged `@shape` and `@depth` from the lookup table in [system-inspection.md](system/system-inspection.md) **Codebase lookups**, literals and symbols quoted exactly, names unknown said so |
| `research-aws`, `research-azure` | mode (`question` \| `implementation`); services and operations; region and account or subscription; dimensions the answer turns on; whether applied (live CLI) values are needed or documented defaults suffice |
| other `research-*` | its declared inputs, scope, and mode fields |

Unknown field → `unknown`; never guess names, symbols, or accounts. The brief is a starting plan: the specialist's contract wins on conflict, and it may add lookups the brief missed. Done when every specialist and Codebase inspection part has a brief.

### 4. Dispatch by source

One subagent per part; parts with no dependency run in parallel, each writing its own file. Pass each specialist subagent its part's search brief verbatim beside the question.

- **codebase**, Codebase inspection → spawn one subagent with full tool access per part, passing the part's question, search brief, and `@outputShape` verbatim plus the absolute paths, resolved from this skill's base directory, of [system-inspection.md](system/system-inspection.md) and the brief axis's reference and template from **Codebase inspection**. Instruct it to **MUST** read those three files fully, act as the inspector they define, inspect the system as-built, and write one cited Markdown inspection document. The inspector owns its codebase lookups and output path.
- **codebase**, other → read `explore-codebase` skill's **Request**; form `@work` = the Generic brief, `@shape` and `@depth` per its **Route the lookup**, `@outputShape` = `@outputShape`, `@outputArtifact` = the brief's file; spawn a read-only subagent with that request verbatim, instructing it to *run `explore-codebase` skill for the read-only codebase lookup — multi-repo targets, installed NuGet packages, symbol, flow, and config evidence*. Skill unavailable → spawn the explore agent with the same request plus the read-only contract; **MUST NOT** search directly.
- **cloud** → spawn a general-purpose subagent with full tool access (CLI, MCP docs servers, web fetch), passing the part's question, search brief, and `@outputShape` verbatim, instructing it to **MUST** run the provider's specialist when present in the roster; the specialist owns CLI discovery and docs-MCP search:
  - AWS → *run `research-aws` skill to research AWS service behavior, API operations, SDK, IAM, Service Quotas, throttling and retries into an evidence-backed research file*.
  - Azure → *run `research-azure` skill to research Azure service behavior, REST/ARM operations, SDK, Entra ID, RBAC, subscription quotas, throttling and retries into an evidence-backed research file*.
  - Specialist absent, other provider, or no match → the same subagent runs the Generic brief.
- **web** → delegate the Generic brief directly to a general-purpose subagent with full tool access, including web fetch — not a codebase-only explore agent.

Every subagent returns one final report: output path, cited findings summary, unknowns, and, from an inspector, any Data, Behavior, or cloud follow-ups.

### 5. Verify delegated output

A subagent's summary is a claim, not the output. Open each artifact and check it against Completion criteria. Mechanical defect → repair directly. Needs research redone → re-dispatch with the violated constraint stated first. Inspector follow-up: Data or cloud → dispatch it as a new part; Behavior → offer it to the user and dispatch only on request.

## Codebase inspection

Inspect a system as-built along one axis, picked by the unit the question is about. Shared contract (lookups, evidence ladder, claim types, file references, runtime checks): [system-inspection.md](system/system-inspection.md).

| Axis | Unit; pick when | Reference | Template |
|---|---|---|---|
| **Behavior** | one deployable's contribution to a functional slice; how something works, where a decision is made, what a change touches, which implementation or double serves a call | [behavior-inspection.md](system/behavior-inspection.md) | [behavior-inspection-template.md](system/behavior-inspection-template.md) |
| **Flow** | cross-deployable slice chain; a flow crosses a process boundary, what handles a message next, where it ends, what contract crosses the wire | [flow-inspection.md](system/flow-inspection.md) | [flow-inspection-template.md](system/flow-inspection-template.md) |
| **Data** | one data boundary; key design, ownership, stale reads, attribute migration, concurrent writes, retention, deletion | [data-inspection.md](system/data-inspection.md) | [data-inspection-template.md](system/data-inspection-template.md) |

## Generic brief

1. Investigate against primary sources — official docs, source code, specs, first-party APIs — never a secondary write-up. Trace every claim to the source that owns it.
2. Cite each claim's source; mark unverified statements as assumptions or unknowns.
3. Write one Markdown file where the repo keeps such notes (e.g. `docs/research/`); match the existing convention, otherwise pick a sensible path and report it.

## Completion criteria

- **Path and count** — each file sits where the chosen skill's contract (or the Generic brief) puts it; no extra files.
- **Diagram type** — every diagram is the type the user or the skill's contract named.
- **Citations** — inspection documents cite every repository claim per **File references** in [system-inspection.md](system/system-inspection.md); every Mermaid block renders.
- **Placeholders** — no `{{…}}` token, `**Rules**` block, or unfilled template section remains.
- **Evidence** — every claim cites its source or is marked as an assumption/unknown.
- **Requested shape** — `@outputShape` constraints are satisfied.
- **Coverage** — every part from Classify sources has an artifact or a reported blocker.
