# Flow axis — cross-deployable slice chain

Start with boundaries. One deployable and its functional slice form one lane. Trace each outcome-relevant handoff through the systems whose source is available. Apply Behavior checks within a lane when its internal decision changes the answer.

Map each handoff to a row, then verify sender, wire contract, receiver, and deployment or configuration binding. Stop at a terminal infrastructure boundary only after recording the operation, protocol, authentication, errors, and relevant configuration.

Add findings to the How report. The default single-axis Flow path is `docs/research/{{slug}}-chain.md`.

## Contents

- Diagram
- Tiers
- Deployable eligibility
- Workflow
- Boundary
- Integration contract
- Handoff evidence
- Chain check
- Gotchas

## Diagram

When a chain diagram adds clarity, draw a **swimlane** with one lane per deployable, 1–5 ordered major-step nodes in each lane, terminal systems as edge lanes, and every cross-lane arrow labelled with its contract. *Follow `doc-diagram` skill's **Swimlane Diagram** for lane ownership, handoffs, and responsibility changes* and open its swimlane template before drafting.

Use Mermaid `swimlane-beta`. When the renderer lacks swimlane support, fall back to a `flowchart` with one `subgraph` per lane. A `sequenceDiagram` is not a chain view because it loses the lane ownership this axis exists to show.

Back every node and crossing with the cited mechanism or handoff table. Group terminal nodes at the edges in a lane titled Terminal boundaries when useful. Add a **container diagram** above the swimlane only when the lane count passes roughly eight and the reader needs the shape first; *run `doc-diagram` skill for the Mermaid C4 container diagram's deployables and relationships*.

## Tiers

| | This axis — chain | Behavior axis — lane |
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
3. **Walk lane by lane** — per deployable record what it receives, 1–5 ordered major steps, and what it emits. A major step is a boundary-relevant responsibility needed to explain how the inbound contract becomes the outbound contract; collapse implementation details that do not change that explanation. Read only enough client call sites, routes, publish/subscribe calls, SDK use, auth configuration, error handling, and IaC bindings to prove the steps and next crossing; apply the Behavior lens in the same report when an internal decision affects the outcome.
4. **Classify every edge** — continuable or terminal (see Boundary). Continue when the next deployable's executing source opens and its behavior can change the framed outcome. Otherwise close a confirmed crossing as terminal with `no source access` or `out of framed scope — {{reason}}`; keep an unconfirmed crossing in Gaps.
5. **Complete the chain** — reach a terminal for every in-scope branch. Trace deciding lane behavior and storage or provider semantics as needed to settle the question. Record outcome-irrelevant siblings as terminal by scope and cycles as handoffs back to an existing lane.
6. **Check the chain at runtime** when runtime confirmation matters. Follow Chain check and the System inspection runtime rules.
7. **Explain the chain** — use the How mechanism. If a table clarifies the trace, give each deployable one row in chain order, with the inbound contract, ordered major steps, outbound contract, and evidence. Render any included diagram.

**Done when** each entry reaches a lane, each in-scope branch reaches a terminal or a recorded gap, and each internal handoff has emit, receive, and binding citations. Record why each terminal ends the trace. Back the mechanism and any diagram with confirmed evidence.

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

## Chain check

Correlate an existing request across logs or distributed traces, or issue a request with a correlation ID when authorized on a safe target. Record the command or query, environment, correlation ID, and observed handoffs. If confirmation is blocked, name the claim and exact next check. Keep unobserved handoffs separate from runtime-confirmed facts.

## Gotchas

- **A lane that appears twice is one lane revisited, not two** — a chain that returns to an earlier deployable is a cycle; record the second crossing as a handoff back to the existing lane number and stop, or the walk never terminates.
- **An artifact given its own lane invents a deployable that production never starts** — a bundle, script, playbook, or chart shows up in logs and file trees like a participant, so apply the eligibility test before drawing a lane for anything you cannot point at a process for.
- **A missing sibling in a code graph is a gap, not a terminal** — graph and index tools cover only the repositories in their manifest, so search the repository directly before classifying the crossing. When emit or receive evidence suggests the sibling exists but the other side or binding remains missing, record an Assumption; when that gap could change chain completeness or the framed answer, also record the consequence as an Unknown.
- **Too many steps in a chain lane hide an unfinished chain** — one deployable's mechanism can consume the run before downstream boundaries are proved, so keep only 1–5 boundary-relevant major steps and offer a Behavior follow-up after the chain closes.
