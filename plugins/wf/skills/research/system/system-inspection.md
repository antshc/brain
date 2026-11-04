# System inspection

Inspect the **as-built** state using target repositories and restored packages as primary sources. Write one Markdown file with cited claims. Use File references for repository citations.

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

**MUST** delegate repository lookups. Extend the brief with missing lookups. Spawn one read-only subagent per independent lookup. Sequence dependent lookups. Instruct each to *run `explore-codebase` skill for symbol, callers, flow, literal, or config evidence*. If the skill is unavailable, spawn the explore agent with the same Request and read-only contract. Pass each Request:

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
| Isolated symbol or package call site | `symbol` | `quick` |
| Citation line, config key, route path, table or queue name | `literal` | `quick` |

For NuGet-owned claims or evidence, delegate a lookup to *run `inspect-nuget-source` skill to verify the package API or behavior from XML docs or decompiled code*. Cite the resolved package ID, version, type or member, and evidence source. Missing package evidence → mark unknown.

Structure and cite returned evidence. Write only the inspection document.

## Axes

A capability is a stable product ability realized by features and functional slices. Each slice belongs to one deployable. Behavior inspects one slice. Flow traces contracts across slices in different deployables. Data inspects one data boundary. Load only the selected axis reference and template. For isolated lookups or package API questions, write a focused Markdown report with cited findings and unknowns in `docs/research/` unless `@outputShape` sets the path.

Write one file at the axis reference's output path directly in `docs/research/<slug>` unless `@outputShape` names a location. Fill the axis template, obey its `**Rules**` blocks, and remove them from the result.

Run the diagram’s owning skill for syntax and style before drafting. Render every Mermaid block before completion.

## Crossing axes

- End Flow at the chain document. Add a Behavior follow-up only when a lane's internal decision determines the framed outcome and boundary contracts leave it unexplained. Record the lane, rationale, exact question, inbound contract, and expected outbound contracts.
- Run the Behavior axis only after the user requests a listed follow-up. Write `docs/research/<slug>/{{chainSlug}}-chain-{{n}}-{{deployable}}.md` beside the chain file; pass the question verbatim, start at its inbound contract, bound outcomes by expected outbound contracts, and link the result from the follow-up row.
- In Flow or Behavior, report a Data follow-up to the orchestrator when a persistence question depends on ownership, keys, consistency, migration, concurrency, retention, or deletion.
- Report managed-service semantics, quotas, and API parameters to the orchestrator as cloud follow-ups.

## Evidence ladder

Executing source > passing test exercising this exact path > repo docs (ADR, Concept, README, ARCHITECTURE.md) > config/schema defaults > commit or PR description > code comment > inference.

Tests, comments, and docs state *intent*. Executing code proves *behavior*. Record mismatches as findings.

IaC and migration files are executing code. Entity classes *declare* shape. Serializers determine write *behavior*.

## Claim types

- **FACT** — confirmed against code, a test, or a runtime check; carries a citation.
- **ASSUMPTION** — plausible, unconfirmed; state why, and what would verify it.
- **UNKNOWN** — a named gap, stated as a concrete next check.
- **CONCLUSION** — the explanation the facts support.

## File references

Use filename-only links with visible line numbers for every repository file mention: `[{{filename}}]({{path relative to the research document}}#L{{line}}):L{{line}}` for one line or `[{{filename}}]({{path relative to the research document}}#L{{start}}):L{{start}}-{{end}}` for a range. Put the relative path and start-line anchor in the target. Keep the full line location outside it. Example: `[orders.py](../../src/orders.py#L42):L42-54`. Apply in prose, tables, Facts, Gaps, runtime checks, and Evidence fields. Place each citation immediately after its claim. Quote a short deciding line when it settles the claim. A bare path, symbol, table, or service name is not a citation.

## Runtime checks

Static reading proves possible behavior. Verify actual behavior with a runtime check when reading leaves a claim open: run the test, add a temporary log, call the endpoint, read stored data, or correlate logs by ID. Discard the check and keep the result.

## Gotchas

- **A `block` mermaid diagram rejects rhombus/diamond node shapes (`{"label"}`)**. Use `flowchart` for decision shapes.
- **A trace that ends in a double proves the wiring, not the behavior** — an environment, profile, or flag may substitute a mock, stub, in-memory fake, or recorded response. Record the double as its own Fact and follow the real implementation for behavior claims.
- **Use production configuration for consistency, lag, and expiry claims.** An emulator, in-memory fake, or single-node instance can behave differently.
