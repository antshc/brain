---
name: draft-research
description: Drafts a research brief through a structured interview.
disable-model-invocation: true
---

# Draft Research

Turn an initial topic into a decision-ready, Google-style one-pager. The brief defines what research must answer and why; the research skill owns evidence strategy, sources, citations, experiments, findings, and conclusions.

## 1. Grill the scope

Run `/grilling` skill over the user's request and the available context. Treat these as the research tree:

- **Frame the Question** — required. Resolve the subject and the decision, explanation, design, or action the findings must support.
- **Set Constraints** — resolve only limits that can change the answer.
- **Map the Space** — resolve which approaches, alternatives, or boundaries need broad coverage.
- **Create Hypotheses** — derive falsifiable claims only when their truth can change the decision.
- **Rank Unknowns by Risk** — order unresolved questions by their power to invalidate an approach: feasibility and hard limitations, performance and scale, reliability, security, operational complexity, then developer ergonomics.
- **Deep Only Where Needed** — define which viable branches deserve depth and what finding prunes each branch.
- **Stopping Criteria** — define observable conditions under which further research is unlikely to change the decision.

Ask only questions that can change the research scope or plan. Use facts already present in the conversation or discoverable from the environment; preserve unresolved factual claims as unknowns for the research. Keep the six branches after **Frame the Question** optional and close each one as soon as it adds no decision value.

**Done when:** the user confirms shared understanding, the question names both subject and intended outcome, and no unresolved branch can materially change the brief.

## 2. Draft the one-pager

Write a self-contained Markdown brief of about 500 words or fewer. Use **Research Question** as the only mandatory heading. Add the other headings only when they sharpen the investigation; omit empty and not-applicable sections.

```markdown
# {{concise research title}}

## Research Question
{{subject to investigate, question to answer, and outcome the answer must support}}

## Constraints
{{decision-changing boundaries and non-goals}}

## Map the Space
{{realistic approaches, alternatives, and breadth boundaries}}

## Hypotheses
{{falsifiable, decision-relevant claims}}

## Ranked Unknowns
{{risk-ordered investigation sequence, with deeper work gated by earlier findings}}

## Deep Only Where Needed
{{branches to deepen and conditions that prune them}}

## Stopping Criteria
{{observable conditions for a decision-ready result}}
```

Encode the plan in **Ranked Unknowns** rather than adding a separate plan section. Keep evidence strategy out of the brief so `/research` and its selected specialist can choose the appropriate sources and methods.

Present the draft and ask the user to confirm or correct it. Resume `/grilling` when a correction exposes an unresolved branch.

**Done when:** every included section changes the investigation, the brief stays near the one-page limit, no placeholder remains, and the user confirms it.

## 3. Persist and hand off

Write the confirmed brief to `/memories/session/research-brief.md`, replacing the previous current brief, then display it to the user.

Ask whether to Run `/research` skill. On acceptance, pass the confirmed brief verbatim as the research request. On decline, stop with the displayed brief available for later use.

**Done when:** the session file matches the displayed brief and any accepted research handoff uses that exact content.