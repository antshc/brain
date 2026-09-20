---
name: research-capability
description: Investigate how a feature, capability, or flow actually works in the existing codebase, citing every claim to file:line evidence, and produce a Markdown research doc with a mermaid diagram tracing the mechanism end-to-end. Use when asked how something works, to document a feature's mechanism, trace a flow through the code, explain existing behavior, determine which provider or fallback actually serves a capability, or write an as-built explanation with diagrams.
---

# Research a feature

Source of truth is this repo, not the web. Output: one Markdown file, every claim cited to `path:line`, carrying a mermaid diagram of the confirmed mechanism.

## Workflow

1. **Frame** — name the capability, the entry point (route, CLI command, event handler, UI action), and the exact behavior in question. "Where does an expired token get rejected?" beats "how does auth work?".
2. **Scope** — repo/service and layers in scope (API, domain, persistence, infra), and what is explicitly out.
3. **Map broad** — grep/semantic-search route tables, command registrations, event subscribers, schedulers, and container/provider registrations for candidate entry points. Collect candidates before reading any of them deeply.
4. **Hypothesize** — write the mechanism as a testable chain (`OrderController.Create` → `OrderService.Place` → `OrdersRepository.Insert`). Each hypothesis names the next thing to confirm.
5. **Rank by risk** — confirm in this order: does this path actually execute for the framed case (vs. a dead or superseded lookalike) → which implementation actually serves it when several sit behind one interface, and what it falls back to (see Multiple external sources) → config/feature-flag branching → error and edge cases → async ordering → performance → naming.
6. **Trace deep, narrow** — go-to-definition, find-references, call hierarchy along that one chain instead of reading whole files. Drop a branch the moment it is irrelevant.
7. **Probe** when static reading can't settle a claim (which branch fires, runtime-computed config, async ordering): run the test, add a temporary log, call the endpoint, query the data it wrote. Discard the probe, keep the result.
8. **Record on confirmation** — write each Fact with its citation immediately, and prune the branches it rules out.

**Done when** every step from entry point to effect carries a citation, every selectable source and its fallback edge is accounted for, the diagram accounts for every recorded Fact, and the remaining unknowns can't change the answer.

## Multiple external sources

A capability usually has several providers behind it — picked by config, flag, or tenant tweak, and swapped again when the first fails or answers badly. The first implementation you find is a candidate, not the answer; the provider stays unresolved until selection and fallback both carry citations.

Where the wiring hides: implementations of one interface resolved by factory, keyed registration, or injected collection · separate clients chained by an orchestrator or decorator · fallback in a resilience policy, HTTP handler, or gateway, leaving the call site a single call.

Cite each with `path:line`:

- **Registry** — where the set of sources is registered.
- **Selector** — config key/flag read, value per source, default when absent, and whether it is read per call or once at startup.
- **Precedence** — the order fallback walks.
- **Trigger** — what demotes a source: exception, timeout, status code, or the validation that rules a *successful* response invalid.
- **Terminal** — behavior when every source fails, and whether a fallback result is cached.

Diagram selector and fallback edges, not the winning path alone.

## Evidence ladder

Executing source (`path:line`) > passing test exercising this exact path > repo docs (ADR, Concept, README, ARCHITECTURE.md) > config/schema defaults > commit or PR description > code comment > inference.

Tests, comments, and docs state *intent*; only executing code proves *behavior*. When they disagree, record the mismatch as a finding.

## Claim types

- **FACT** — confirmed against code, a test, or a probe; carries a citation.
- **ASSUMPTION** — plausible, unconfirmed; state why, and what would verify it.
- **UNKNOWN** — a named gap, stated as a concrete next probe.
- **CONCLUSION** — the explanation the facts support.

## Citations

Cite `path:line` or `path:startLine-endLine` inline, immediately after the claim it supports — never pooled at the end. Quote the deciding line when short enough to settle the claim on sight. A bare symbol name is not a citation.

## Output

Write to `docs/ongoing/<slug>.md` unless the user names a location or the repo documents features elsewhere. Fill [capability-research-template.md](capability-research-template.md), obeying its `**Rules**` blocks and deleting every one of them from the result.

Diagram: `sequenceDiagram` for a call/message flow, `flowchart` for branching decision logic. Every node or message names the `file:line` that established it, keeping the diagram falsifiable. Run `/render-mermaid-png` skill only if the user wants an exported image alongside the Markdown.

## Gotchas

- **A `block` mermaid diagram rejects rhombus/diamond node shapes (`{"label"}`)** — the renderer throws. Use `flowchart` for decision shapes.
