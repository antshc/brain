---
name: research
description: Investigates a question against primary sources — codebase, NuGet packages, cloud docs and CLIs, or the web — via discovered research-* specialists or subagents, saving cited findings as Markdown. Use to research a topic, gather docs or API facts, or delegate reading legwork.
---

# Research

## Inputs

- `@question` — what to research.
- `@outputShape` [optional] — user-requested document count, diagram type, file path, framing.

## Constraints

- **MUST** delegate all reading to a subagent; this session only routes, briefs, and verifies. Rationale: keeps raw reading out of parent context. If delegation is unavailable, report the blocker; **MUST NOT** research directly.
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

### 3. Dispatch by source

One subagent per part; parts with no dependency run in parallel, each writing its own file.

- **codebase** → **MUST** *run `explore-codebase` skill to delegate the read-only codebase lookup — multi-repo targets, installed NuGet packages, symbol, flow, and config evidence* — naming the matched specialist (e.g. `research-system`) as the skill for its subagent to run and that skill's document as the output artifact; with no specialist, pass the Generic brief as the instruction and its file as the output artifact. **MUST NOT** substitute a plain subagent or direct search. Rationale: the engine owns target resolution, the deployables index, graph coverage, and NuGet routing. If the skill is unavailable, report the blocker for that part.
- **cloud** → delegate to a general-purpose subagent with full tool access (CLI, MCP docs servers, web fetch) that runs the matched specialist (e.g. `research-aws`, `research-azure`); the specialist owns CLI discovery and docs-MCP search.
- **web** → delegate the Generic brief directly to a general-purpose subagent with full tool access, including web fetch — not a codebase-only explore agent.

Every subagent returns one final report: output path, cited findings summary, unknowns.

### 4. Verify delegated output

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
