---
name: trace-chain
description: Trace a flow end-to-end across deployable units — services, containers, queues, databases, managed services — down to the terminal external systems where research cannot continue, and document it as a swimlane whose every handoff is cited on both sides. Use when the question spans more than one service, when asked what happens after a request or message leaves a service, which system finally handles it, where the flow ends, whether an external system can be researched further, or to map the whole chain before researching any single service in depth.
---

# Trace a chain across deployables

Breadth first, depth later. One deployable is one lane; the chain ends at the systems whose source you cannot open. Depth inside a lane belongs to `research-capability`, which this skill runs per lane.

**Single deployable? Run `/research-capability` skill instead** — this skill earns its cost only when the flow crosses a process boundary.

## Tiers

| | This skill — chain | `research-capability` — lane |
|---|---|---|
| Unit | one deployable = one lane | one symbol = one participant |
| Diagram | swimlane | sequence |
| Evidence | the wire: emit site + receive site + the binding naming the real resource | `path:line` along the call chain |
| Stops at | terminal external systems | that lane's inbound entry and outbound effects |
| Output | `docs/ongoing/{{slug}}/README.md` | `docs/ongoing/{{slug}}/{{n}}-{{deployable}}.md` |

Grounding is shared, not restated: follow `/research-capability` skill **Evidence ladder**, **Claim types**, and **Citations** for every claim written here.

## Workflow

1. **Frame the chain** — name the outcome traced, not the service. "Where does a placed order become reserved stock?" beats "how does ordering work?".
2. **Find the chain entries** — what originates the flow from outside the whole system: user action, schedule, webhook, upstream system, batch drop. An inbound call from a deployable already in the chain is a handoff, not an entry.
3. **Walk lane by lane, shallow** — per deployable record only what it receives, what it does in one line, and what it emits. Read the wire, not the internals: client call sites, route registrations, publish/subscribe calls, IaC bindings. Resist opening the first lane deeply — a later lane routinely makes an earlier one irrelevant.
4. **Classify every edge** — continuable or terminal (see Boundary). A continuable edge extends the chain; a terminal edge closes it with a contract.
5. **Probe the chain** (see Chain probe) — one real correlation id beats any amount of static reading for proving the lanes actually connect.
6. **Rank lanes by depth need** — `contract`, `traced`, or `deep` (see Depth dial). Rank against the framed outcome, not against how interesting the code looks.
7. **Deep-dive** — per `deep` lane, Run `/research-capability` skill passing the lane's Frontier question verbatim as its framed question, and the lane's inbound contract as its entry point. Write its doc beside this one and link it from the lane row.

**Done when** every chain entry reaches a lane, every lane is classified `contract`/`traced`/`deep`, every handoff carries emit-side and receive-side citations, every terminal states why research stops, every `deep` lane has its doc, and every untraced lane sits in Frontier with a verbatim next frame.

## Boundary

Two kinds of crossing, with different stop semantics.

| | Terminal | Continuable |
|---|---|---|
| What | managed service reached through an SDK or API (DynamoDB, S3, SQS, Stripe), database engine, third-party API, OS primitive | a deployable whose source you can open — microservice, container, lambda, queue consumer, sibling repo |
| Record | the contract: operation, parameters, consistency and idempotency, error surface, plus the IaC or config line naming the real resource, region, and account | the wire: the request or message emitted, its schema or topic, and the consuming deployable |
| Becomes | a Terminals row | the next Lanes row |

**Stop test** — follow a hop only when its source is reachable **and** the framed outcome depends on what happens there. Either answer is no → terminal, write the contract, stop.

A deployable often emits to several downstreams. Expand only the ones on the path to the framed outcome; record the siblings as terminal by scope with a one-line reason. This is what keeps a mesh from swallowing the research.

## Handoff evidence

**Every handoff carries two citations — the emit site and the receive site.** A producer publishing to a topic proves nothing about who consumes it, and a consumer subscribing proves nothing about who fills it. One side alone is an ASSUMPTION row, not a handoff row. The binding — Terraform, Bicep, compose file, config key — is the third citation that proves both sides mean the same real resource rather than two same-named ones in different accounts.

Guessed topology is the default failure of cross-service tracing, and this rule is what makes it falsifiable.

## Chain probe

Static reading settles what the code *can* do; a probe settles what it *does*. Issue one real request carrying a correlation id, then collect that id across every deployable's logs or distributed trace. Every handoff the id lights up becomes a Fact in one action, and lanes the static read missed surface here. Record the correlation id and the command issued so the trace is re-runnable; handoffs the probe never lit stay assumptions.

## Depth dial

Not every lane earns its own document.

| Depth | Meaning | Costs |
|---|---|---|
| `contract` | only its inputs and outputs matter to the outcome | the Lanes row is the whole research |
| `traced` | its internal mechanism matters in outline | one cited paragraph in this doc |
| `deep` | the outcome turns on how it works inside | its own `research-capability` doc |

Without this dial a five-lane chain produces five documents when two carry the answer.

## Output

Write the chain to `docs/ongoing/{{slug}}.md` unless the user names a location. Lane documents are siblings named `{{n}}-{{deployable}}.md`, numbered by lane order.

Fill [chain-trace-template.md](chain-trace-template.md), obeying its `**Rules**` blocks and deleting every one of them from the result.

## Diagrams

The chain diagram is a **swimlane** — one lane per deployable, terminal systems as edge lanes, every arrow labelled with its contract. Run `/behavior-diagram` skill for its syntax and styling. Every lane and every arrow names the evidence that established it.

Add a **container diagram** above it only when the lane count passes roughly eight and the reader needs the shape before the sequence of handoffs. Run `/architecture-diagram` skill for its syntax and styling. Lane internals are never drawn here — they belong to the lane's own sequence diagram, per `/research-capability` skill **Diagrams**.

## Gotchas

- **A lane that appears twice is one lane revisited, not two** — a chain that returns to an earlier deployable is a cycle; record the second crossing as a handoff back to the existing lane number and stop, or the walk never terminates.
- **A trace that ends in a double proves the wiring, not the behavior** — an environment or profile that swaps a lane for a mock, stub, or recorded response makes that lane's contract real and its behavior fictional. Record the double as its own Fact and follow the real deployable for behavior claims.
