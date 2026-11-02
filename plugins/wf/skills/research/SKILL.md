---
name: research
description: Investigates a question against primary sources — codebase, NuGet packages, cloud docs and CLIs, or the web — via discovered research-* specialists or subagents, saving cited findings as Markdown. Use to research a topic, gather docs or API facts, or delegate reading legwork.
---

# Research

## Inputs

- `@question` — what to research.
- `@outputShape` [optional] — user-requested document count, diagram type, file path, framing.

## Constraints

- **MUST** delegate all reading to a subagent; this session only routes, briefs, and verifies. Rationale: keeps raw reading out of parent context. If delegation is unavailable, report the blocker; **MUST NOT** research directly. Loading a matched specialist's `SKILL.md` to brief it (Load specialist contracts) is briefing, not research.
- **MUST** pass `@outputShape` to every subagent **verbatim**, as a constraint the specialist's defaults do not override. Paraphrase drops shape requirements.
- Discover specialists from the roster, never hardcode them: scan available skills across every scope for names matching `research-*`, then judge each by its `description` and `compatibility` line.

## Workflow

### 1. Classify sources

Split `@question` by the source that owns each part's answer:

| Source | Covers |
|---|---|
| **codebase** | this repo, any deployable or supporting repo, installed NuGet packages — what existing code, config, or a dependency actually does |
| **cloud** | provider service behavior, APIs, SDKs, IAM/RBAC, quotas, resource state — AWS, Azure, etc. |
| **web** | other external docs, specs, standards, libraries |

Done when every part of `@question` maps to one source.

### 2. Match specialists

For each part, pick the `research-*` specialist whose description covers it. A specialist owns its sources, evidence rules, template, and output path. No match → that part uses the Generic brief.

Best match lists a tool or server in `compatibility` the session lacks → state which is missing, then continue that part with the Generic brief.

### 3. Load specialist contracts

Before dispatch, load each matched specialist skill and read its search contract: inputs or Request fields, scope and mode framing, lookup kinds, source and evidence priority. Read `SKILL.md` only; never its references, templates, or the sources it names. Rationale: a brief already shaped to the specialist's contract lets the subagent route each lookup to the right tool and scope on its first search instead of re-classifying the question and searching broadly.

Fill a **search brief** per part from `@question` only:

| Specialist | Search brief |
|---|---|
| `research-system` | axis (`Behavior` \| `Flow` \| `Data`); deployables or repositories as named; planned lookups, each tagged `@shape` and `@depth` from its lookup table, literals and symbols quoted exactly, names unknown said so |
| `research-aws`, `research-azure` | mode (`question` \| `implementation`); services and operations; region and account or subscription; dimensions the answer turns on; whether applied (live CLI) values are needed or documented defaults suffice |
| other `research-*` | its declared inputs, scope, and mode fields |

Unknown field → `unknown`; never guess names, symbols, or accounts. The brief is a starting plan: the specialist's contract wins on conflict, and it may add lookups the brief missed. Done when every specialist part has a brief.

### 4. Dispatch by source

One subagent per part; parts with no dependency run in parallel, each writing its own file. Pass each specialist subagent its part's search brief verbatim beside the question.

- **codebase** → spawn a subagent with the part's question, search brief, and `@outputShape` verbatim, instructing it to **MUST** *run `research-system` skill to inspect the system as-built — behavior, cross-deployable flow, or data boundary — and write a cited Markdown inspection document*. The specialist owns axis, template, output path, and its codebase lookups. No `research-*` specialist matches → read `explore-codebase` skill's **Request**; form `@work` = the Generic brief, `@shape` and `@depth` per its **Route the lookup**, `@outputShape` = `@outputShape`, `@outputArtifact` = the brief's file; spawn a read-only subagent with that request verbatim, instructing it to *run `explore-codebase` skill for the read-only codebase lookup — multi-repo targets, installed NuGet packages, symbol, flow, and config evidence*. Skill unavailable → spawn the explore agent with the same request plus the read-only contract; **MUST NOT** search directly.
- **cloud** → spawn a general-purpose subagent with full tool access (CLI, MCP docs servers, web fetch), passing the part's question, search brief, and `@outputShape` verbatim, instructing it to **MUST** run the provider's specialist when present in the roster; the specialist owns CLI discovery and docs-MCP search:
  - AWS → *run `research-aws` skill to research AWS service behavior, API operations, SDK, IAM, Service Quotas, throttling and retries into an evidence-backed research file*.
  - Azure → *run `research-azure` skill to research Azure service behavior, REST/ARM operations, SDK, Entra ID, RBAC, subscription quotas, throttling and retries into an evidence-backed research file*.
  - Specialist absent, other provider, or no match → the same subagent runs the Generic brief.
- **web** → delegate the Generic brief directly to a general-purpose subagent with full tool access, including web fetch — not a codebase-only explore agent.

Every subagent returns one final report: output path, cited findings summary, unknowns.

### 5. Verify delegated output

A subagent's summary is a claim, not the output. Open each artifact and check it against Completion criteria. Mechanical defect → repair directly. Needs research redone → re-dispatch with the violated constraint stated first.

## Generic brief

1. Investigate against primary sources — official docs, source code, specs, first-party APIs — never a secondary write-up. Trace every claim to the source that owns it.
2. Cite each claim's source; mark unverified statements as assumptions or unknowns.
3. Write one Markdown file where the repo keeps such notes (e.g. `docs/research/`); match the existing convention, otherwise pick a sensible path and report it.

## Completion criteria

- **Path and count** — each file sits where the chosen skill's contract (or the Generic brief) puts it; no extra files.
- **Diagram type** — every diagram is the type the user or the skill's contract named.
- **Placeholders** — no `{{…}}` token, `**Rules**` block, or unfilled template section remains.
- **Evidence** — every claim cites its source or is marked as an assumption/unknown.
- **Requested shape** — `@outputShape` constraints are satisfied.
- **Coverage** — every part from Classify sources has an artifact or a reported blocker.
