# Flow Research: {{flowName}}

**Rules** — apply while filling this scaffold, then delete this block and every `**Rules:**` line from the result.

- Every claim carries `path:line`, or the IaC/config line for a terminal system; a bare service name is not evidence.
- Every boundary records API/event, SDK, protocol, auth, errors, and binding. Use `—` only when an aspect does not apply.
- Every internal handoff carries an emit-side citation **and** a receive-side citation. One side alone belongs in Assumptions, not in Handoffs.
- Executing code and a probed correlation id prove the chain; deployment diagrams, READMEs, and team knowledge state only intent — record any mismatch as a finding.
- This file is the whole deliverable. Lane internals stay out of it — nothing here describes what happens inside a deployable beyond one line — and no second document is written unless the user asks for a lane deep dive.

- Question: {{the exact end-to-end outcome being traced}}
- Chain: {{first deployable}} → {{…}} → {{terminal system}}
- Status: chain mapped | lanes {{n}}/{{m}} traced | answered

## Summary

**Rules:** 2-3 sentences answering the framed question across the whole chain. Lead with whatever most surprises a reader who assumed the obvious topology.

{{summary}}

## Chain

**Rules:** a rendered Mermaid **swimlane** per **Deployables — one chain** in the skill — one lane per deployable, terminal systems as edge lanes, every arrow labelled with its contract.

{{diagram}}

## Inputs

**Rules:** chain entries only — what originates the flow from outside the whole system. An inbound call from a deployable already in the chain is a handoff, not an input.

| # | Input | Actor | Lands in | Carries | Evidence |
|---|---|---|---|---|---|
| 1 | {{route, schedule, webhook, upstream system, batch drop}} | {{who or what triggers it}} | {{lane #}} | {{payload or message}} | {{path:line}} |

## Lanes

**Rules:** one row per deployable — something production starts independently — in chain order, each appearing exactly once. Bundles, scripts, playbooks, charts, and libraries belong inside the lane that executes them. `Does` is one line. `Depth` is `contract`, `traced`, or `deep`; `deep` names a lane worth a later Capability-axis run, recorded in Frontier.

| # | Deployable | Receives | Does | Emits | Depth |
|---|---|---|---|---|---|
| 1 | {{service, container, lambda, worker, host agent}} | {{inbound contract}} | {{one line}} | {{outbound contract}} | {{contract \| traced \| deep}} |

**Rules:** one cited paragraph per `traced` lane, under a `### {{lane}}` subsection. Omit the section when no lane is `traced`.

{{tracedLaneNotes}}

## Handoffs

**Rules:** one row per internal edge. Both code citations required. `API/event` names the operation or route, parameters, or topic/schema/version. `SDK` names package/version and method. `Errors` includes statuses, exceptions or failure events and relevant timeout/retry/idempotency/DLQ behavior. `Binding` proves both sides address the same resource.

| Edge | API/event | SDK | Protocol | Auth | Errors | Emit site | Receive site | Binding |
|---|---|---|---|---|---|---|---|---|
| {{1→2}} | {{operation or schema/version}} | {{package@version; method, or —}} | {{HTTP, gRPC, AMQP, ...}} | {{identity; mechanism; permissions}} | {{error contract and resilience}} | {{path:line}} | {{path:line}} | {{path:line}} |

## Terminals

**Rules:** one row per external or out-of-scope edge. Cite authoritative contract documentation for semantics not encoded in the repository. `Why terminal` is `no source access` or `out of framed scope` with its reason; unresolved edges belong in Frontier. `Real target` cites config or IaC naming the resource, region, and account.

| System | From | API/event | SDK | Protocol | Auth | Errors | Why terminal | Real target |
|---|---|---|---|---|---|---|---|---|
| {{managed service, database, third-party API}} | {{lane #}} | {{operation or schema/version}} | {{package@version; method, or —}} | {{transport and serialization}} | {{identity; mechanism; permissions}} | {{error contract and resilience}} | {{no source access \| out of framed scope — reason}} | {{path:line}} |

## Chain probe

**Rules:** the correlation id, the command issued, and which handoffs it confirmed. Handoffs the probe never lit stay assumptions. Omit the section when no probe was run, and say so in Unknowns.

{{chainProbe}}

## Facts

**Rules:** one row per confirmed claim about the chain — ordering, retries, duplication, transactional scope, what survives a lane failing. Prefer facts that contradict the assumed topology over facts that confirm it.

| # | Fact | Evidence |
|---|---|---|
| 1 | {{fact}} | {{path:line — `deciding line quoted`}} |

## Assumptions

**Rules:** plausible but unconfirmed, including every handoff cited on one side only. `What would verify it` is a concrete action — a command, a probe, a file to open.

| # | Assumption | Why unverified | What would verify it |
|---|---|---|---|

## Unknowns

**Rules:** `Next probe` names the exact search, command, or file to open.

| # | Unknown | Next probe |
|---|---|---|

## Frontier

**Rules:** lanes deliberately not traced yet — deferred scope, distinct from Unknowns. Every `deep` lane appears here as a suggested deep dive. `Next question` is the verbatim frame an optional Capability-axis run takes as its question, so resuming needs no rethinking.

| # | Lane | Not traced because | Next question |
|---|---|---|---|

## Conclusion

**Rules:** state the explanation the facts support across the chain, and name the lane that actually decides the outcome when several touch it.

{{conclusion}}
