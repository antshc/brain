---
name: define
description: >-
  Define a research map or an arc42 Crosscutting Concept. Use 'define research' to chart or resume research and hypothesis topics, or 'define concept' to discover, question, and record a Concept against codebase evidence.
argument-hint: "research {{researchPromptOrMapPath}} | concept {{conceptOrContext}}"
---

# Define

Route the request to exactly one procedure. Read that route and every reference it requires in full; do not load the other route.

| Request | Route |
|---|---|
| Chart or resume a research map, list unknowns or hypotheses to resolve | [Research](references/research.md) |
| Define, improve, or recommend an arc42 Crosscutting Concept | [Concept](references/concept.md) |

Explicit `research` or `concept` arguments win. Otherwise infer from the requested artifact: a research map under `docs/ongoing/` selects Research; a Crosscutting Concept or architecture default selects Concept. Ask when neither is clear.

Both routes use [Questioning](references/questioning.md). Research maps only evidence work and hands off decisions; Concept confirms decisions; *run `doc-architecture` skill to record settled architecture* with route `concept-record`.
