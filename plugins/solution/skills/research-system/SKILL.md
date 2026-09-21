---
name: research-system
description: "Research a software system as-built and write a Markdown research document citing every claim to path:line. Use when asked how a capability works inside one deployable, to trace a flow across deployables and document its integration contracts, or to settle a question turning on data — keys, ownership, consistency, migration, concurrency, retention."
---

# Research a system

Source of truth is this repo, not the web. Output: one Markdown file, every claim cited to `path:line`.

Research documents **as-built** — current state, never a delta.

## Axes

Three axes, one per unit of research. Pick by the unit the question is about, load only that axis's references and template, and leave the other two unread.

Write to the axis's output path unless the user names a location. Fill its template, obeying the `**Rules**` blocks and deleting every one of them from the result.

### Capability — one deployable

The unit is one symbol chain inside one deployable: the trace starts at this unit's entry points and stops at the effects leaving it. Pick it for how something works, where a decision is made, what a change touches, which implementation or double actually serves a call.

- References: [capability-research.md](references/capability-research.md)
- Template: [capability-research-template.md](templates/capability-research-template.md)
- Output: `docs/ongoing/{{slug}}.md`, or `docs/ongoing/{{chainSlug}}/{{n}}-{{deployable}}.md` when run as a lane of a chain

### Deployables — one chain

The unit is one deployable per lane, and the chain ends at the systems whose source you cannot open. Pick it when the flow crosses a process boundary, or when asked what handles a message next, where it ends, or what contract crosses the wire.

- References: [deployables-research.md](references/deployables-research.md)
- Template: [deployables-research-template.md](templates/deployables-research-template.md)
- Output: `docs/ongoing/{{slug}}/README.md`, with lane documents as siblings named `{{n}}-{{deployable}}.md`, numbered by lane order

### Data — one item type and its store

The unit is one item type and the store holding it — one writer, many readers, a boundary cutting across services and often across repos. Pick it when the question turns on key design, who owns a table, whether a read can be stale, how an attribute is migrated, whether concurrent writes are safe, or how records are aged out.

- References: [data-research.md](references/data-research.md)
- Template: [data-research-template.md](templates/data-research-template.md)
- Output: `docs/ongoing/research-{{slug}}-data.md`

### Crossing axes

- The Deployables axis runs the Capability axis per lane worth depth, writing the lane document beside the chain document.
- Provider semantics, quotas, and API parameters behind a managed service belong to the provider, not this repo: Run `/research-aws` skill or `/research-azure` skill.

## Evidence ladder

Executing source (`path:line`) > passing test exercising this exact path > repo docs (ADR, Concept, README, ARCHITECTURE.md) > config/schema defaults > commit or PR description > code comment > inference.

Tests, comments, and docs state *intent*; only executing code proves *behavior*. When they disagree, record the mismatch as a finding.

IaC and migration files are executing code. An entity class is a *declaration* of shape; the serializer that writes it is the *behavior*.

## Claim types

- **FACT** — confirmed against code, a test, or a probe; carries a citation.
- **ASSUMPTION** — plausible, unconfirmed; state why, and what would verify it.
- **UNKNOWN** — a named gap, stated as a concrete next probe.
- **CONCLUSION** — the explanation the facts support.

## Citations

Cite `path:line` or `path:startLine-endLine` inline, immediately after the claim it supports — never pooled at the end. Quote the deciding line when short enough to settle the claim on sight. A bare symbol, table, or service name is not a citation.

## Probes

Static reading settles what the code *can* do; a probe settles what it *does*. Reach for one whenever a claim cannot be closed by reading: run the test, add a temporary log, call the endpoint, read the stored item, collect a correlation id across logs. Discard the probe, keep the result.

## Gotchas

- **A trace that ends in a double proves the wiring, not the behavior** — an environment, profile, or flag that swaps a real dependency for a mock, stub, in-memory fake, or recorded response makes the contract real and the behavior fictional. Record the double as its own Fact and follow the real implementation for behavior claims.
- **A local development store is not the production store** — an emulator, in-memory fake, or single-node instance answers consistency, lag, and expiry questions differently from the real one, so those claims need production configuration as evidence.
