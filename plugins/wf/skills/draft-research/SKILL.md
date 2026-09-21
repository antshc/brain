---
name: draft-research
description: Drafts a decision-ready research request through a focused interview.
disable-model-invocation: true
---

# Draft Research

Work **decision-backwards**: identify what the findings must let the user decide, explain, design, or do, then shape the investigation around the evidence needed for that outcome.

Produce the research instruction, then hand the confirmed request to `/research`.

## 1. Seed the research tree

Extract what the user has already supplied before asking anything: the desired outcome, subject, known anchors, suspected answer, boundaries, source material, constraints, audience, and requested artifact.

Look up facts available from the environment or supplied sources. Ask the user for choices, priorities, access they control, and facts only they can know.

Map unresolved choices as a dependency tree. Open only branches that can materially change where the researcher looks, what evidence settles the question, or what the deliverable contains:

- **Outcome** — the decision, explanation, design, or action the findings must support.
- **Question** — one primary question and the subordinate questions required to answer it.
- **Subject** — systems, providers, services, capabilities, artifacts, versions, regions, dates, or other greppable anchors.
- **Boundary** — entry and stopping points, included and excluded concerns, environments, repositories, accounts, and time horizon.
- **Evidence** — authoritative sources, acceptable secondary sources, freshness requirements, and claims requiring live-state checks or probes.
- **Challenge** — assumptions, expected conclusions, alternatives, failure paths, and disconfirming evidence the research must test.
- **Deliverable** — audience, format, location, diagrams or tables, comparison criteria, and completion criterion.

**Done when:** every unresolved item is either discoverable without the user or represented by a question whose answer can change the research instruction.

## 2. Interview the frontier

The **frontier** is every unresolved question whose prerequisites are settled. Ask up to three independent frontier questions per round, then wait. A question depending on another answer belongs to a later round.

Use this shape:

```markdown
**Q1 — {{short title}}**
{{one decision the user must make}}

**Recommended:** {{answer and brief reason}}
```

Offer concrete options when they expose a real tradeoff. Give a recommendation based on the stated outcome and mark it as an assumption if the user accepts the draft without answering.

Turn an expected answer into a hypothesis to test. Ask what evidence would overturn it; frame the request to seek confirming and disconfirming evidence.

Stop interviewing when another answer would only alter wording, not the investigation. Summarize any assumptions that remain and draft the instruction.

**Done when:** the frontier is empty and no material research choice remains silently assumed.

## 3. Calibrate by research domain

Apply every cross-domain field above, then add only the relevant branch below.

### System research

Resolve the unit being investigated, the trace entry point, observable outcome or terminal boundary, important branches, concrete implementations, runtime configuration, and suspected doubles or local-only infrastructure. For cross-process flows, require both sides of each contract. For data questions, identify the item type, store, writers, readers, consistency, concurrency, migration, and retention concerns that matter.

### Cloud research

Resolve provider, service, operation, SDK and API version, region, account or subscription scope, identity and permissions, network path, quotas, retries, failures, and whether the answer needs documented defaults or applied live values. Name commands and environments that are safe to probe.

### Architecture research

Resolve whether the user needs current state, a proposed design, alternatives, or a delta. Name the system boundary, actors and neighboring systems, deployable units, integrations, deployment context, quality attributes, constraints, and tradeoffs the conclusion must settle. Request only views or diagrams that answer a named question.

### External or general research

Resolve the authoritative source classes, publication or version cutoff, geographic or regulatory scope when relevant, comparison set, evaluation criteria, and acceptable evidence age. Prefer primary sources and require each conclusion to trace to the claims supporting it.

**Done when:** every domain-specific detail that can change the conclusion or its applicability is either resolved or explicitly named as an unknown to investigate.

## 4. Draft the instruction

Write one standalone instruction in this shape, removing empty sections and replacing every placeholder:

```markdown
Research {{subject}} to determine {{primary question}} so that {{decision, explanation, design, or action}}.

## Context
{{known facts, anchors, and hypotheses to test}}

## Questions to settle
- {{subquestion whose answer is necessary}}

## Scope
- Start at: {{entry point, earliest date, or initial boundary}}
- Stop at: {{observable outcome, terminal boundary, cutoff, or sufficient evidence}}
- Include: {{branches, environments, alternatives, or concerns}}
- Exclude: {{explicit non-goals}}

## Evidence
- Prefer: {{source hierarchy}}
- Verify live: {{state-dependent claims and permitted probes}}
- Distinguish: {{documented defaults, configured values, observed behavior, assumptions, and unknowns as relevant}}
- Challenge: {{expected answer and evidence that would disconfirm it}}

## Deliverable
{{audience, format, output location, required views, and citation style}}

## Complete when
{{exhaustive, checkable condition showing the primary question is answered and decision-relevant unknowns are exposed}}
```

Keep one research unit per instruction. Split independent questions when they require different boundaries, evidence, or deliverables.

Present the finished instruction in one fenced Markdown block and ask the user to confirm it.

**Done when:** the instruction is self-contained; every sentence changes the investigation or output; the primary question, boundaries, evidence standard, deliverable, and completion criterion are explicit; and no placeholder remains.

## 5. Hand off the research

After the user confirms the instruction, Run `/research` skill with the instruction verbatim. Let `/research` select and verify the relevant specialist; keep this skill focused on framing.

**Done when:** `/research` has accepted the confirmed instruction and reported its result.