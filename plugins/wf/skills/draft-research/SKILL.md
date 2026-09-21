---
name: draft-research
description: Drafts a decision-ready research request through a focused interview. Use when the user wants to frame, scope, or refine a research question before running `/research`.
disable-model-invocation: true
---

# Draft Research

Work **decision-backwards**: identify what the findings must let the user decide, explain, design, or do, then shape the investigation around the evidence needed for that outcome. Produce a confirmed research instruction; run the research only if the user asks after confirmation.

## Research tree

Map the request as a **research tree**: each unresolved choice branches into the choices that depend on it. Seed the tree from everything the user already supplied: outcome, primary question, subject and anchors, boundaries, constraints, suspected answer, comparison criteria, source material, and permitted access.

Keep the tree abstract. Open only branches that can change where the researcher looks, which options remain viable, or what evidence settles a claim. Subject-specific details belong only when they can change the conclusion or its applicability; `/research` and its specialists own domain procedures.

Rank unresolved branches by decision risk: feasibility and hard limitations first, then performance and scale, reliability, security, operational complexity, and lower-risk usability or presentation details. This ordering decides what must be settled now; it is not a checklist that every request must exhaust.

## Facts and decisions

Finding facts is the agent's job. Use supplied sources, the environment, and available tools before asking; an unresolved lookup blocks only branches that depend on it. When a fact needs runtime evidence the current session cannot safely obtain, preserve it as an unknown with the exact probe that could settle it.

Decisions belong to the user: priorities, tradeoffs, boundaries, acceptable evidence, access they control, and the action the findings must support. Ask only when the answer can materially change the research instruction. A preference with a safe, low-consequence default can remain an explicit assumption for confirmation instead of consuming a question.

## Clarify once

Ask one batch of at most three questions, then draft. Questions may cover different topics; select the unresolved decisions whose answers would most improve the instruction's question, scope, constraints, or hypothesis. Three is a ceiling, not a target, and no clarification batch is needed when the supplied context already settles the material choices.

When the VS Code question tool is available, send the whole batch in one call. Give concrete options for real tradeoffs, mark the recommended option, allow a free-form answer unless the choice must be restricted, and keep each prompt focused on one decision. When the tool is unavailable, use this fallback shape:

```markdown
**Q1 — {{short title}}**
{{one decision the user must make}}

**Recommended:** {{answer and one-sentence reason}}
```

Make each recommendation easy to accept in a short reply. If the user accepts it without elaborating, treat it as their answer; if they skip a non-critical choice, carry the recommendation as an explicit assumption in the draft.

Do not ask a second clarification batch. Resolve dependent or lower-risk details from the answers, available facts, and recommended defaults; expose any decision-relevant inference as an assumption beside the draft. Turn expected answers into hypotheses and put disconfirming evidence in the instruction rather than asking the user how to test them.

Do not ask about facts the researcher can discover, choices that only alter wording, or details a specialist can resolve without changing scope. Present remaining assumptions with the draft so confirmation closes them together.

**Done when:** the single batch is answered or unnecessary, every material unresolved choice is exposed as an assumption, and every undiscovered fact is represented by a concrete probe.

## Draft the instruction

Write one short, standalone prose instruction per **research unit**. Questions share a unit when they use the same boundaries and constraints; split them when those differ. Use one to four sentences without headings or lists.

Use this template. **Question** is required; **Scope**, **Constraints**, and **Hypothesis** are optional and appear only when they materially guide the investigation. Replace every placeholder and keep each included marker as part of its sentence so the instruction remains scannable prose:

```markdown
**Question:** Research {{subject and concrete anchors}} to determine {{primary question}} so that {{decision, explanation, design, or action the findings must support}}.

**Scope:** Start at {{entry point, earliest date, or initial boundary}}, stop at {{observable outcome, terminal boundary, cutoff, or sufficient evidence}}, include {{decision-relevant branches, options, environments, or concerns}}, and exclude {{explicit non-goals}}.

**Constraints:** Evaluate within {{scale, latency, cost, deployment, skills, security, compatibility, freshness, access, or other limits that can change the answer}}, mapping realistic options broadly and testing feasibility and hard limitations before lower-risk detail.

**Hypothesis:** Test {{expected answer or assumption}} against {{evidence that would confirm it}} and {{evidence that would disconfirm it}}, using {{safe probe or experiment}} if documentary evidence cannot settle the claim.
```

Do not prescribe source hierarchy, citations, document shape, output location, findings taxonomy, or specialist stopping criteria. `/research` and the selected `research-*` skill own those choices.

The strategy must direct the researcher to map realistic options broadly, test high-risk unknowns before low-risk detail, deepen only viable branches, prune branches after decisive findings, and use a safe probe when documentary evidence cannot settle a decision-relevant claim.

Present the instruction with its explicit assumptions and ask the user to confirm or correct it. The draft is ready when it is self-contained; every sentence changes the investigation; the primary question, boundaries, constraints, and hypothesis are explicit where relevant; and no placeholder remains.

## Confirm and hand off

Do not start the investigation before the user confirms shared understanding. After confirmation, ask whether to Run `/research` skill. If the user declines, return the reusable instruction and stop. If the user accepts, pass each confirmed instruction to `/research` verbatim and let it select and verify the relevant specialist.

**Done when:** the user has the confirmed instruction and, when requested, `/research` has reported its result.