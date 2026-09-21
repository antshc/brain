# Feature Research: {{featureName}}

**Rules** — apply while filling this scaffold, then delete this block and every `**Rules:**` line from the result.

- Every claim carries `path:line` or `path:startLine-endLine`; a bare symbol name is not evidence.
- Quote the deciding line whenever it is short enough to settle the claim on sight.
- Executing code proves behavior; tests, comments, and docs state only intent — record any mismatch as a finding.
- Nothing reaches the diagram, tables, or conclusion without a Fact behind it.
- Scope is one deployable. The only cross-boundary nodes allowed are this unit's own entry points and the effects leaving it; upstream and downstream internals belong to their own documents.

- Question: {{the exact question being answered — capability, entry point, specific behavior}}
- Scope: {{repo/service and layers in scope; what's explicitly out, with a link to any doc that owns the excluded area}}
- Chain: {{link to the chain document and this lane's number, or — when researched standalone}}
- Inbound: {{the contract this lane receives and its handoff evidence, or — when researched standalone}}
- Status: investigating | answered

## Summary

**Rules:** 2-3 sentences answering the framed question. Lead with whatever most surprises a reader who assumed the obvious mechanism.

{{summary}}

## Mechanism

**Rules:** pick the diagram type from Diagrams in `SKILL.md`; when a diagram skill owns that type, its template governs syntax and styling — do not compose a Mermaid skeleton from this template. Label every participant, node, and message with trace keywords — the role or step plus a greppable token (route path, config key, event or queue name, table name, interface name) — never class/method names with `path:line`, unless the user asked for them; the tables below carry the citations. Every node still traces back to a Fact row. One diagram by default — multiple entry points enter as parallel participants meeting at the cited convergence point, effects leave from it. Add a `### {{question this diagram answers}}` subsection per extra diagram only when entries never converge, selection and fallback need their own flowchart, effects fire out of band, or the single diagram sprawls past ~12 participants; an extra diagram repeats no node the first already showed.

{{diagram}}

## Entry points

**Rules:** one row per in-scope way in — route, GUI action, client library, CLI, scheduled job, queue/event consumer, webhook. `Does differently` records auth, validation, defaults, or deserialization unique to that entry; `Converges at` is the cited symbol where it joins the shared path.

| Entry point | Trigger | Does differently | Converges at | Evidence |
|---|---|---|---|---|
| {{entry}} | {{request, user action, schedule, message, call}} | {{auth/validation/defaults, or none}} | {{symbol at path:line}} | {{path:line}} |

## Effects

**Rules:** one row per observable outcome — persisted write, published event, outbound call, file, cache invalidation, notification, response payload, consumed log/metric. `When` says unconditional or names the condition; `Transactional with` names what it commits or rolls back alongside. An effect leaving the deployable carries its contract — operation or schema, parameters, error surface — in `Effect`.

| Effect | Kind | When | Transactional with | Evidence |
|---|---|---|---|---|
| {{effect}} | {{write, event, outbound call, response, file, cache, notification}} | {{unconditional, or the condition}} | {{shared transaction/unit of work, or independent}} | {{path:line}} |

## External sources

**Rules:** one row per source reachable for the framed case, doubles included — a mock, stub, in-memory fake, or recorded response is a source whose selector is an environment or profile. Keep the section when a single source is confirmed to be the only one, and say so. `Selected when` names the config key, flag, or tweak and the deciding value, including the default when it is absent.

| Source | Selected when | Falls back to | Demotion trigger | Evidence |
|---|---|---|---|---|
| {{client or implementation}} | {{key=value, flag, tweak, environment, or default}} | {{next source, or none}} | {{exception, timeout, status code, invalid-result rule}} | {{path:line}} |

**Rules:** state the terminal behavior when every source fails, whether the selector is read per call or once at startup, and whether a fallback result is cached — each cited.

{{sourceSelectionNotes}}

## Facts

**Rules:** one row per confirmed claim. Prefer facts that contradict the default assumption over facts that confirm it.

| # | Fact | Evidence |
|---|---|---|
| 1 | {{fact}} | {{path:line — `deciding line quoted`}} |

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
