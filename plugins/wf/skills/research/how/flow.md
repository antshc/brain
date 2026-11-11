# Flow axis — cross-deployable slice chain

Start with boundaries. One deployable and its functional slice form one lane. Trace each outcome-relevant handoff through the systems whose source is available. Apply Behavior checks within a lane when its internal decision changes the answer.

Map each handoff to a row, then verify sender, wire contract, receiver, and deployment or configuration binding. Stop at a terminal infrastructure boundary only after recording the operation, protocol, authentication, errors, and relevant configuration.

Add findings to the How explanation; the caller owns any save destination.

## Contents

- Presentation
- Deployable eligibility
- Workflow
- Boundary
- Integration contract
- Handoff evidence
- Chain check
- Gotchas

## Presentation

The Explainer chooses the view under Visualize: ownership/responsibility → swimlane or container; interaction order → sequence. If lanes help, use one per deployable and 1–5 boundary-relevant steps per lane; label crossings with contracts. Back every node/crossing with evidence. Do not require a diagram when prose or a table answers the question.

## Deployable eligibility

A lane is a **deployable**: a unit independently runnable or deployed in production — a process, service, container, function, host workload, or scheduled job that the platform starts on its own.

**Eligibility test** — does production start this unit independently? Yes → it earns a lane. No → it is an artifact, and it belongs inside the lane of whatever executes it.

Upgrade bundles, installers, shell and Python scripts, Ansible playbooks, Helm charts, Terraform modules, SQL migrations, and libraries are **artifacts** unless independently started/deployed; verify the executing unit. Name the executing deployable as the lane and record the artifact as what that lane *does*. A bundle executed by a privileged host agent is one lane — the agent — not two.

## Workflow

1. **Frame the chain** — name the outcome traced, not the service. "Where does a placed order become reserved stock?" beats "how does ordering work?".
2. **Find the chain entries** — what originates the flow from outside the whole system: user action, schedule, webhook, upstream system, batch drop. An inbound call from a deployable already in the chain is a handoff, not an entry.
3. **Walk lane by lane** — per deployable record what it receives, 1–5 ordered major steps, and what it emits. A major step is a boundary-relevant responsibility needed to explain how the inbound contract becomes the outbound contract; collapse implementation details that do not change that explanation. Read only enough client call sites, routes, publish/subscribe calls, SDK use, auth configuration, error handling, and IaC bindings to prove the steps and next crossing; apply the Behavior lens in the same report when an internal decision affects the outcome.
4. **Classify every edge** — continuable or terminal (see Boundary). Continue when the next deployable's executing source opens and its behavior can change the framed outcome. Otherwise record a proven external terminal, explicit scope stop, or inaccessible-source stop with its reason and coverage consequence; keep an unconfirmed crossing in Gaps.
5. **Complete the chain** — reach a terminal for every in-scope branch. Trace deciding lane behavior and storage or provider semantics as needed to settle the question. Record outcome-irrelevant siblings as scope stops and cycles as handoffs back to an existing lane.
6. **Check the chain at runtime** when runtime confirmation matters. Follow Chain check and Inspection evidence runtime rules.
7. **Explain the chain** — use the How mechanism. If a table clarifies the trace, give each deployable one row in chain order, with the inbound contract, ordered major steps, outbound contract, and evidence. Render any included diagram.

**Done when** each entry reaches a lane, each in-scope branch reaches a terminal or a recorded gap, and each internal handoff has emit, receive, and binding citations. Record why each terminal ends the trace. Back the mechanism and any diagram with confirmed evidence.

## Boundary

Two kinds of crossing, with different stop semantics.

| | Terminal | Continuable |
|---|---|---|
| What | managed service reached through an SDK or API (DynamoDB, S3, SQS, Stripe), database engine, third-party API, OS primitive | a deployable whose source you can open — microservice, container, lambda, queue consumer, sibling repo |
| Record | the integration contract and the IaC/config naming the real resource, region, and account | the integration contract plus emit site, receive site, and binding |
| Becomes | a terminal Boundary contract | the next Flow row plus an internal Boundary contract |

**Continue test** — keep following a hop while its executing source opens **and** the framed outcome depends on what happens there. Either answer turns no → classify the stop and record its contract, reason, and coverage consequence. Inaccessible source does not establish downstream behavior. Unfamiliarity, repository distance, and lane count are not stop conditions.

A deployable often emits to several downstreams. Expand only the ones on the path to the framed outcome; record the siblings as scope stops with a one-line reason. This is what keeps a mesh from swallowing the research.

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
