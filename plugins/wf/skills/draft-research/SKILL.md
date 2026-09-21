---
name: draft-research
description: Drafts a decision-ready research request through a focused interview. Use when the user wants to frame, scope, or refine a research question before running `/research`.
disable-model-invocation: true
---

# Draft Research

Work **decision-backwards**: identify what the findings must let the user decide, explain, design, or do, then shape the investigation around the evidence needed for that outcome. Produce a confirmed research instruction; run the research only if the user asks after confirmation.

## Research tree

Map the request as a **research tree**: each unresolved choice branches into the choices that depend on it. Seed the tree from everything the user already supplied: outcome, primary question, subject and anchors, boundaries, constraints, suspected answer, comparison criteria, source material, permitted access, audience, deliverable, and completion condition.

Keep the tree abstract. Open only branches that can change where the researcher looks, which options remain viable, what evidence settles a claim, what the deliverable contains, or when the investigation stops. Subject-specific details belong only when they can change the conclusion or its applicability; `/research` and its specialists own domain procedures.

Rank unresolved branches by decision risk: feasibility and hard limitations first, then performance and scale, reliability, security, operational complexity, and lower-risk usability or presentation details. This ordering decides what must be settled now; it is not a checklist that every request must exhaust.

## Facts and decisions

Finding facts is the agent's job. Use supplied sources, the environment, and available tools before asking; an unresolved lookup blocks only branches that depend on it. When a fact needs runtime evidence the current session cannot safely obtain, preserve it as an unknown with the exact probe that could settle it.

Decisions belong to the user: priorities, tradeoffs, boundaries, acceptable evidence, access they control, and the action the findings must support. Ask only when the answer can materially change the research instruction. A preference with a safe, low-consequence default can remain an explicit assumption for confirmation instead of consuming another round.

## Interview the frontier

The **frontier** is every unresolved decision whose prerequisites are settled: the questions that can be answered now without guessing at another answer. Ask at most three independent frontier questions per round, then wait. Three is a ceiling, not a target; draft immediately when the supplied context already settles the material choices.

Use this shape:

```markdown
**Q1 — {{short title}}**
{{one decision the user must make}}

**Recommended:** {{answer and one-sentence reason}}
```

Offer concrete options only when they expose a real tradeoff. Make the recommendation easy to accept in a short reply. If the user accepts the recommendation without elaborating, treat it as their answer; if they skip a non-critical choice, carry the recommendation as an explicit assumption in the draft.

Each answer reshapes the tree. Recompute the frontier, open only the branches it unblocks, and never ask a dependent question in the same round as its unresolved prerequisite. Turn expected answers into hypotheses and put disconfirming evidence in the instruction rather than repeatedly asking the user how to test them.

Stop when the frontier contains no material user decision. Do not prolong the interview for facts the researcher can discover, choices that only alter wording, or details a specialist can resolve without changing scope. Present remaining assumptions with the draft so confirmation closes them together.

**Done when:** every material user decision is answered or exposed as an assumption, every discoverable fact is resolved or represented by a concrete probe, and no dependent branch remains silently assumed.

## Draft the instruction

Write one short, standalone prose instruction per **research unit**. Questions share a unit when they use the same boundaries, evidence, and deliverable; split them when any of those differ. Use one to five sentences without headings or lists unless the user requests a structured format.

Use this template. Replace every placeholder, omit any optional sentence that adds nothing, and keep each marker as part of its sentence so the instruction remains scannable prose:

```text
Question: Research {{subject and concrete anchors}} to determine {{primary question}} so that {{decision, explanation, design, or action the findings must support}}.
Scope: Start at {{entry point, earliest date, or initial boundary}}, stop at {{observable outcome, terminal boundary, cutoff, or sufficient evidence}}, include {{decision-relevant branches, options, environments, or concerns}}, and exclude {{explicit non-goals}}.
Constraints: Evaluate within {{scale, latency, cost, deployment, skills, security, compatibility, freshness, access, or other limits that can change the answer}}, mapping realistic options broadly and testing feasibility and hard limitations before lower-risk detail.
Hypothesis: Test {{expected answer or assumption}} against {{evidence that would confirm it}} and {{evidence that would disconfirm it}}, using {{safe probe or experiment}} if documentary evidence cannot settle the claim.
Evidence and output: Prefer {{source hierarchy}}, distinguish {{facts, assumptions, unknowns with next probes, and conclusions as useful}}, deliver {{audience, format, location, views, and citation style}}, and stop when {{critical unknowns are resolved or exposed, viable options are comparable, major risks are understood, and further research is unlikely to change the decision}}.
```

Prefer primary evidence: executing source or a safe experiment for observed behavior, then official documentation, specifications, first-party APIs, official issues or design documents, maintainer material, and only then credible secondary sources. Adapt the hierarchy to the subject instead of forcing unavailable source classes.

The strategy must direct the researcher to map realistic options broadly, test high-risk unknowns before low-risk detail, deepen only viable branches, prune branches after decisive findings, and use a safe probe when documentary evidence cannot settle a decision-relevant claim. Record findings as they are confirmed rather than reconstructing the evidence trail at the end.

Present the instruction with its explicit assumptions and ask the user to confirm or correct it. The draft is ready when it is self-contained; every sentence changes the investigation or output; the primary question, boundaries, strategy, evidence standard, deliverable, and completion criterion are explicit; and no placeholder remains.

## Confirm and hand off

Do not start the investigation before the user confirms shared understanding. After confirmation, ask whether to Run `/research` skill. If the user declines, return the reusable instruction and stop. If the user accepts, pass each confirmed instruction to `/research` verbatim and let it select and verify the relevant specialist.

**Done when:** the user has the confirmed instruction and, when requested, `/research` has reported its result.