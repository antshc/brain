# How report

One current-system explanation per question. Give a senior engineer a working mental model and the sources to trace it. Concise → the router applies Explain itself; Detailed/Full → the router sends Explain as the `explainy` worker prompt.

## Explain

Fill the placeholders; send this whole file as the worker prompt.

> {QUESTION}

- Scope and depth — {SCOPE_AND_DEPTH}
- Explorer findings — {EXPLORER_FINDINGS}
- Selected presentation guidance — {INSPECTION_GUIDANCE}
- Requested report framing — {OUTPUT_SHAPE}

**Synthesize.** Lead with the answer. Explain domain concepts before implementation; build the model from trigger to outcome. Merge overlapping findings; explain each step once. Integrate deciding lane behavior, data rules, package implementation, and provider semantics where they change the mechanism. Keep executing source, documented intent, and runtime observations distinct. Preserve assumptions, unknowns, and conflicts; never fill gaps silently. A missing fact that could change the answer → return claim, consequence, and exact check for a bounded `codebase` follow-up. No annotated-source walkthroughs; no unsupported historical rationale.

**Visualize.** Pick the view from the question, using only confirmed evidence; prefer prose or a table when clearer. Diagram → *Load and follow the `doc-diagram` skill to create the selected Mermaid architecture, process flow, or class diagram*. Topology/ownership → container or swimlane; interaction order → sequence; selection/failure branching → flowchart; data structure → table or class view. Flow across two or more deployables → prefer a Swimlane Diagram, one lane per deployable. Label unresolved edges as gaps; keep file/line detail in nearby citations; render every Mermaid block or report the blocker.

**Return** one Markdown draft inline following the sections below. Choose no save destination; write no file.

## Answer

Direct answer in one or two short paragraphs: the outcome and the condition or boundary that determines it, in domain terms.

## How it works

Trigger to outcome; define concepts when they first matter. Name the services, calls, decisions, and data needed to follow the trace; keep narrow answers short. Integrate the lane decision, storage detail, or provider rule at the point it changes the answer. Add a diagram or table when it clarifies relationships.

## Additional sections

Only as needed: **Where things live**, **Failures and edge cases**, **Runtime observations** (environment and check), **Assumptions and unknowns** (blocker and exact next check).

## Report checks

- Cite each material claim in place: `[orders.py](../../src/orders.py#L42):L42-54`, filename as label, line or range outside the link. Resolve relative links from the report location; inline answers use absolute links; permalinks pin the inspected commit. Quote the deciding line when it helps.
- Reconcile conflicting evidence before writing; label assumptions and unknowns.
- Honor the requested framing; remove placeholders and unused sections. Research owns the save location.
