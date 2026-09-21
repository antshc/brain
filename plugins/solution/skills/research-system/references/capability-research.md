# Capability axis — one deployable

The document carries a mermaid diagram of the confirmed mechanism. Scope is one deployable: the trace starts at this unit's entry points and stops at the effects leaving it.

## Workflow

1. **Frame** — name the capability, the entry point(s) in question, and the exact behavior. "Where does an expired token get rejected?" beats "how does auth work?".
2. **Scope** — repo/service and layers in scope (API, domain, persistence, infra), and what is explicitly out.
3. **Map surface** — enumerate both ends before tracing either (see Surface map), and say which the question covers.
4. **Map broad** — grep/semantic-search route tables, command registrations, event subscribers, schedulers, and container/provider registrations for candidate entry points. Collect candidates before reading any of them deeply.
5. **Hypothesize** — write the mechanism as a testable chain (`OrderController.Create` → `OrderService.Place` → `OrdersRepository.Insert`). Each hypothesis names the next thing to confirm.
6. **Rank by risk** — confirm in this order: does this path actually execute for the framed case (vs. a dead or superseded lookalike) → which entry points reach it, and what each does differently before they converge → which implementation actually serves it when several sit behind one interface, and what it falls back to (see Multiple external sources) → config/feature-flag branching → error and edge cases → async ordering → performance → naming.
7. **Trace deep, narrow** — go-to-definition, find-references, call hierarchy along that one chain instead of reading whole files. Drop a branch the moment it is irrelevant.
8. **Probe** when static reading can't settle a claim — which branch fires, runtime-computed config, async ordering.
9. **Record on confirmation** — write each Fact with its citation immediately, and prune the branches it rules out.

**Done when** every in-scope entry point reaches a cited convergence point, every step from there to effect carries a citation, every effect and every selectable source with its fallback edge is accounted for, every call leaving the deployable is recorded as an effect carrying its contract, the diagram accounts for every recorded Fact, and the remaining unknowns can't change the answer.

## Surface map

A capability has many ways in and many ways out; tracing one of each answers a narrower question than the one asked.

- **Entry points** — REST/RPC route, GUI action, client library, CLI, scheduled job, queue or event consumer, webhook. Several usually converge on one core; each can apply its own auth, validation, defaults, and deserialization first. Cite each entry, cite the **convergence point**, then trace once below it and note per-entry differences as Facts.
- **Effects** — persisted writes, published events, outbound calls, files, cache invalidations, notifications, the response payload, and logs/metrics another system consumes. The returned value is one effect among several; name each and whether it is unconditional, and whether it shares the caller's transaction.
- **Boundary** — an effect that leaves the deployable ends this trace: record the contract it carries — operation or schema, parameters, error surface — and stop. What the receiving system does with it is a lane of its own, reached by the **Deployables** axis.

## Multiple external sources

A capability usually has several providers behind it — picked by config, flag, or tenant tweak, and swapped again when the first fails or answers badly. The first implementation you find is a candidate, not the answer; the provider stays unresolved until selection and fallback both carry citations.

Where the wiring hides: implementations of one interface resolved by factory, keyed registration, or injected collection · separate clients chained by an orchestrator or decorator · fallback in a resilience policy, HTTP handler, or gateway, leaving the call site a single call.

Cite each with `path:line`:

- **Registry** — where the set of sources is registered.
- **Selector** — config key/flag read, value per source, default when absent, and whether it is read per call or once at startup.
- **Precedence** — the order fallback walks.
- **Trigger** — what demotes a source: exception, timeout, status code, or the validation that rules a *successful* response invalid.
- **Terminal** — behavior when every source fails, and whether a fallback result is cached.
- **Double** — the environment, profile, or flag that swaps a source for a mock, stub, in-memory fake, or recorded response, and where that double is the default.

Diagram selector and fallback edges, not the winning path alone.

## Diagrams

Pick the diagram from what the question asks, then Run its owning skill for syntax and styling — never compose Mermaid from memory.

| Research topic | Draw | Skill |
|---|---|---|
| the call chain end to end — interaction order, cross-boundary calls, returns, failure branching | a **sequence diagram** | `/behavior-diagram` |
| which branch fires — config or feature-flag branching, provider selection and fallback, error and edge paths | a **flowchart** | `/behavior-diagram` |
| who owns each step and where responsibility changes — handoffs across layers, modules, or teams | a **swimlane diagram** | `/behavior-diagram` |
| which deployable units and external systems the capability spans | a **container diagram** | `/architecture-diagram` |
| scope and integration boundary — the actors and external systems around it | a **system context diagram** | `/architecture-diagram` |
| where it runs — hosting, runtime, infrastructure placement | a **deployment view** | `/architecture-diagram` |
| which types implement the interface behind it — inheritance, composition, dependencies | a **class diagram** | `/code-diagram` |

A traced capability defaults to the sequence diagram; Run `/behavior-diagram` skill before drafting it.

**Label with trace keywords, not class names and line numbers.** A diagram node names the role or step in the flow (`HTTP entry`, `order validation`, `payment provider`, `order persisted`) plus the one literal token an agent can grep to land on it — a route path, config key, event or queue name, table name, or interface name. Keep `path:line` citations out of the diagram; the Facts, Entry points, Effects, and External sources tables carry them, and the diagram stays falsifiable by pairing with those rows. Use real class, method, or file names with exact lines in the diagram **only when the user asks for them**.

Default to one: entries enter as parallel participants meeting at the convergence point, effects leave from it. Split when a single diagram would misstate or sprawl — each split carries a heading naming the question it answers, and repeats no node the first one already showed:

- **Entries diverge** — they never reach a shared path; diagram each distinct path.
- **Selection** — selector and fallback edges are branching logic, so they want their own **flowchart** beside the sequence.
- **Out-of-band effects** — events, background dispatch, or post-commit work whose ordering one sequence would imply wrongly.
- **Sprawl** — past roughly 12 participants or 25 messages, readability dies.

Run `/render-mermaid-png` skill only if the user wants an exported image alongside the Markdown.

## Gotchas

- **A `block` mermaid diagram rejects rhombus/diamond node shapes (`{"label"}`)** — the renderer throws. Use `flowchart` for decision shapes.
