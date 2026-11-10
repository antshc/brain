# How

Use this template for every saved answer about current system behavior. Write one Markdown document per system question. Give a senior engineer enough context to trace the mechanism and find the source.

## Answer

Lead with the direct answer in one or two short paragraphs. Name the outcome and the condition or boundary that determines it. Frame the answer and scope in domain terms before introducing implementation details.

## How it works

Explain the mechanism from trigger to outcome. Define key concepts when they first matter. Name concrete services, calls, decisions, and data where they help the reader follow the trace. Keep a narrow answer short.

Integrate relevant Behavior, Flow, and Data findings into this explanation. Include the lane decision, storage detail, or provider rule that changes the answer at the point where it matters. Explain each step once. Add a diagram or table when it clarifies relationships or comparisons. Follow the applicable lens and diagram guidance and render every included Mermaid block.

## Additional sections

Include only sections the question needs, such as **Where things live**, **Failures and edge cases**, **Runtime observations**, or **Assumptions and unknowns**. Report observed results with the environment and check used. For an unresolved claim, name the blocker and the exact next check. Explain non-obvious behavior where it changes the answer.

## Report checks

- Cite each material claim in place. Use repository links such as `[orders.py](../../src/orders.py#L42):L42-54`. Use the filename as the label and show the line or range outside the link. For remote source, pin the commit and line. Quote the deciding line when it helps.
- Reconcile conflicting evidence before writing. Distinguish executing source, documented intent, and observations from a specific runtime. Label assumptions and unknowns.
- Honor the requested `@outputShape` path and framing in one document. Use `docs/research/<slug>-chain.md` for single-axis Flow and `docs/research/<slug>-data.md` for single-axis Data. Use `docs/research/<slug>.md` for focused, Behavior, and combined work.
- Remove placeholders and unused sections. Report the saved path and material gaps.
