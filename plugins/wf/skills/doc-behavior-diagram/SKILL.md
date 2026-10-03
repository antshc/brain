---
name: doc-behavior-diagram
description: Document software behavior with a Mermaid flowchart, swimlane diagram, or sequence diagram. Use for process flows, decision paths, config or feature-flag branching, provider selection and fallback, responsibility handoffs and who owns each step, call-chain and interaction order, cross-boundary calls, failure branching, and their deltas.
---

# Behavior Diagram

## When to use

A diagram type named by the caller — the user or the skill that ran this one — is **binding**. Draw that type and skip the selection below. A parent workflow asking for a swimlane is asking for responsibility ownership, and message ordering is not grounds to substitute a sequence diagram for it.

Use this skill to document software behavior as one of:

### Flowchart

Show a process flow, decision path, or component wiring when ownership and message timing are not the primary concern.

### Swimlane Diagram

Show a process divided by responsibility when the key question is: **who owns each step and where does responsibility change?**

Each lane represents one owner of work, such as an actor, team, system/container, component/module, or phase when phase ownership is the purpose of the view. Prefer one primary responsibility axis per diagram.

Use:

- **Solution responsibility** for actors, teams, systems, and containers participating in one process.
- **Internal responsibility** for components/modules inside one container or system.

Use a sequence diagram instead when message or call ordering over time is the primary concern.

### Sequence Diagram

Show interaction order, cross-boundary calls, returns, activation, or failure branching when message order over time matters.

## Reference

Official Mermaid syntax:

- Flowchart: https://mermaid.ai/open-source/syntax/flowchart.html
- Swimlanes: https://mermaid.ai/open-source/syntax/swimlanes.html
- Sequence diagram: https://mermaid.ai/open-source/syntax/sequenceDiagram.html

## 1. Select mode

Use **current mode** by default.

Use **delta mode** when the user asks for a delta or change-focused diagram, including requests such as `diagram the delta`, `show what changed`, `show changes`, or `show added/removed/modified elements`.

- **Current mode:** show the relevant current behavior.
- **Delta mode:** show only added, modified, or removed behavior, plus the minimum unchanged context needed to connect it.

## 2. Select diagram and open its template

### Flowchart

Open [flowchart-template.md](templates/flowchart-template.md).

`orientation := the orientation the caller named — `TD` or `LR`; `TD` when the caller named none`

### Swimlane Diagram

Open [swimlane-diagram-template.md](templates/swimlane-diagram-template.md).

### Sequence Diagram

Open [sequence-diagram-template.md](templates/sequence-diagram-template.md).

Open the selected template before drafting. Follow its drawing, styling, delta, and Mermaid rules; do not compose from memory.

A renderer fallback may change syntax, never semantics: a swimlane falls back to a `flowchart` with one `subgraph` per lane, keeping one lane per owner. It never falls back to another diagram type.

Ground current-state elements in the actual codebase or repository evidence. Do not guess. Show only elements relevant to what is being documented.

**Done when:** the type drawn is the one the caller named when there was one; the selected template was opened this run; the selected diagram follows its rules; a flowchart opens with the caller's `orientation`, or `TD` when none was named; current mode uses the base palette; delta mode uses the diagram-specific delta rules and minimum context; every step is numbered per Step numbering; no unused placeholder or instruction-only comment remains.

### Step numbering

Every step **MUST** carry a hierarchical number written into its label text as `{{stepNo}} - {{label}}`, e.g. `3a.1 - Reject order`. Never `3. Label` — Mermaid parses `N.` as a Markdown list and fails. Mermaid built-ins are not used: `autonumber` is flat, flowchart and swimlane have none.

- Main path — the primary/success path — numbers `1`, `2`, `3` in execution order.
- A decision or branching block is a step; its branches number from it: first branch `3a.1`, `3a.2`; second `3b.1`. Letters follow declaration order.
- Nested branch appends again: `3a.2b.1`.
- A branch rejoining the main path continues main numbering.
- Parallel arms branch the same way as exclusive ones.
- Start/End terminals, lanes, participants, notes, and edge/condition labels stay unnumbered.
- Number the diagram as drawn; in delta mode a removed step keeps its own number in sequence.
- Template-specific placement is in each template's Step numbering rules.

### Layout order (flowchart, swimlane)

The layout engine ranks nodes by edges, not declaration order; a cycle makes it reverse an edge, pushing the start mid-diagram and later steps to the top. Reordering nodes or edges never fixes placement — fix the graph shape.

- Graph **MUST** be acyclic. Draw a repeat/retry as a terminal connector node in the owning lane, `loopBack([Next iteration - back to step N])`, never an edge back to an earlier node.
- One node per use of an external system or data store, id marked by use (`issuesRead`, `issuesWrite`); a shared store node used early and late closes a cycle.
- Exactly one start node, no incoming edge, declared first.
- End/exit nodes have no outgoing edge. Failure branches may share one `exit` node, never a node that feeds a later step.
- Declare nodes in flow order per lane; list edges main path first, branches after — for review, not placement.

## 3. Assign a diagram id

`diagramId := kebab-case id naming this diagram's subject and view, unique within the file it lands in, e.g. `order-submission-sequence``

Write it as `%% diagram-id: {{diagramId}}` on its own line — after the `%%{init: …}%%` theme directive and immediately above the `flowchart`/`swimlane-beta`/`sequenceDiagram` line, as the output template shows.

The id is the diagram's published identity: `/publish-page` names its Confluence attachment and Draw.io record after it, so a republish replaces that diagram in place. Redrawing a diagram that already carries an id keeps that id; a fresh id publishes a second copy beside the old one.

**Done when:** the diagram carries exactly one `%% diagram-id` line, reused from the diagram it redraws when there is one, and unique among the ids already in the target file.

## 4. Render and check order

**Run `python3 ./scripts/check_layout.py <file>` from this skill's base directory**, where `<file>` is the `.md` holding the diagram or a `.mmd`. It renders every Mermaid block with `npx -y @mermaid-js/mermaid-cli` and, for flowchart and swimlane, checks the rendered SVG: no cycle, one start node first in flow direction, no edge running against flow (`TD`/`TB` down, `LR` right), each step at or after its predecessor (`3` after `2`, `2a.1` after `2`, `2a.2` after `2a.1`). Sequence diagrams are render-checked only.

On `FAIL`, fix the reported cause per Layout order — back-edge or shared store node — and rerun. Never drop the diagram or a step to make it pass.

**Done when:** the script prints `OK` for every diagram written this run and exits 0.
