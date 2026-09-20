# Flow Research: {{flowName}}

**Rules** — apply while filling this scaffold, then delete this block and every `**Rules:**` line from the result.

- Every claim carries `path:line`, or the IaC/config line for a terminal system; a bare service name is not evidence.
- Every handoff carries an emit-side citation **and** a receive-side citation. One side alone belongs in Assumptions, not in Handoffs.
- Executing code and a probed correlation id prove the chain; deployment diagrams, READMEs, and team knowledge state only intent — record any mismatch as a finding.
- Lane internals stay in the lane's own document. Nothing here describes what happens inside a deployable beyond one line.

- Question: {{the exact end-to-end outcome being traced}}
- Chain: {{first deployable}} → {{…}} → {{terminal system}}
- Status: chain mapped | lanes {{n}}/{{m}} traced | answered

## Summary

**Rules:** 2-3 sentences answering the framed question across the whole chain. Lead with whatever most surprises a reader who assumed the obvious topology.

{{summary}}

## Chain

**Rules:** a swimlane — one lane per deployable, terminal systems as edge lanes, every arrow labelled with its contract. When a diagram skill owns that type, its template governs syntax and styling. Add a container diagram above it only past roughly eight lanes.

{{diagram}}

## Inputs

**Rules:** chain entries only — what originates the flow from outside the whole system. An inbound call from a deployable already in the chain is a handoff, not an input.

| # | Input | Actor | Lands in | Carries | Evidence |
|---|---|---|---|---|---|
| 1 | {{route, schedule, webhook, upstream system, batch drop}} | {{who or what triggers it}} | {{lane #}} | {{payload or message}} | {{path:line}} |

## Lanes

**Rules:** one row per deployable, in chain order. `Does` is one line — the mechanism belongs to the lane document. `Depth` is `contract`, `traced`, or `deep`; only `deep` lanes have a document.

| # | Deployable | Receives | Does | Emits | Depth | Doc |
|---|---|---|---|---|---|---|
| 1 | {{service, container, lambda, worker}} | {{inbound contract}} | {{one line}} | {{outbound contract}} | {{contract \| traced \| deep}} | {{link, or —}} |

**Rules:** one cited paragraph per `traced` lane, under a `### {{lane}}` subsection. Omit the section when no lane is `traced`.

{{tracedLaneNotes}}

## Handoffs

**Rules:** one row per edge between lanes. Both citations required. `Binding` is the IaC, compose, or config line proving both sides address the same real resource.

| Edge | Kind | Contract | Emit site | Receive site | Binding |
|---|---|---|---|---|---|
| {{1→2}} | {{HTTP, gRPC, queue, topic, shared table, file drop}} | {{schema or operation, with version}} | {{path:line}} | {{path:line}} | {{path:line}} |

## Terminals

**Rules:** one row per edge where research stops. `Why terminal` is `no source access` or `out of framed scope` with its reason — an unresolved reason means the row belongs in Frontier instead. `Real target` cites the IaC or config naming the resource, region, and account actually addressed.

| System | Reached from | Contract | Why terminal | Real target |
|---|---|---|---|---|
| {{managed service, database, third-party API}} | {{lane #}} | {{operation, parameters, error surface}} | {{no source access \| out of framed scope — reason}} | {{path:line, or —}} |

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

**Rules:** lanes deliberately not traced yet — deferred scope, distinct from Unknowns. `Next question` is the verbatim frame the next `research-capability` run takes as its question, so resuming needs no rethinking.

| # | Lane | Not traced because | Next question |
|---|---|---|---|

## Conclusion

**Rules:** state the explanation the facts support across the chain, and name the lane that actually decides the outcome when several touch it.

{{conclusion}}
