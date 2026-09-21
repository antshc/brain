# Deployables axis — one chain

Breadth first, depth later. One deployable is one lane; the chain continues through every outcome-relevant system whose executing source you can open, and ends at the systems whose source you cannot. **One chain run produces one document.** Depth inside a lane belongs to the **Capability** axis, offered as a follow-up once the chain is complete.

## Tiers

| | This axis — chain | Capability axis — lane |
|---|---|---|
| Unit | one deployable = one lane | one symbol = one participant |
| Diagram | swimlane | sequence |
| Evidence | the wire: emit site + receive site + the binding naming the real resource | `path:line` along the call chain |
| Stops at | terminal external systems | that lane's inbound entry and outbound effects |

## Deployable eligibility

A lane is a **deployable**: a unit independently runnable or deployed in production — a process, service, container, function, host workload, or scheduled job that the platform starts on its own.

**Eligibility test** — does production start this unit independently? Yes → it earns a lane. No → it is an artifact, and it belongs inside the lane of whatever executes it.

Upgrade bundles, installers, shell and Python scripts, Ansible playbooks, Helm charts, Terraform modules, SQL migrations, and libraries are **artifacts**. Name the executing deployable as the lane and record the artifact as what that lane *does*. A bundle executed by a privileged host agent is one lane — the agent — not two.

## Workflow

1. **Frame the chain** — name the outcome traced, not the service. "Where does a placed order become reserved stock?" beats "how does ordering work?".
2. **Find the chain entries** — what originates the flow from outside the whole system: user action, schedule, webhook, upstream system, batch drop. An inbound call from a deployable already in the chain is a handoff, not an entry.
3. **Walk lane by lane, shallow** — per deployable record what it receives, does in one line, and emits. Read client call sites, routes, publish/subscribe calls, SDK use, auth configuration, error handling, and IaC bindings; leave internals for a later lane trace.
4. **Classify every edge** — continuable or terminal (see Boundary). A continuable edge extends the chain; a terminal edge closes it with a contract. Keep walking while the next system is outcome-relevant and its executing source opens.
5. **Probe the chain** (see Chain probe) — one real correlation id beats any amount of static reading for proving the lanes actually connect.
6. **Rank lanes by depth need** — `contract`, `traced`, or `deep` (see Depth dial). Rank against the framed outcome, not against how interesting the code looks.
7. **Draw and render the chain** (see **Deployables — one chain** in [SKILL.md](../SKILL.md)) — the swimlane is part of the deliverable, not an illustration added afterwards.
8. **Offer the deep dives** — list the `deep` lanes and their Frontier questions in the report back to the user, and stop. Run the **Capability** axis on a lane only when the user asks for it, passing that lane's Frontier question verbatim as the framed question and its inbound contract as the entry point.

**Done when** the chain document is the only file written; every entry reaches a lane; every deployable appears exactly once as a lane and every artifact sits inside its executing lane; every lane is `contract`/`traced`/`deep`; the swimlane renders and every terminal sits at a diagram edge; every boundary records its API or event, SDK, protocol, auth, and error contract; every internal handoff has emit- and receive-side citations; every terminal says why research stops; and every deferred lane has a verbatim next frame.

## Boundary

Two kinds of crossing, with different stop semantics.

| | Terminal | Continuable |
|---|---|---|
| What | managed service reached through an SDK or API (DynamoDB, S3, SQS, Stripe), database engine, third-party API, OS primitive | a deployable whose source you can open — microservice, container, lambda, queue consumer, sibling repo |
| Record | the integration contract and the IaC/config naming the real resource, region, and account | the integration contract plus emit site, receive site, and binding |
| Becomes | a Terminals row | the next Lanes row |

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

**Every handoff carries two citations — the emit site and the receive site.** A producer publishing to a topic proves nothing about who consumes it, and a consumer subscribing proves nothing about who fills it. One side alone is an ASSUMPTION row, not a handoff row. The binding — Terraform, Bicep, compose file, config key — is the third citation that proves both sides mean the same real resource rather than two same-named ones in different accounts.

Guessed topology is the default failure of cross-service tracing, and this rule is what makes it falsifiable.

## Chain probe

Issue one real request carrying a correlation id, then collect that id across every deployable's logs or distributed trace. Every handoff the id lights up becomes a Fact in one action, and lanes the static read missed surface here. Record the correlation id and the command issued so the trace is re-runnable; handoffs the probe never lit stay assumptions.

## Depth dial

Depth records how much research a lane earned, not how many files the run writes.

| Depth | Meaning | Costs |
|---|---|---|
| `contract` | only its inputs and outputs matter to the outcome | the Lanes row is the whole research |
| `traced` | its internal mechanism matters in outline | one cited paragraph in this doc |
| `deep` | the outcome turns on how it works inside | a Frontier question offered to the user as an optional Capability-axis run |

No depth writes a second file. `deep` marks a lane as *worth* its own document; the user decides whether that document gets written.

## Gotchas

- **A lane that appears twice is one lane revisited, not two** — a chain that returns to an earlier deployable is a cycle; record the second crossing as a handoff back to the existing lane number and stop, or the walk never terminates.
- **An artifact given its own lane invents a deployable that production never starts** — a bundle, script, playbook, or chart shows up in logs and file trees like a participant, so apply the eligibility test before drawing a lane for anything you cannot point at a process for.
- **A missing sibling in a code graph is a gap, not a terminal** — graph and index tools cover only the repositories in their manifest, so treat their paths as candidate navigation and confirm the boundary by searching the repository directly before writing a Terminals row.
