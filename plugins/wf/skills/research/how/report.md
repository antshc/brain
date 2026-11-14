# How report

Produce one current-system explanation per question, inline or saved. Give a senior engineer context to trace the mechanism and find its source.

## Answer

Lead with the direct answer in one or two short paragraphs. Name the outcome and the condition or boundary that determines it. Frame the answer and scope in domain terms before introducing implementation details.

## How it works

Explain trigger to outcome; define concepts when they first matter. Name concrete services, calls, decisions, and data needed to follow the trace. Keep narrow answers short.

Integrate relevant Behavior, Flow, and Data findings into this explanation. Include the lane decision, storage detail, or provider rule that changes the answer at the point where it matters. Explain each step once. Add a diagram or table when it clarifies relationships or comparisons. Follow the applicable lens and diagram guidance and render every included Mermaid block.

## Visualize

Choose from confirmed evidence: topology/ownership → container or swimlane; interaction order → sequence; selection/failure → flowchart; data shape → table or class view. Prefer prose or a table when clearer. *Load and follow the `doc-diagram` skill to create Mermaid architecture, process flow, or class diagrams* using only the selected view's guidance. No lens requires a diagram type.

Back nodes/crossings with evidence; label unresolved edges. Keep file/line detail in nearby citations. Split crowded views by question; render every Mermaid block or name the rendering blocker.

## Additional sections

Include only needed sections, e.g. **Where things live**, **Failures and edge cases**, **Runtime observations**, **Assumptions and unknowns**. Give observations’ environment/check and unresolved claims’ blocker/exact next check. Explain non-obvious behavior where it changes the answer.

## Report checks

- Cite each material claim in place. Use repository links such as `[orders.py](../../src/orders.py#L42):L42-54`. Resolve relative source links from the actual caller-selected report location; for inline answers use source links the caller can open. Use the filename as the label and show the line or range outside the link. For repository permalinks to locally inspected source, pin the inspected commit and line. Quote the deciding line when it helps.
- Reconcile conflicting evidence before writing. Distinguish executing source, documented intent, and observations from a specific runtime. Label assumptions and unknowns.
- Honor `@outputShape` framing. Research owns delivery under Caller-owned destinations; use only its resolved caller-supplied `@outputPath` when saving. Define no output directory, filename, or lens suffix here.
- Remove placeholders and unused sections. Report the saved path when saved, otherwise the inline answer; include material gaps.
