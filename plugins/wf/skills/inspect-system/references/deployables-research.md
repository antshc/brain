# Deployables axis — one chain

Breadth first, depth later. One deployable is one lane; the chain continues through every outcome-relevant system whose executing source you can open, and ends at the systems whose source you cannot. **One chain run produces one document.** Depth inside a lane belongs to the **Capability** axis, offered as a follow-up once the chain is complete.

## Tiers

| | This axis — chain | Capability axis — lane |
|---|---|---|
| Unit | one deployable = one lane | one symbol = one participant |
| Diagram | swimlane | sequence |
| Evidence | the wire: emit site + receive site + the binding naming the real resource | file references along the call chain |
| Stops at | terminal external systems | that lane's inbound entry and outbound effects |

## Deployable eligibility

A lane is a **deployable**: a unit independently runnable or deployed in production — a process, service, container, function, host workload, or scheduled job that the platform starts on its own.

**Eligibility test** — does production start this unit independently? Yes → it earns a lane. No → it is an artifact, and it belongs inside the lane of whatever executes it.

Upgrade bundles, installers, shell and Python scripts, Ansible playbooks, Helm charts, Terraform modules, SQL migrations, and libraries are **artifacts**. Name the executing deployable as the lane and record the artifact as what that lane *does*. A bundle executed by a privileged host agent is one lane — the agent — not two.

## Workflow

1. **Frame the chain** — name the outcome traced, not the service. "Where does a placed order become reserved stock?" beats "how does ordering work?".
2. **Find the chain entries** — what originates the flow from outside the whole system: user action, schedule, webhook, upstream system, batch drop. An inbound call from a deployable already in the chain is a handoff, not an entry.
3. **Walk lane by lane** — per deployable record what it receives, 1–5 ordered major steps, and what it emits. A major step is a boundary-relevant responsibility needed to explain how the inbound contract becomes the outbound contract; collapse implementation details that do not change that explanation. Read only enough client call sites, routes, publish/subscribe calls, SDK use, auth configuration, error handling, and IaC bindings to prove the steps and next crossing; leave deeper internal mechanism for a Capability-axis run.
4. **Classify every edge** — continuable or terminal (see Boundary). Continue when the next deployable's executing source opens and its behavior can change the framed outcome. Otherwise close a confirmed crossing as terminal with `no source access` or `out of framed scope — {{reason}}`; keep an unconfirmed crossing in Gaps.
5. **Complete the chain** — reach a terminal for every in-scope branch before examining any lane internally. Record outcome-irrelevant siblings as terminal by scope and cycles as handoffs back to an existing lane.
6. **Probe the chain** (see Chain probe) — one real correlation id beats any amount of static reading for proving the lanes actually connect. Record the command, correlation id, and confirmed handoffs as Facts; when no probe runs and runtime confirmation matters, record the exact probe in Unknowns.
7. **Draw and render the chain** — the swimlane is part of the deliverable, not an illustration added afterwards. Draw each deployable once as one lane containing 1–5 ordered major-step nodes; arrows between lanes carry boundary contracts.
8. **Offer Capability follow-ups** — after the chain is complete, apply the Capability follow-up gate. Run the **Capability** axis only when the user asks for a listed follow-up; pass its question verbatim, its inbound contract as the entry point, and its expected outbound contracts as the observable-outcome boundary.

**Done when** the chain document is the only file written; every entry reaches a lane; every deployable appears exactly once as one lane with 1–5 major-step nodes; every artifact sits inside its executing lane; every in-scope branch reaches a terminal; the swimlane renders and every terminal sits at a diagram edge; every boundary records its API or event, SDK, protocol, auth, errors, and binding; every internal handoff has emit-, receive-, and binding citations; every terminal says why research stops; every diagram and conclusion claim is backed by a numbered Fact; and every deferred internal question has a complete Capability follow-up.

## Boundary

Two kinds of crossing, with different stop semantics.

