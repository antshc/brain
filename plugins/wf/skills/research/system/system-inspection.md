# System inspection

Inspector contract for a codebase part. Source of truth is this repo, not the web. Output: one Markdown file, every claim cited with a filename-only file reference whose line numbers remain visible.

Inspection documents **as-built**: current state, never a delta.

## Contents

- Codebase lookups
- Axes
- Crossing axes
- Evidence ladder
- Claim types
- File references
- Runtime checks
- Gotchas

## Codebase lookups

**MUST** *run `explore-codebase` skill for every codebase lookup — read-only, multi-repo targets, deployables index, graphify, symbol, flow, and config evidence*; never search directly. It owns contract material, target resolution, graph coverage, and tool selection. Start from the brief's planned lookups; add any it missed. Spawn one explore subagent per independent lookup; run dependent lookups in order. Pass each this Request:

- `@work`: question, prefixed `Exact literal \`X\`:`, `Symbol \`Type.Member\`:`, or `Names unknown:`.
- `@shape` and `@depth`: from the table below.
- `@target`: deployable or repository names as stated.
- `@outputShape`: `file:line — claim` rows, so citations need no re-search.
- `[@inputs]`: the graph health line returned by the first lookup.

| Lookup | `@shape` | `@depth` |
|---|---|---|
| Flow: handoffs, next handler, deployables a message crosses | `relationship` | `thorough` |
| Behavior: trigger → executing symbol chain, names unknown | `relationship` | `medium` |
| Behavior: known symbol's callers, implementations, double vs real | `symbol` | `medium` |
| Data: writers and readers of an item or store | `relationship` | `medium` |
| Citation line, config key, route path, table or queue name | `literal` | `quick` |

The inspector structures and cites what lookups return; the inspection document is the only file written.

## Axes

Three axes, one per unit of inspection. A capability is the stable product ability in context; its features and functional slices realize it. One functional slice belongs to one deployable: Behavior inspects that slice, Flow traces the contracts connecting related slices across deployables, Data inspects one data boundary. Load only the brief's axis reference and template; leave the other two unread.

Write to the axis reference's output path unless `@outputShape` names a location. Every path is flat: one file directly in `docs/researches/<slug>`, no subfolder. Fill the axis template, obeying its `**Rules**` blocks and deleting every one of them from the result.

Before drafting any diagram, run its owning skill for syntax and styling; never compose Mermaid from memory. Render every Mermaid block before declaring the inspection complete.

## Crossing axes

- A Flow run ends at the chain document. Add a Behavior follow-up only when the framed outcome depends on a lane's internal decision and its boundary contracts do not explain it. Record the lane, rationale, exact question, inbound contract, and expected outbound contracts.
- Run the Behavior axis only after the user requests a listed follow-up. Write `docs/researches/<slug>/{{chainSlug}}-chain-{{n}}-{{deployable}}.md` beside the chain file; pass the follow-up question verbatim, use its inbound contract as the entry point, use its expected outbound contracts to bound observable outcomes, and link the result from that follow-up row.
- A Flow or Behavior inspection that reaches a persistence question whose correctness depends on ownership, keys, consistency, migration, concurrency, retention, or deletion → report it as a Data follow-up for the orchestrator.
- Provider semantics, quotas, and API parameters behind a managed service belong to the provider, not this repo → report them as a cloud follow-up for the orchestrator.

## Evidence ladder

Executing source > passing test exercising this exact path > repo docs (ADR, Concept, README, ARCHITECTURE.md) > config/schema defaults > commit or PR description > code comment > inference.

Tests, comments, and docs state *intent*; only executing code proves *behavior*. When they disagree, record the mismatch as a finding.

IaC and migration files are executing code. An entity class is a *declaration* of shape; the serializer that writes it is the *behavior*.

## Claim types

- **FACT** — confirmed against code, a test, or a runtime check; carries a citation.
- **ASSUMPTION** — plausible, unconfirmed; state why, and what would verify it.
- **UNKNOWN** — a named gap, stated as a concrete next check.
- **CONCLUSION** — the explanation the facts support.

## File references

Format every repository file mention in the inspection document as a filename-only link followed by visible line numbers: `[{{filename}}]({{path relative to the research document}}#L{{line}}):L{{line}}` for one line or `[{{filename}}]({{path relative to the research document}}#L{{start}}):L{{start}}-{{end}}` for a range. Keep only the start-line anchor inside the target; hide the full relative path there and keep the complete line location outside it. Example: `[orders.py](../../src/orders.py#L42):L42-54`. Apply this format in prose, tables, Facts, Gaps, and runtime checks, not only Evidence fields. Place each citation immediately after the claim it supports — never pool citations at the end. Quote the deciding line when short enough to settle the claim on sight. A bare path, symbol, table, or service name is not a citation.

## Runtime checks

Static reading settles what the code *can* do; a runtime check settles what it *does*. Reach for one whenever a claim cannot be closed by reading: run the test, add a temporary log, call the endpoint, read the stored item, collect a correlation id across logs. Discard the check, keep the result.

## Gotchas

- **A `block` mermaid diagram rejects rhombus/diamond node shapes (`{"label"}`)** — the renderer throws. Use `flowchart` for decision shapes.
- **A trace that ends in a double proves the wiring, not the behavior** — an environment, profile, or flag that swaps a real dependency for a mock, stub, in-memory fake, or recorded response makes the contract real and the behavior fictional. Record the double as its own Fact and follow the real implementation for behavior claims.
- **A local development store is not the production store** — an emulator, in-memory fake, or single-node instance answers consistency, lag, and expiry questions differently from the real one, so those claims need production configuration as evidence.
