<!-- @: Rules: select one mode block; repeat topic subsections as needed; remove unused sections, placeholders and authoring directives from rendered pages. -->
<!-- @: Rules: preserve caller-owned structures and markers; updates retain unaffected content unless restructuring was requested. -->
<!-- @: Rules: standalone pages use one H1 and logical heading levels; fragments keep their owner's format; headings name navigable sections and short labels stay within sections. -->
<!-- @: Rules: use language-tagged code fences, numbered sequences, bullets for unordered items and tables for comparisons or structured facts. -->
<!-- @: Rules: prefer relative repository links; preserve destination-specific link constraints and TOC markers; GitHub needs no literal [TOC] directive. -->
<!-- @: Rules: unknown is not inapplicable; report missing facts separately; never invent content to fill optional sections. -->
<!-- @: Rules: troubleshooting follows main content and verification, before related documentation; retain evidence-supported causes and conditional fixes only. -->
<!-- @: Rules: each troubleshooting case needs symptom, diagnostic checks, conditional resolution and success verification; escalation requires a supplied path. -->
<!-- @: Rules: link extensive troubleshooting separately; create additional pages only within caller scope. -->

# {{title|Task or subject in sentence case}}

{{introduction|Required. Purpose, scope and intended result in 1–3 sentences.}}

<!-- @: OPTIONAL Audience; include when required expertise is unclear from the opening. -->
## Audience

{{audience|Required background.}}

<!-- @: OPTIONAL table of contents; include for long pages only when the renderer needs an inline TOC; use supported syntax. -->

<!-- @: OPTIONAL Prerequisites; include required access, versions, tools, prior knowledge or initial state before dependent actions. -->
## Prerequisites

- {{prerequisite|Actual dependency.}}

<!-- @: REQUIRED main content; select exactly one of the following four mode blocks and remove the others. -->

<!-- @: TUTORIAL block; show the learning result and guided walkthrough with observable checkpoints; link substantial explanation separately. -->
## {{learningTask|What the learner builds}}

{{learningResult|Concrete learning result.}}

1. {{guidedAction|Action and expected observable result.}}

<!-- @: HOW-TO block; solve one task with ordered actions; include branches, cleanup or recovery only when relevant. -->
## {{task|Verb phrase describing the task}}

1. {{action|One action with supplied exact commands or UI labels.}}

<!-- @: REFERENCE block; organize facts like the documented system; include applicable fields, options, defaults, limits and errors; link procedures separately. -->
## {{referenceSubject|Component, option group or interface}}

{{referenceFacts|Verified technical facts.}}

<!-- @: EXPLANATION block; answer one why question with context and reasoning; include supported history, decisions, alternatives and tradeoffs when relevant. -->
## {{concept|Concept or design question}}

{{reasoning|Context, constraints and rationale.}}

<!-- @: README entry page: within the selected mode, include purpose and paths to getting started and detailed docs; support, contribution and maintenance links are optional. -->

<!-- @: REQUIRED verification content for tutorial/how-to; omit this heading when checks are already in steps; omit for reference/explanation unless requested. -->
## Verify the result

{{successCheck|Action, observable result and interpretation.}}

<!-- @: OPTIONAL Examples; include concrete examples that clarify facts or use; tutorial examples belong in the walkthrough. -->
## Examples

{{examples|Realistic examples; tag code fences with their language.}}

<!-- @: OPTIONAL Limitations; include verified boundaries or unsupported cases affecting use. -->
## Limitations

- {{limitation|Relevant bound or unsupported case.}}

<!-- @: OPTIONAL Troubleshooting; include known failure symptoms with supported diagnostic and recovery actions; omit when no useful cases are supplied. -->
## Troubleshooting

<!-- @: Repeat per supported case; use the recognizable symptom or exact error as the heading; preserve commands and log strings exactly in code formatting. -->
### {{symptom|Recognizable symptom or exact error message}}

{{observation|What the reader observes and when it occurs.}}

1. {{diagnosticCheck|Check and what its result establishes; identify cause as confirmed only when evidence confirms it.}}
2. {{resolution|Supported corrective action and the condition under which it applies.}}
3. {{verification|Observable confirmation that the problem is resolved.}}

<!-- @: OPTIONAL Related documentation; include relevant background, tasks, reference or next pages only. -->
## Related documentation

- [{{linkText|Specific destination title}}]({{target|Relative path or external URL}})
