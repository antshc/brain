---
name: define-research
description: Charts a research prompt or context into a research map of one or many research and hypothesis topics under docs/ongoing/, then resolves them through /research or through experiments run by /prototype until the destination is clear. Use to define, split, or scope research before running it, or to resume an existing research map.
argument-hint: "{{researchPromptOrContext}} | {{researchMapPath}}"
disable-model-invocation: true
---

# Define Research

A research prompt or context has arrived, and it may hide several questions. This skill charts it as a **research map**: a destination, the topics that must be resolved to reach it, and the fog beyond them. It then works the frontier — `/research` topics in parallel, experiments one at a time with the user — until nothing left open can change the destination.

The destination is the decision, explanation, design, or action the findings must support. Naming it is the first act of charting: it fixes the scope and shapes every topic.

## Research, don't decide

Each topic surfaces a fact or tests a claim; the map is done when the findings support the destination. The decision itself and any implementation belong to the caller after the map is done. `/research` and its specialists own sources, evidence strategy, citations, and findings files — a topic carries only the question.

## Refer by name

In everything the user reads — narration, printed tables, Findings so far — refer to a topic by its title, never by a number or slug.

## The research map

The map is one Markdown file at `docs/ongoing/{{destinationSlug}}-research-map.md`, where `destinationSlug` is a short kebab-case name for the destination. Create `docs/ongoing/` when missing. The file outlives the session and is the single source of truth for resuming.

```markdown
# {{destination short name}} — research map

## Destination

{{decision, explanation, design, or action the findings must support — one or two lines}}

## Notes

{{constraints that can change the answer; resolved API/SDK versions; standing preferences}}

## Topics

<!-- open topics, ordered by risk; one block per topic, see Topics -->

## Findings so far

<!-- one line per resolved topic -->

- [{{topic title}}]({{findings file or experiment link}}) — {{one-line gist of the finding}}

## Not yet specified

<!-- see Fog of war -->

## Out of scope

<!-- see Out of scope -->
```

## Topics

One topic is one sharp question, sized to one `/research` run or one experiment.

```markdown
### {{topic title}}

- **Type:** {{type| research | hypothesis }}
- **Question:** {{research: the fact to surface}} | **Claim:** {{hypothesis: the falsifiable claim}} — **confirmed when** {{observable condition}}, **refuted when** {{observable condition}}
- **Resolve via:** {{resolver| research | experiment }}
- **Blocked by:** {{titles of open topics this waits on, or none}}
```

- **Research** (AFK) — surfaces a fact the destination waits on from documentation, APIs, specifications, source code, or local knowledge bases. Always resolved via research.
- **Hypothesis** — a falsifiable claim whose truth changes the destination. Names its resolver: experiment (HITL) when the behavior must be observed for real; research (AFK) when authoritative sources settle it.

Resolvers map to skills: **research** → `/research`; **experiment** → `/prototype`, which builds the smallest throwaway artifact that exercises the claim and records whether it held. An experiment's result is an observation, so it confirms or refutes the claim; it never ships.

A topic is **unblocked** when every title in its Blocked by has moved to Findings so far. The **frontier** is every open, unblocked topic.

Order Topics by risk — the power of the finding to invalidate an approach: feasibility and hard limits, performance and scale, reliability, security, operational complexity, then developer ergonomics.

## Fog of war

Chart only what you can see. Not yet specified holds in-scope areas that hang on topics still open: the suspected question, the area to revisit. Resolving a topic clears the fog ahead of it, graduating whatever is now specifiable into new topics.

Fog or topic? The test is whether you can state the question precisely now — not whether you can answer it now.

- Topic when the question is sharp, even if it is blocked.
- Not yet specified when it is not yet that sharp. Keep fog coarse: one patch may graduate into several topics, or none.

## Out of scope

The destination fixes the scope; work beyond it goes to Out of scope, one line each with the reason. Out-of-scope work never graduates — it returns only if the destination is redrawn, as a fresh map. When an existing topic turns out to sit past the destination, remove it from Topics and record it here, never in Findings so far.

## Invocation

- **Chart** — the argument is a research prompt or context: run Steps 1–5.
- **Resume** — the argument is an existing research map path: read the map, print it as in Step 3, then continue from Step 4.

### 1. Name the destination

Run `/questioning` skill over the prompt, the conversation, and the available context to settle the subject and the destination.

For third-party API or SDK research, inspect manifests, lockfiles, imports, and configuration to resolve the exact version in use; ask the user only when the codebase does not establish it. Record the version in Notes.

**Done when:** the user confirms the destination and it names both the subject and the outcome the findings must support.

### 2. Map the frontier

Run `/questioning` skill again, breadth-first: fan out across approaches, alternatives, constraints, and unknowns rather than deep on one thread. Ask only questions that can change the set of topics; look up facts rather than asking for them, and keep unresolved factual claims as topics. Turn claims whose truth changes the destination into hypothesis topics.

**Done when:** every sharp question is a topic with type, resolver, and Blocked by filled in; everything else sits in Not yet specified or Out of scope.

### 3. Write and print

Write the map. When a map with the same `destinationSlug` already exists, ask whether to overwrite it or resume it.

Print to the user:

| Topic | Type | Resolve via | Blocked by |
|---|---|---|---|
| {{topic title}} | {{type}} | {{resolver}} | {{blocking titles or none}} |

followed by the Not yet specified and Out of scope lists. Ask the user to confirm or correct the map; return to `/questioning` when a correction exposes an unresolved branch.

**Done when:** the user confirms and the file matches what was printed.

### 4. Hand off the frontier

Ask whether to resolve the frontier now. On decline, stop — the map file holds the state for a later resume.

On acceptance:

- Run `/research` skill in parallel, one subagent per frontier topic resolved via research. Pass the topic's Question or Claim with its confirm/refute conditions, the Destination, and the Notes verbatim.
- Offer each frontier experiment to the user one at a time; on acceptance, Run `/prototype` skill with the Claim as the question, its confirm/refute conditions as the observation criteria, and the Notes verbatim.

**Done when:** every frontier topic has either returned a result or been declined by the user.

### 5. Record and loop

For each result:

- Add a line to Findings so far linking the findings file or experiment result, and remove the topic from Topics.
- Graduate any fog the result made specifiable into new topics, clearing it from Not yet specified.
- Move any topic the result shows to sit past the destination into Out of scope.
- Update or delete topics the result invalidates, and re-rank Topics by risk.

Write the map, reprint it as in Step 3, and return to Step 4.

**Done when:** Topics and Not yet specified are both empty, or the user confirms the remaining topics cannot change the destination. Print the final map with its Findings so far.