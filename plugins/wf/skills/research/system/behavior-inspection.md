# Behavior axis — one deployable's contribution

The document carries a mermaid diagram of the confirmed mechanism. A capability is the stable product ability; a feature and its functional slice realize it. This axis records one deployable's responsibility in that slice, framed as actor + action + object. The trace starts at this unit's triggers and stops at its observable outcomes.

Route to one owning deployable and stop at effects leaving it. For an API, start with Swagger, then trace controller, DTO, validation, and outbound calls.

**Output:** `docs/research/{{slug}}.md`, or `docs/research/{{chainSlug}}-chain-{{n}}-{{deployable}}.md` when the brief asks for a lane of an existing chain.

## Diagram

Pick the diagram from what the question asks, then run its owning skill.

| Inspection topic | Draw | Skill |
|---|---|---|
| the call chain end to end — interaction order, cross-boundary calls, returns, failure branching | a **sequence diagram** | `doc-diagram` |
| which branch fires — config or feature-flag branching, provider selection and fallback, error and edge paths | a **flowchart** | `doc-diagram` |
| who owns each step and where responsibility changes — handoffs across layer, modules, or teams | a **swimlane diagram** | `doc-diagram` |
| which deployable-local functional slices and external systems a flow connects | a **container diagram** | `doc-diagram` |
| scope and integration boundary — the actors and external systems around it | a **system context diagram** | `doc-diagram` |
| where it runs — hosting, runtime, infrastructure placement | a **deployment view** | `doc-diagram` |
| which types implement the interface behind it — inheritance, composition, dependencies | a **class diagram** | `doc-diagram` |

A traced behavior defaults to the **sequence diagram**; *run `doc-diagram` skill for the sequence diagram's interaction order, call chain, and failure branching* before drafting it.

Label nodes with the role or step plus one greppable trace keyword — a route path, config key, event or queue name, table name, or interface name. Keep file references in the tables; use class, method, or file names with exact lines in the diagram only when the brief asks for them.

Default to one: triggers enter as parallel participants meeting at the convergence point, observable outcomes leave from it. Split only when triggers diverge, selection needs a flowchart, outcomes fire out of band, or the diagram passes roughly 12 participants or 25 messages. Each split carries a heading naming the question it answers and repeats no node.

## Workflow

1. **Frame** — name the capability, feature, functional slice, actor, action, object, trigger(s), and exact behavior in domain language. "When does the system reject an expired session?" beats "how does auth work?".
2. **Scope** — name the capability, feature, functional slice, actor, object, outcome, and external systems in scope, plus what is explicitly out; keep paths and implementation layers in the technical sections.
3. **Map surface** — enumerate both ends before tracing either (see Surface map), and say which the question covers.
4. **Map broad** — grep/semantic-search route tables, command registrations, event subscribers, schedulers, and container/provider registrations for candidate triggers. Collect candidates before reading any of them deeply.
5. **Hypothesize** — write the mechanism as a testable chain (`OrderController.Create` → `OrderService.Place` → `OrdersRepository.Insert`). Each hypothesis names the next thing to confirm.
6. **Rank by risk** — confirm in this order: does this path actually execute for the framed case (vs. a dead or superseded lookalike) → which triggers reach it, and what each does differently before they converge → which provider actually serves it and what it falls back to (see Providers and fallback) → config/feature-flag branching → error and edge cases → async ordering → performance → naming.
7. **Trace deep, narrow** — go-to-definition, find-references, call hierarchy along that one chain instead of reading whole files. Drop a branch the moment it is irrelevant.
8. **Run a runtime check** when static reading can't settle a claim — which branch fires, runtime-computed config, async ordering.
9. **Record on confirmation** — write each Fact with its citation immediately, and prune the branches it rules out.

**Done when** every in-scope trigger reaches a cited convergence point, every step from there to an observable outcome carries a citation, every outcome and selectable provider with its fallback edge is accounted for, every call leaving the deployable is recorded as an outcome carrying its contract, the diagram accounts for every recorded Fact, and the remaining unknowns can't change the answer.

## Surface map

A behavior can have many triggers and observable outcomes; tracing one of each answers a narrower question than the one asked.

- **Triggers** — REST/RPC route, GUI action, client library, CLI, scheduled job, queue or event consumer, webhook. Several usually converge on one core; each can apply its own auth, validation, defaults, and deserialization first. Cite each trigger and its **convergence point**, then trace once below it and note per-trigger differences as Facts.
- **Observable outcomes** — independently observable persisted writes, published events, outbound calls, files, cache invalidations, notifications, response payloads, and logs or metrics another system consumes. Reads, validations, branch decisions, internal calls, and calculations stay in Mechanism or Facts unless they themselves create an observable result. Separate outcomes with different timing or transactionality.
- **Boundary** — an outcome that leaves the deployable ends this trace: record the contract it carries — operation or schema, parameters, error surface — and stop. What the receiving system does with it is a lane of its own, reached by the **Flow** axis.

## Providers and fallback

A behavior may have several providers behind one outcome — picked by config, flag, or tenant tweak, and swapped again when the first fails or answers badly. The first implementation you find is a candidate, not the answer; the provider stays unresolved until selection and fallback both carry citations. Record the outbound call under Observable outcomes and explain why that provider serves it here.

Where the wiring hides: implementations of one interface resolved by factory, keyed registration, or injected collection · separate clients chained by an orchestrator or decorator · fallback in a resilience policy, HTTP handler, or gateway, leaving the call site a single call.

Cite each with a file reference per **File references**:

- **Registry** — where the set of sources is registered.
- **Selector** — config key/flag read, value per source, default when absent, and whether it is read per call or once at startup.
- **Precedence** — the order fallback walks.
- **Trigger** — what demotes a source: exception, timeout, status code, or the validation that rules a *successful* response invalid.
- **Terminal** — behavior when every source fails, and whether a fallback result is cached.
- **Double** — the environment, profile, or flag that swaps a source for a mock, stub, in-memory fake, or recorded response, and where that double is the default.

Diagram selector and fallback edges, not the winning path alone.
