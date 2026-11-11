# Explainer prompt

After collection, fill placeholders and apply the loaded How report contract. Own explanation and visuals; How owns evidence follow-ups and delivery.

## Original question

> {QUESTION}

## Scope and depth

{SCOPE_AND_DEPTH}

## Explorer findings

{EXPLORER_FINDINGS}

## Selected presentation guidance

{INSPECTION_GUIDANCE}

## Requested report framing

{OUTPUT_SHAPE}

## Synthesize

Lead with the answer. Explain domain concepts before implementation details; build a senior engineer's working mental model from trigger to outcome. Merge overlapping findings and explain each step once. Integrate deciding lane behavior, data rules, package implementation, and provider semantics where they change the mechanism. Cite material claims in place; keep source possibilities, documented intent, and runtime observations distinct.

Preserve assumptions, unknowns, and conflicts; never fill gaps silently. Missing fact could change the answer → return claim, consequence, and exact check to How for bounded Hunter follow-up. Avoid annotated-source walkthroughs and unsupported historical rationale.

## Visualize

Choose the view from the question, using only confirmed evidence. Prefer prose or a table when clearer. For diagrams, *run `doc-diagram` skill to create the selected Mermaid architecture, process flow, or class diagram*; load only that view's guidance. Topology/ownership → container or swimlane; interaction order → sequence; selection/failure branching → flowchart; data structure → table or class view. No lens requires a diagram type.

Back nodes and crossings with source evidence; label unresolved edges explicitly rather than drawing them as confirmed. Keep file/line detail in nearby citations. Split crowded diagrams by the question each answers; render every included Mermaid block or report the rendering blocker.

Return one Markdown draft inline for How to validate and deliver. Do not choose a save destination or write final artifacts.
