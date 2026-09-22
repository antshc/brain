---
name: inspect-system
description: "Inspect a software system as-built and write a Markdown inspection document citing every claim with filename-only file references and visible line numbers. Use when asked how behavior is implemented inside one deployable, to trace a flow across deployables and document its integration contracts, or to settle a question turning on data — keys, ownership, consistency, migration, concurrency, retention."
---

# Inspect a system

Source of truth is this repo, not the web. Output: one Markdown file, every claim cited with a filename-only file reference whose line numbers remain visible.

Inspection documents **as-built** — current state, never a delta.

## Axes

Three axes, one per unit of inspection. Pick by the unit the question is about, load only that axis's references and template, and leave the other two unread.

Write to the axis's output path unless the user names a location. Every path is flat — one file directly in `docs/ongoing/`, no subfolder. Fill its template, obeying the `**Rules**` blocks and deleting every one of them from the result.

### Behavior — one deployable

Inspect how one behavior is implemented inside a deployable. Start from a trigger, follow the executing symbol chain and decisions, and stop at observable outcomes or deployable boundaries. Pick it for how something works, where a decision is made, what a change touches, or which implementation or double actually serves a call.

- References: [behavior-inspection.md](references/behavior-inspection.md)
- Template: [behavior-inspection-template.md](templates/behavior-inspection-template.md)
- Output: `docs/ongoing/research-{{slug}}.md`, or `docs/ongoing/research-{{chainSlug}}-chain-{{n}}-{{deployable}}.md` when the user asks for a lane of an existing chain

**Diagram:** Pick the diagram from what the question asks, then Run its owning skill for syntax and styling — never compose Mermaid from memory.

| Inspection topic | Draw | Skill |
|---|---|---|
| the call chain end to end — interaction order, cross-boundary calls, returns, failure branching | a **sequence diagram** | `/doc-behavior-diagram` |
| which branch fires — config or feature-flag branching, provider selection and fallback, error and edge paths | a **flowchart** | `/doc-behavior-diagram` |
| who owns each step and where responsibility changes — handoffs across layer, modules, or teams | a **swimlane diagram** | `/doc-behavior-diagram` |
| which deployable units and external systems the capability spans | a **container diagram** | `/doc-architecture-diagram` |
| scope and integration boundary — the actors and external systems around it | a **system context diagram** | `/doc-architecture-diagram` |
| where it runs — hosting, runtime, infrastructure placement | a **deployment view** | `/doc-architecture-diagram` |
| which types implement the interface behind it — inheritance, composition, dependencies | a **class diagram** | `/doc-code-diagram` |

A traced behavior defaults to the **sequence diagram**; Run `/doc-behavior-diagram` skill before drafting it.

Label nodes with the role or step plus one greppable trace keyword — a route path, config key, event or queue name, table name, or interface name. Keep file references in the tables; use class, method, or file names with exact lines in the diagram only when the user asks for them.

Default to one: triggers enter as parallel participants meeting at the convergence point, observable outcomes leave from it. Diagram selector and fallback edges, not the winning path alone. Split only when triggers diverge, selection needs a flowchart, outcomes fire out of band, or the diagram passes roughly 12 participants or 25 messages. Each split carries a heading naming the question it answers and repeats no node.

Render the Mermaid block before declaring the inspection complete. Run `/render-mermaid-png` skill only when the user wants an exported image.

### Flow — cross-deployable chain

Inspect how one system behavior travels across runtime or deployment boundaries. Each lane is one **deployable** — something independently runnable or deployed in production: a process, service, container, function, host workload, or scheduled job — and each crossing identifies its contract. Trace breadth first across every outcome-relevant deployable whose executing source you can open, and end each branch at a system whose source you cannot or whose behavior is outside the framed outcome. Pick it when the behavior crosses a process boundary, or when asked what handles a message next, where it ends, or what contract crosses the wire.

- References: [flow-inspection.md](references/flow-inspection.md)
- Template: [flow-inspection-template.md](templates/flow-inspection-template.md)
- Output: exactly one file, `docs/ongoing/research-{{slug}}-chain.md`. A chain run writes no other document.

**Diagram:** Draw a mandatory **swimlane** with one lane per deployable, 1–5 ordered major-step nodes in each lane, terminal systems as edge lanes, and every cross-lane arrow labelled with its contract. Follow `/doc-behavior-diagram` skill's **Swimlane Diagram** and open its swimlane template before drafting.

Use Mermaid `swimlane-beta`. When the renderer lacks swimlane support, fall back to a `flowchart` with one `subgraph` per lane. A `sequenceDiagram` is not a chain view because it loses the lane ownership this axis exists to show.

