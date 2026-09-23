# Behavior Inspection: {{functionalSliceName}}

**Rules** — apply while filling this scaffold, then delete this block and every `**Rules:**` line from the result.

- Question, Scope, and Summary use domain anchors — capability, feature, functional slice, actor, action, object, outcome, named external system — without source paths, routes, code symbols, configuration keys, or implementation-layer terms.
- Summary claims cite numbered Facts; every repository file mention and technical claim elsewhere carries a file reference per **File references** in the skill. A bare symbol name is not evidence.
- Quote the deciding line whenever it is short enough to settle the claim on sight.
- Executing code proves behavior; tests, comments, and docs state only intent — record any mismatch as a finding.
- Nothing reaches the diagram, tables, or conclusion without a Fact behind it.
- Scope is one deployable. The only cross-boundary nodes allowed are this unit's own triggers and observable outcomes; upstream and downstream internals belong to their own documents.

- Capability: {{stable product ability this slice realizes}}
- Feature: {{user-meaningful behavior that realizes the capability}}
- Functional slice: {{end-to-end behavior or outcome inspected here}}
- Question: {{the exact domain question — actor, action, object, outcome}}
- Scope: {{the domain boundary, named external systems, and what's explicitly out}}
- Chain: {{link to the chain document and this lane's number, or — when researched standalone}}
- Inbound: {{the contract this lane receives and its handoff evidence, or — when researched standalone}}
- Status: investigating | answered

## Summary

**Rules:** 2-3 domain-facing sentences answering the framed question. Lead with whatever most surprises a reader who assumed the obvious mechanism, and cite each claim by Fact number instead of source path.

{{summary}}

## Mechanism

**Rules:** pick, label, and split the diagram per **Behavior — one deployable** in the skill; the owning diagram skill's template governs syntax and styling — do not compose a Mermaid skeleton from this template. Every node traces back to a Fact row; the tables below carry the citations. Give each extra diagram a `### {{question this diagram answers}}` subsection.

{{diagram}}

## Triggers

**Rules:** one row per in-scope way in — route, GUI action, client library, CLI, scheduled job, queue/event consumer, webhook. `Does differently` records auth, validation, defaults, or deserialization unique to that trigger; `Converges at` is the cited symbol where it joins the shared path.

| Trigger | Initiated by | Does differently | Converges at | Evidence |
|---|---|---|---|---|
| {{route, action, schedule, message, or call}} | {{actor or upstream system}} | {{auth/validation/defaults, or none}} | {{symbol and file reference}} | {{file reference}} |

## Observable outcomes

**Rules:** one row per independently observable outcome — persisted write, published event, outbound call, file, cache invalidation, notification, response payload, consumed log/metric. Reads, validations, branch decisions, internal calls, and calculations stay in Mechanism or Facts unless they create an observable result. Split outcomes with different timing or transactionality. `When` says unconditional or names the condition; `Transactional with` names what commits or rolls back alongside it. An outcome leaving the deployable carries its contract — operation or schema, parameters, error surface — in `Outcome`.

| Outcome | Kind | When | Transactional with | Evidence |
|---|---|---|---|---|
| {{observable result}} | {{write, event, outbound call, response, file, cache, notification}} | {{unconditional, or the condition}} | {{shared transaction/unit of work, or independent}} | {{file reference}} |

## Providers and fallback

**Rules:** one row per provider reachable for the framed case, doubles included — a mock, stub, in-memory fake, or recorded response is a provider whose selector is an environment or profile. Keep the section when a single provider is confirmed to be the only one, and say so. `Selected when` names the config key, flag, or tweak and the deciding value, including the default when it is absent. Record the outbound call under Observable outcomes too: that section says what leaves; this one says why this provider serves it and what follows failure.

| Provider | Selected when | Falls back to | Failure trigger | Evidence |
|---|---|---|---|---|
| {{client or implementation}} | {{key=value, flag, tweak, environment, or default}} | {{next source, or none}} | {{exception, timeout, status code, invalid-result rule}} | {{file reference}} |

**Rules:** state the terminal behavior when every provider fails, whether the selector is read per call or once at startup, and whether a fallback result is cached — each cited.

{{providerSelectionNotes}}

## Facts

**Rules:** one row per confirmed claim. Prefer facts that contradict the default assumption over facts that confirm it.

| # | Fact | Evidence |
|---|---|---|
| 1 | {{fact}} | {{file reference — `deciding line quoted`}} |

## Assumptions

**Rules:** plausible but unconfirmed. `What would verify it` is a concrete action — a command, a probe, a file to open — not "investigate further".

| # | Assumption | Why unverified | What would verify it |
|---|---|---|---|

## Unknowns

**Rules:** `Next probe` names the exact search, command, or file to open.

| # | Unknown | Next probe |
|---|---|---|

## Conclusion

**Rules:** state the explanation the facts support, and name which artifact actually enforces the behavior when several describe it.

{{conclusion}}
