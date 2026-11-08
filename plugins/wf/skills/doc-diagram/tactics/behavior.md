# Behavior Diagram

## Flowchart

Show a process flow, decision path, or component wiring when ownership and message timing are not the primary concern.

## Swimlane Diagram

Show a process divided by responsibility when the key question is: **who owns each step and where does responsibility change?**

Each lane represents one owner of work, such as an actor, team, system/container, component/module, or phase when phase ownership is the purpose of the view. Prefer one primary responsibility axis per diagram.

Use:

- **Solution responsibility** for actors, teams, systems, and containers participating in one process.
- **Internal responsibility** for components/modules inside one container or system.

Use a sequence diagram instead when message or call ordering over time is the primary concern.

## Sequence Diagram

Show interaction order, cross-boundary calls, returns, activation, or failure branching when message order over time matters.

## Reference

Official Mermaid syntax:

- Flowchart: https://mermaid.ai/open-source/syntax/flowchart.html
- Swimlanes: https://mermaid.ai/open-source/syntax/swimlanes.html
- Sequence diagram: https://mermaid.ai/open-source/syntax/sequenceDiagram.html

## Rendering

Use the caller's `TD` or `LR` orientation for a Flowchart. Default to `TD`.

If the renderer requires a swimlane fallback, use a `flowchart` with one `subgraph` per lane. Keep lane ownership and handoffs.

Put `%% diagram-id: {{diagramId}}` after the `%%{init: …}%%` theme directive and immediately above the Mermaid type line.

## Step numbering

Every step **MUST** carry a hierarchical number written into its label text as `{{stepNo}} - {{label}}`, e.g. `3a.1 - Reject order`. Never `3. Label` — Mermaid parses `N.` as a Markdown list and fails. Mermaid built-ins are not used: `autonumber` is flat, flowchart and swimlane have none.

- Main path — the primary/success path — numbers `1`, `2`, `3` in execution order.
- A decision or branching block is a step; its branches number from it: first branch `3a.1`, `3a.2`; second `3b.1`. Letters follow declaration order.
- Nested branch appends again: `3a.2b.1`.
- A branch rejoining the main path continues main numbering.
- Parallel arms branch the same way as exclusive ones.
- Start/End terminals, lanes, participants, notes, and edge/condition labels stay unnumbered.
- Number the diagram as drawn; in delta mode a removed step keeps its own number in sequence.
- Template-specific placement is in each template's Step numbering rules.

## Layout order (flowchart, swimlane)

The layout engine ranks nodes by edges, not declaration order; a cycle makes it reverse an edge, pushing the start mid-diagram and later steps to the top. Reordering nodes or edges never fixes placement — fix the graph shape.

- Graph **MUST** be acyclic. Draw a repeat/retry as a terminal connector node in the owning lane, `loopBack([Next iteration - back to step N])`, never an edge back to an earlier node.
- One node per use of an external system or data store, id marked by use (`issuesRead`, `issuesWrite`); a shared store node used early and late closes a cycle.
- Exactly one start node, no incoming edge, declared first.
- End/exit nodes have no outgoing edge. Failure branches may share one `exit` node, never a node that feeds a later step.
- Declare nodes in flow order per lane; list edges main path first, branches after — for review, not placement.

## Render and check order

**Run `python3 ./scripts/check_layout.py <file>` from this skill's base directory**, passing the absolute path to the `.md` holding the diagram or to the `.mmd`. It renders every Mermaid block with `npx -y @mermaid-js/mermaid-cli` and, for flowchart and swimlane, checks the rendered SVG: no cycle, one start node first in flow direction, no edge running against flow (`TD`/`TB` down, `LR` right), each step at or after its predecessor (`3` after `2`, `2a.1` after `2`, `2a.2` after `2a.1`). Sequence diagrams are render-checked only.

On `FAIL`, fix the reported cause per Layout order — back-edge or shared store node — and rerun. Never drop the diagram or a step to make it pass.

**Done when:** the script prints `OK` for every diagram written this run and exits 0.