| | Terminal | Continuable |
|---|---|---|
| What | managed service reached through an SDK or API (DynamoDB, S3, SQS, Stripe), database engine, third-party API, OS primitive | a deployable whose source you can open — microservice, container, lambda, queue consumer, sibling repo |
| Record | the integration contract and the IaC/config naming the real resource, region, and account | the integration contract plus emit site, receive site, and binding |
| Becomes | a terminal Boundary contract | the next Flow row plus an internal Boundary contract |

**Continue test** — keep following a hop while its executing source opens **and** the framed outcome depends on what happens there. Either answer turns no → terminal, write the contract, stop. Unfamiliarity, repository distance, and lane count are not stop conditions.

A deployable often emits to several downstreams. Expand only the ones on the path to the framed outcome; record the siblings as terminal by scope with a one-line reason. This is what keeps a mesh from swallowing the research.

## Integration contract

Research integrations at each boundary; do not create a separate integration-research output.

- **API/event** — operation or route; parameters; event/topic and schema; version.
- **SDK** — package, version, client, and method when used; otherwise `—`.
- **Protocol** — transport, serialization, and sync/async behavior.
- **Auth** — caller identity, credential/mechanism, required permissions, and trust/TLS boundary.
- **Errors** — statuses, exceptions or failure events; timeout, retry, throttling, idempotency, and DLQ behavior when relevant.
- **Binding** — endpoint, resource, account, and region selected by config or IaC.

For internal boundaries, cite both sides. For external boundaries, cite the call site and binding; cite authoritative provider or protocol documentation for semantics not encoded in the repository. Keep observed configuration distinct from provider guarantees.

## Handoff evidence

**Every handoff carries three citations — the emit site, receive site, and binding.** A producer publishing to a topic proves nothing about who consumes it, a consumer subscribing proves nothing about who fills it, and matching names do not prove the same account or region. Until all three are confirmed, record the claimed crossing as an Assumption with the missing evidence named under `What would verify it`. The binding may be Terraform, Bicep, a compose file, or a config key proving both sides address the same real resource.

Guessed topology is the default failure of cross-service tracing, and this rule is what makes it falsifiable.

## Chain probe

Issue one real request carrying a correlation id, then collect that id across every deployable's logs or distributed trace. Every handoff the id lights up becomes a Fact in one action, and lanes the static read missed surface here. Record the correlation id and the command issued so the trace is re-runnable; handoffs the probe never lit stay assumptions.

## Capability follow-up gate

Add a follow-up only when the framed outcome depends on a deployable's internal decision and its boundary contracts do not explain that decision. Curiosity, complexity, and unfamiliar code do not qualify. Finish the chain first, then record each qualifying lane with:

| Field | Content |
|---|---|
| Lane | lane number and deployable |
| Rationale | why its internal mechanism can change the framed outcome |
| Capability question | the exact domain-facing question for the Capability-axis run |
| Inbound contract | the proved contract that becomes the Capability trace's entry point |
| Expected outbound contracts | the proved emissions that bound its observable outcomes |

The follow-up is deferred scope, not missing evidence. A one-sided handoff or unresolved terminal belongs in Gaps instead. When the user requests a follow-up, the Capability document links back to this chain and uses the lane number, question, inbound contract, and expected outbound contracts without reframing them.

## Gotchas

- **A lane that appears twice is one lane revisited, not two** — a chain that returns to an earlier deployable is a cycle; record the second crossing as a handoff back to the existing lane number and stop, or the walk never terminates.
- **An artifact given its own lane invents a deployable that production never starts** — a bundle, script, playbook, or chart shows up in logs and file trees like a participant, so apply the eligibility test before drawing a lane for anything you cannot point at a process for.
- **A missing sibling in a code graph is a gap, not a terminal** — graph and index tools cover only the repositories in their manifest, so search the repository directly before classifying the crossing. When emit or receive evidence suggests the sibling exists but the other side or binding remains missing, record an Assumption; when that gap could change chain completeness or the framed answer, also record the consequence as an Unknown.
- **Too many steps in a chain lane hide an unfinished chain** — one deployable's mechanism can consume the run before downstream boundaries are proved, so keep only 1–5 boundary-relevant major steps and offer a Capability follow-up after the chain closes.
