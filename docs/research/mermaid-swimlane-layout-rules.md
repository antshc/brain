# Mermaid swimlane layout rules

Rules for the swimlane and flowchart templates of the behavior-diagram skill, so elements render in flow order. The layout engine ranks nodes by edges, not by declaration order; a cycle makes it reverse the wrong edge, which pushes the start node to the middle and later steps to the top.

## Drawing rules: layout order

- The layout engine ranks nodes by edges, not by declaration order. Reordering nodes or edges never fixes placement; fix the graph shape.
- Keep the graph acyclic. A repeat or retry is drawn as a terminal connector node in the owning lane (`([Next iteration - back to step N])`), never as an edge back to an earlier node.
- Give each external system or data store one node per use (read, refresh, write). A single shared store node used both early and late closes a cycle through the store.
- Mark each store node by use, e.g. `issuesRead`, `issuesWrite`.
- Every process has exactly one start node with no incoming edge, and it is the first node declared.
- End and exit nodes have no outgoing edge. Several failure branches may share one `exit` node, but not a node that also feeds a later step.
- Declare nodes in flow order within each lane, and list edges in flow order, main path first, branches after. This does not control placement, but it keeps the diagram reviewable.
- Number steps in flow order (`1 - …`, `8.2.1 - …`). Write `N - text`, never `N. text`, because Mermaid reads `N.` as a markdown list and fails.

## Validation: done when

- The diagram has no cycle: every edge goes from an earlier step to a later step, and loop-backs are terminal connector nodes.
- No store or external-system node has both an incoming edge from a late step and an outgoing edge to an early step.
- Rendered, the start node is the topmost node and the end nodes are the bottommost.
- Rendered, step numbers increase down the page along the main path.
- Rendering exits 0 with the target Mermaid version. A render failure is fixed, not worked around by dropping the diagram.

## Render check

```bash
npx -y @mermaid-js/mermaid-cli -i diagram.mmd -o diagram.svg
```

Read the `translate(x, y)` of each `<g class="node …">` in the SVG. The start node's `y` must be the smallest, and the `y` values must follow the step order. If they don't, look for a back-edge or a shared store node, remove the cycle, and render again.
