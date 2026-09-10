# Swimlane Diagram Template

Official Mermaid swimlane syntax: https://mermaid.ai/open-source/syntax/swimlanes.html

## Grounding rules

- Diagram only behavior evidenced by the repository/code, provided documentation, or explicit user input.
- Every lane, step, decision, and handoff must be traceable to evidence.
- Never infer missing behavior from naming, architecture conventions, or the skeleton.
- Do not invent calls, events, responses, data, decisions, failure paths, or ownership.
- If ownership or behavior is unclear, omit it from the diagram and state the uncertainty outside the diagram when relevant.
- Prefer a smaller incomplete-but-evidenced diagram over a complete speculative one.
- Before output, verify that every diagram element has supporting evidence.

## Drawing rules

- Use Mermaid `swimlane-beta` when responsibility for each step and handoffs between owners are design-relevant.
- A lane represents one owner of work: actor, team, system/container, component/module, or phase when phase ownership is the purpose of the view.
- Prefer one primary responsibility axis per diagram. Do not mix unrelated axes such as teams, statuses, phases, containers, and components in one view.
- Mixing owner types is allowed when they participate at the same responsibility level, for example a user, API, and worker in one solution flow.
- Show only decision-relevant lanes and steps.
- Prefer about 3-7 lanes. Split the flow when handoffs become difficult to trace.
- Split a large flow into a solution-responsibility diagram plus one or more internal-responsibility diagrams when needed.
- `swimlane-beta` is experimental in Mermaid 11.16.0+. Confirm the target renderer supports it. If not, fall back to a `flowchart` with one `subgraph` per lane.

## Responsibility views

### Solution responsibility

Use for responsibility across process participants.

- Lanes may be actors, teams, systems, or deployable/runnable containers participating in the same flow.
- Keep lane labels architectural or business-oriented, for example `[Customer]`, `[Order API - REST API]`, `[Fulfillment Worker - Worker]`.
- Group co-deployed artifacts that form one operational unit into one lane. A Linux service plus Bash scripts plus Ansible playbooks it runs is usually one system/container responsibility, not separate lanes.
- Do not decompose internal implementation unless necessary to explain ownership.

### Internal responsibility

Use when ownership inside one system/container matters.

- Scope the diagram to one system/container.
- Each lane is an evidenced component/module such as a controller, service, page, repository, handler, or subsystem.
- Include component name and type when useful, for example `[OrderController - Controller]`.
- Use only when internal ownership or handoffs are decision-relevant.

## Nodes and handoffs

- `id([Text])` — process start/end.
- `id[Text]` — action/activity.
- `id{Text}` — decision.
- Put an action or decision in the lane that owns it.
- Prefer business/process language for steps, such as `Validate order`, `Create order`, or `Persist order`.
- Avoid method-level labels such as `OrderService.placeOrder()` unless implementation detail is explicitly requested.
- A cross-lane edge represents a responsibility handoff.
- Label a cross-lane edge when the handoff payload, event, condition, or outcome adds useful meaning; do not label mechanically.
- Number edges only when execution order would otherwise be ambiguous. If strict temporal ordering is the main concern, use a sequence diagram.
- For mutually exclusive branches, label evidenced outcomes clearly.
- Use short, stable node IDs and descriptive labels.

## Accessibility

Add accessible metadata when producing a standalone diagram:

```mermaid
accTitle: Process responsibility
accDescr: Shows the process steps and responsibility handoffs between participating owners.
```

Keep `accTitle` concise. Use `accDescr` to summarize the process and main responsibility handoffs.

## Current-mode styling

Use the repo dark palette.

```text
lineColor: #8b949e
fill: #242424
stroke: #8b949e
text: #c9d1d9
```

Keep this initialization and default class definition in current mode:

```mermaid
%%{init: {'themeVariables': {'lineColor': '#8b949e'}}}%%
classDef default fill:#242424,stroke:#8b949e,color:#c9d1d9,stroke-width:1px
```

## Delta-mode styling

Apply only when `SKILL.md` selects **delta mode**.

Define:

```mermaid
classDef added stroke:#4a7a5a,stroke-width:1px
classDef removed stroke:#8a4a4a,stroke-width:1px
```

Then style each changed node with a separate statement:

```mermaid
class nodeId added;
class oldNodeId removed;
```

- Swimlane nodes use `class nodeId className;`; do not rely on the inline `id:::class` shorthand.
- A lane that is entirely new or removed has no supported Mermaid `subgraph` border-color hook; call out the lane state in prose.
- Show changed nodes/handoffs plus the minimum unchanged context needed to connect them.
- Omit unchanged lanes and nodes not needed to understand the delta.
- Do not apply delta styling in current mode.

## Mermaid constraints and gotchas

- `swimlane-beta` optionally accepts `TB`, `TD`, `BT`, `LR`, or `RL`; it defaults to `TB`.
- Each top-level `subgraph id [Label] ... end` becomes one lane.
- Avoid parentheses inside `[Label]` lane labels; they can break parsing.
- Do not use curly braces inside node label text for placeholders; Mermaid interprets `{` as a decision-node delimiter.
- Never use `click` as a node ID; it is a reserved Mermaid interaction keyword.
- Use separate `class` statements for swimlane node styling.
- Delete unused lanes and nodes from the final diagram.

## Minimal skeleton

Use this only as a syntax scaffold, never as a content checklist. Remove or replace every element not supported by evidence. Add only evidenced lanes, steps, decisions, and handoffs.

```mermaid
%%{init: {'themeVariables': {'lineColor': '#8b949e'}}}%%
swimlane-beta TB
  accTitle: Process responsibility
  accDescr: Shows responsibility handoffs in the process.

  subgraph ownerA [Owner A]
    stepA[Action]
  end

  subgraph ownerB [Owner B]
    stepB[Action]
  end

  stepA -->|handoff| stepB

  classDef default fill:#242424,stroke:#8b949e,color:#c9d1d9,stroke-width:1px
```
