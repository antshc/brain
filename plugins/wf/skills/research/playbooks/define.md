# Define Research

## Contents

- Research, don't decide
- Refer by name
- The research map
- Topics
- Fog of war
- Out of scope
- Invocation

A research prompt or context has arrived, and it may hide several questions. This route charts it as a **research map**: a destination, the topics that must be resolved to reach it, and the fog beyond them. It then works the frontier — `/research` topics in parallel, experiments one at a time with the user — until nothing left open can change the destination.

The destination is the decision, explanation, design, or action the findings must support. Naming it is the first act of charting: it fixes the scope and shapes every topic.

## Research, don't decide

Each topic surfaces a fact or tests a claim; the map is done when the findings support the destination. The decision itself and any implementation belong to the caller after the map is done. The selected evidence route owns sources, evidence strategy, and citations. Define owns the map and topic destinations; the Research router writes reports; a topic carries the question, not a source strategy.

## Refer by name

In everything the user reads — narration, printed tables, Findings so far — refer to a topic by its title, never by a number or slug.

## The research map

The map is one Markdown file at `docs/ongoing/{{destinationSlug}}-research-map.md`, where `destinationSlug` is a short kebab-case name for the destination. Create `docs/ongoing/` when missing. The file outlives the session and is the single source of truth for resuming.

Render using the already-loaded Research map template, Map and Topic sections. Preserve all map sections and existing findings links on resume.

## Topics

One topic is one sharp question, sized to one `/research` run or one experiment.

- **Research** (AFK) — surfaces a fact the destination waits on from documentation, APIs, specifications, source code, or local knowledge bases. Always resolved via research.
- **Hypothesis** — a falsifiable claim whose truth changes the destination. Names its resolver: experiment (HITL) when the behavior must be observed for real; research (AFK) when authoritative sources settle it.

Resolvers: **research** → the existing Explore, How, Why, Cloud or Web evidence pipeline; **experiment** → *Load and follow the `prove` skill to confirm or refute one technical claim with reproducible evidence*, which builds the smallest throwaway artifact that exercises the claim and records whether it held. An experiment's result is an observation, so it confirms or refutes the claim; it never ships.

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

Copy this checklist into working notes; update it as the map progresses.

```markdown
- [ ] Destination confirmed or resumed
- [ ] Topics, fog and exclusions mapped
- [ ] Map saved, presented and confirmed
- [ ] Frontier resolved or explicitly deferred
- [ ] Findings and remaining work persisted
```

- **Chart** — the argument is a research prompt or context: run Steps 1–5.
- **Resume** — the argument is an existing research map path: read the whole map, retain its destination, links and state, print it as in Step 3, then continue from Step 4 without restarting the destination interview. Missing or unreadable map → report the blocker; do not silently create a replacement.

### 1. Name the destination

Follow the already-loaded Questioning procedure over the prompt, the conversation, and the available context to settle the subject and the destination.

For third-party API or SDK research, use Explore to inspect manifests, lockfiles, imports, and configuration to resolve the exact version in use; ask the user only when the codebase does not establish it. Record the version in Notes.

**Done when:** the user confirms the destination and it names both the subject and the outcome the findings must support.

### 2. Map the frontier

Follow the already-loaded Questioning procedure again, breadth-first: fan out across approaches, alternatives, constraints, and unknowns rather than deep on one thread. Ask only questions that can change the set of topics; look up facts rather than asking for them, and keep unresolved factual claims as topics. Turn claims whose truth changes the destination into hypothesis topics.

**Done when:** every sharp question is a topic with type, resolver, and Blocked by filled in; everything else sits in Not yet specified or Out of scope.

### 3. Write and print

Write the map. When a map with the same `destinationSlug` already exists, ask whether to overwrite it or resume it.

Print to the user:

| Topic | Type | Resolve via | Blocked by |
|---|---|---|---|
| {{topic title}} | {{type}} | {{resolver}} | {{blocking titles or none}} |

followed by the Not yet specified and Out of scope lists. Ask the user to confirm or correct the map; return to the already-loaded Questioning procedure when a correction exposes an unresolved branch.

**Done when:** the user confirms and the file matches what was printed.

### 4. Hand off the frontier

Ask whether to resolve the frontier now. On decline, stop — the map file holds the state for a later resume.

On acceptance:

- Resolve frontier research topics through the router's Frame, Routing and Spawning agents procedures. Select Explore, How, Why, Cloud or Web per question; load that playbook and required or triggered resources fully before use. Never recursively invoke Research or select Define for a topic. Brief: the topic's Question or Claim and confirm/refute conditions, Destination and Notes verbatim; read-only; cited findings, unknowns and blockers. Batch independent topics in parallel where supported; sequence dependent topics and each route's agent stages. If parallel execution is unavailable, run the same topics sequentially and report the limitation.
- Set each topic destination to absolute `<map repository root>/docs/research/{{destinationSlug}}-{{topicSlug}}.md`, or an explicit caller destination. Use distinct topic slugs; separate reports within a topic each get their own path. These explicit paths override session defaults. Save Explore verdicts unabridged to the topic path as a Define-only delivery exception; other routes write their normal reports there. Read every report fully before recording findings.
- Offer each frontier experiment to the user one at a time; on acceptance, *Load and follow the `prove` skill to confirm or refute one technical claim with reproducible evidence*, filling `@question` = the Claim, `@criteria` = its confirm/refute conditions, `@repoFacts` = the Notes verbatim plus findings from resolved research topics. Supply the exact topic `@outputPath` and repository `@outputBase` using this caller's research-topic destination convention; request retention through any human review; read its returned report in full.

**Done when:** every frontier topic has a result or explicit declined, partial, inconclusive or blocked status persisted in the map; unavailable evidence never counts as resolution.

### 5. Record and loop

For each result:

- For a supported answer or confirmed/refuted hypothesis, add a line to Findings so far linking the findings file or experiment result, then remove the topic from Topics. Keep partial, blocked, declined and inconclusive topics open with the reason and any partial-evidence link; their dependants remain blocked.
- Graduate any fog the result made specifiable into new topics, clearing it from Not yet specified.
- Move any topic the result shows to sit past the destination into Out of scope.
- Update or delete topics the result invalidates, and re-rank Topics by risk.

Write the map and reprint it as in Step 3. Check closure before offering more work. If Topics and Not yet specified are empty, or the user confirms remaining work cannot change the destination, print the final map with Findings so far and stop. If all remaining topics are declined, partial, inconclusive or blocked with no new actionable frontier, hand back their status and the resumable map rather than repeating the same offer. Otherwise return to Step 4.

**Done when:** Topics and Not yet specified are both empty, or the user confirms the remaining topics cannot change the destination. Print the final map with its Findings so far.