Keep file references in the tables and numbered Facts; Summary, diagram, Flow, boundary contracts, and Conclusion trace to those Facts. Add a **container diagram** above the swimlane only when the lane count passes roughly eight and the reader needs the shape first; Run `/doc-architecture-diagram` skill for its syntax and styling. Finish the chain before identifying Behavior follow-ups; lane internals belong only to the requested lane's Behavior-axis document.

Render the Mermaid block before declaring the inspection complete. Done means each deployable has exactly one lane containing 1–5 boundary-relevant major-step nodes, every in-scope branch reaches a terminal at an edge, every internal boundary has emit-, receive-, and binding evidence, and no artifact, script, playbook, chart, or library holds a lane.

### Data — one data boundary

Inspect persistence semantics around one data boundary: the governed item type, its authoritative writer, readers, storage, consistency, concurrency, migration, retention, and deletion behavior. Pick it when the question turns on key design, ownership, stale reads, attribute migration, concurrent writes, retention, or deletion.

- References: [data-inspection.md](references/data-inspection.md)
- Template: [data-inspection-template.md](templates/data-inspection-template.md)
- Output: `docs/ongoing/research-{{slug}}-data.md`

**Diagram:** None by default — the store, key, and shape tables carry the answer. When the user asks for one, pick the diagram from the question and Run its owning skill: `/doc-behavior-diagram` for access order or branching, `/doc-architecture-diagram` for ownership or deployment boundaries, and `/doc-code-diagram` for item types and their relationships. Keep evidence in the tables and render the Mermaid block before declaring the inspection complete.

### Crossing axes

- A Flow run ends at the chain document. Add a Behavior follow-up only when the framed outcome depends on a lane's internal decision and its boundary contracts do not explain it. Record the lane, rationale, exact question, inbound contract, and expected outbound contracts.
- Run the Behavior axis only after the user requests a listed follow-up. Write `docs/ongoing/research-{{chainSlug}}-chain-{{n}}-{{deployable}}.md` beside the chain file; pass the follow-up question verbatim, use its inbound contract as the entry point, use its expected outbound contracts to bound observable outcomes, and link the result from that follow-up row.
- Run the Data axis when either Flow or Behavior inspection reaches a persistence question whose correctness depends on ownership, keys, consistency, migration, concurrency, retention, or deletion.
- Provider semantics, quotas, and API parameters behind a managed service belong to the provider, not this repo: Run `/research-aws` skill or `/research-azure` skill.

## Evidence ladder

Executing source > passing test exercising this exact path > repo docs (ADR, Concept, README, ARCHITECTURE.md) > config/schema defaults > commit or PR description > code comment > inference.

Tests, comments, and docs state *intent*; only executing code proves *behavior*. When they disagree, record the mismatch as a finding.

IaC and migration files are executing code. An entity class is a *declaration* of shape; the serializer that writes it is the *behavior*.

## Claim types

- **FACT** — confirmed against code, a test, or a probe; carries a citation.
- **ASSUMPTION** — plausible, unconfirmed; state why, and what would verify it.
- **UNKNOWN** — a named gap, stated as a concrete next probe.
- **CONCLUSION** — the explanation the facts support.

## File references

Format every repository file mention in the inspection document as a filename-only link followed by visible line numbers: `[{{filename}}]({{path relative to the research document}}#L{{line}}):L{{line}}` for one line or `[{{filename}}]({{path relative to the research document}}#L{{start}}):L{{start}}-{{end}}` for a range. Keep only the start-line anchor inside the target; hide the full relative path there and keep the complete line location outside it. Example: `[orders.py](../../src/orders.py#L42):L42-54`. Apply this format in prose, tables, Facts, Gaps, and probes, not only Evidence fields. Place each citation immediately after the claim it supports — never pool citations at the end. Quote the deciding line when short enough to settle the claim on sight. A bare path, symbol, table, or service name is not a citation.

## Probes

Static reading settles what the code *can* do; a probe settles what it *does*. Reach for one whenever a claim cannot be closed by reading: run the test, add a temporary log, call the endpoint, read the stored item, collect a correlation id across logs. Discard the probe, keep the result.

## Gotchas

- **A `block` mermaid diagram rejects rhombus/diamond node shapes (`{"label"}`)** — the renderer throws. Use `flowchart` for decision shapes.
- **A trace that ends in a double proves the wiring, not the behavior** — an environment, profile, or flag that swaps a real dependency for a mock, stub, in-memory fake, or recorded response makes the contract real and the behavior fictional. Record the double as its own Fact and follow the real implementation for behavior claims.
- **A local development store is not the production store** — an emulator, in-memory fake, or single-node instance answers consistency, lag, and expiry questions differently from the real one, so those claims need production configuration as evidence.
