# Flow Inspection: {{flowName}}

**Rules** — apply while filling this scaffold, then delete this block and every `**Rules:**` line from the result.

- Question, Scope, and Summary use domain anchors — actors, outcome, governed object, and named systems — without source paths, routes, code symbols, configuration keys, or implementation-layer terms.
- Summary claims cite numbered Facts; every repository file mention and technical claim elsewhere carries a file reference per **File references** in the skill. A bare service name is not evidence.
- Every diagram node, Flow row, boundary claim, and Conclusion statement traces to a Fact. Quote the deciding line whenever it settles a claim on sight.
- Executing code and a probed correlation id prove the chain; deployment diagrams, READMEs, comments, and team knowledge state only intent. Record mismatches as Facts.
- Scope is one end-to-end chain. Each deployable appears once as one lane with 1–5 ordered major-step nodes; deeper internal mechanisms belong to optional Behavior follow-ups.

- Question: {{the exact end-to-end outcome being traced}}
- Scope: {{the external entry, terminal boundary, named systems, and what's explicitly out}}
- Status: investigating | answered

## Summary

**Rules:** Answer the framed question in 2-3 domain-facing sentences. Lead with whatever most surprises a reader who assumed the obvious topology, and cite each claim by Fact number instead of source path.

{{summary}}

## Chain

**Rules:** Draw and render one Mermaid swimlane per **Flow — cross-deployable chain** in the skill. Give every deployable one lane containing 1–5 ordered nodes for its major steps, place terminal systems at diagram edges, and label every cross-lane arrow with its boundary contract. Put all terminal nodes in the titled `Terminal boundaries` lane; label each node with the target name only. Every node and arrow traces to a Fact; tables below carry citations.

{{diagram}}

## Flow

**Rules:** One row per deployable in chain order. A deployable is a unit production starts independently; artifacts belong in their executor's major steps. `Receives` names the external entry for the first lane and the boundary contract for later lanes. `Major steps` lists 1–5 ordered, boundary-relevant responsibilities that explain how the inbound contract becomes the outbound contract; put deeper internal decisions in Behavior follow-ups.

| # | Deployable | Receives | Major steps | Emits | Evidence |
|---|---|---|---|---|---|
| 1 | {{service, container, function, worker, host workload, or scheduled job}} | {{external entry or inbound contract}} | {{1–5 ordered steps, each backed by a Fact}} | {{outbound contract or terminal effect}} | {{Fact #; file reference}} |

## Boundary contracts

**Rules:** Add one subsection per crossing. An internal boundary requires emit, receive, and binding citations proving both sides address the same resource. A terminal boundary replaces receive evidence with its stop reason — `no source access` or `out of framed scope — {{reason}}` — and cites config or IaC naming the real target. Record observed configuration separately from provider guarantees.

### {{source lane}} → {{target lane or terminal system}}

| Aspect | Contract | Evidence |
|---|---|---|
| API/event | {{operation or route and parameters; event/topic, schema, and version}} | {{Fact #; file reference}} |
| SDK/protocol | {{package@version; client and method; transport, serialization, sync/async, or —}} | {{Fact #; file reference}} |
| Auth | {{caller identity; credential/mechanism; permissions; trust/TLS boundary}} | {{Fact #; file reference}} |
| Failure behavior | {{statuses, exceptions or failure events; timeout, retry, throttling, idempotency, and DLQ behavior}} | {{Fact #; file reference}} |
| Binding/target | {{endpoint, resource, account, and region; or — when not applicable}} | {{Fact #; file reference}} |
| Handoff/stop | {{emit site + receive site, or terminal stop reason}} | {{Fact #; emit file reference; receive file reference, or authoritative contract citation}} |

## Facts

**Rules:** One row per confirmed chain claim. Include ordering, retries, duplication, transactional scope, and what survives a lane failure when they affect the outcome. A runtime probe Fact records the rerunnable command, correlation id, confirmed lanes or handoffs, and log or trace evidence. Prefer facts that contradict the assumed topology.

| # | Fact | Evidence |
|---|---|---|
| 1 | {{fact}} | {{file reference — `deciding line quoted`}} |

## Gaps

### Assumptions

**Rules:** Plausible but unconfirmed claims, including every crossing missing its emit site, receive site, or binding. A deployable named in diagrams but not confirmed by executing source belongs here when crossing evidence suggests it exists; when its absence could change chain completeness or the framed answer, record that consequence under Unknowns too. `What would verify it` is a concrete command, probe, search, or file to open.

| # | Assumption | Why unverified | What would verify it |
|---|---|---|---|

### Unknowns

**Rules:** Missing information that could change the chain-level answer. `Next probe` names the exact search, command, runtime probe, or file to open. When runtime confirmation matters and no chain probe ran, record the rerunnable probe here.

| # | Unknown | Next probe |
|---|---|---|

## Behavior follow-ups

**Rules:** Add a row only when the framed outcome depends on a deployable's internal decision and its proved boundary contracts do not explain that decision. This is deliberately deferred scope, not missing chain evidence. `Behavior question` is the verbatim domain-facing frame for an optional Behavior-axis run; its inbound contract becomes the entry point and its expected outbound contracts bound the observable outcomes. Omit this section when no lane qualifies.

| Lane | Rationale | Behavior question | Inbound contract | Expected outbound contracts |
|---|---|---|---|---|
| {{lane # — deployable}} | {{why its internal mechanism can change the framed outcome}} | {{exact domain-facing question}} | {{proved received contract}} | {{proved emitted contracts}} |

## Conclusion

**Rules:** State the end-to-end explanation supported by numbered Facts, name the deployable that decides the framed outcome when several touch it, and distinguish confirmed behavior from remaining Gaps.

{{conclusion}}