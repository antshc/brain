---
name: doc-concept
description: Document the body of an arc42 Crosscutting Concept using a business-process, structural implementation, or operational policy one-page template. Use to write or revise shared business process families, architecture or design patterns, or operational conventions; called by record-concept and define-concept.
---

# Document Concept

Render **body only** and return it with its kind to the caller. MUST NOT write files, name records, sync indexes, or invoke a recording skill.

Choose by the shared concern, not the component where it was found; read only the selected template. Return the chosen row's **kind** with the body.

| Concern | Kind | Template |
|---|---|---|
| Business capabilities — the processes that deliver them, and the scenarios each process handles | `dom` | [domain-business-process.md](./templates/domain-business-process.md) |
| Architecture/design patterns (including codebase-specific patterns), domain rules, user-facing validation, transactions, persistence, caching, concurrency, integration | `str` | [structure-implementation.md](./templates/structure-implementation.md) |
| Security, error handling, testing, configuration, migration, installation, logging, disaster recovery, domain safety, runtime safety or batch operations | `ops` | [ops-policy.md](./templates/ops-policy.md) |

Keep one concept per page and aim for one page. Describe a shared approach that governs multiple building blocks; name the affected scope and the conditions under which it applies. If the subject crosses categories, select the template that explains its governing rule best; link related concepts instead of duplicating obligations. Show **how** it works with one representative scenario, code or test anchor where useful. Omit optional sections and inapplicable template prompts.

Each kind fixes its required `##` headings in order — `dom`: `Purpose`, `Definition`, `Business Processes`, `Relationships`; `str`: `Purpose`, `Concept`, `Rules`; `ops`: `Purpose`, `Approach`, `Rules`. `str` then takes an optional tail, in order: `Example`, `Benefits and Trade-offs`, `Validation`, `References`, `Implementation Map`. `ops` takes its own optional tail, in order: `Responsibilities`, `Operational Flow`, `Failure Handling`, `Monitoring and Alerting`, `Security / Safety Controls`, `Procedures`, `Validation / Testing`, `Example`, `References`, `Implementation Map`. `dom` takes `Implementation Map` alone, since its scenario rows already carry conditions, outcomes, and failure behavior. Preserve an existing record's headings when extending it; do not bulk-rewrite old records merely to choose another template.

Write one independently checkable obligation per `Rules` bullet, using MUST, MUST NOT, or SHOULD. Put the reason and application criteria in `str`'s `Concept` or `ops`'s `Approach`, self-contained without following a link. Keep volatile commands and growing inventories in a linked runbook or code, not in the concept.

## Record the house variant

- Name the general pattern in one sentence, with at most one link to an external reference. Do not explain it further.
- Every other paragraph states something this system decided: a bound, a trigger, a state store, a signal, a naming scheme, or an owner.
- **Test:** a sentence that could appear unchanged in a blog post about the pattern → cut it.

## Decisions, not parameters

For `str`, `Concept` states each decision that shapes the design and leaves out values that can change without changing it. Test each candidate: *would changing it require changing the design?*

- **Yes → decision, belongs in `Concept`.** E.g. the loop is driven by orchestrator code, not the prompt or a self-looping agent; code, not an agent signal, decides when to stop (spec has no actionable issues); one unit of work is one spec; attempts are bounded per spec by a persisted counter that resets when the spec's issues resolve; the agent is invoked through a skill command.
- **No → parameter, stays in code or config.** `Implementation Map` may point to it. E.g. `max_executions = 3`, alias `yolo`, a log path, a commit prefix.

Rules cite the decision, not the value: "MUST run the loop in orchestrator code; the prompt MUST NOT contain loop or retry logic", "MUST bound attempts per spec with a configurable counter persisted across runs" — never "MUST stop after 3 iterations".

## Variants

State only chosen approaches. A variant actually in use goes under `Rules` as `### Variant: <name>`, with its own rules and a selection condition. An option not chosen belongs in an ADR, which links to the Concept; never write "the strategy is replaceable".

## Example

Take `Example` from the actual implementation, trimmed to rule-relevant lines; a diagram MAY accompany or replace the code and MUST depict the actual implementation. An invented sketch is allowed only labelled `Sketch — not the implementation`, and it MUST NOT contradict the `Implementation Map`.

## Naming

- **Allowed** in `Concept`, `Rules`, and `Implementation Map` locators: class, interface, and type names that carry a rule (e.g. `IssueFilter`, `ExecutionLog`, `AIAgent`); governed contract names (e.g. skill command `/ralph:dev`).
- **Not allowed:** file paths, directories, modules or namespaces, line numbers; method and function names — name the class and describe the behavior.
- **Greenfield:** name a class only when a decision fixed that name; otherwise describe its role ("the actionable-issue filter") and add the name once the code exists.

## Terminology

Use the project glossary's terms and the exact state, status, and operation names the contracts or source use. A name alone never establishes behavior — read what it does.

## Evidence

A Concept states settled behavior. Resolve open questions, alternatives, and recommendations before writing, and keep a codebase observation out of the normative rules until a decision makes it policy.

Verify every Implemented claim against current contracts, source, and tests; a Decided rule (target code does not exist yet; decision from the user, caller, or an ADR) needs no implementation check. Write `not verified` rather than claiming an implementation is absent — an absence claim is earned only by searching the complete owning repository, and it goes stale the moment someone adds the thing.

## Implementation Map

An optional closing section, for a record whose rules an agent has to relocate in code. Two columns carry the weight: a **stable anchor** that outlives refactoring, and a **semantic locator** that finds today's implementation.

```md
## Implementation Map
| Concern | Stable anchor | Semantic locator |
|---|---|---|
| External contract | <Operation, event, configuration contract, or "No external contract"> | `<repository>`: <operation, event, or configuration keys> |
| Dispatch | <Actor-visible trigger and owning boundary> | `<repository>`: <interface, abstraction, or type names> |
| Application boundary | <Capability exposed by the owning context> | `<repository>`: <interface or abstraction names> |
| Execution | <Responsibility performed> | `<repository>`: <executor interface or type names> |
| Lifecycle state | <Authoritative state and transition owner> | `<repository>`: <state type, state values, or writer abstraction> |
| Persistence | <Persisted entity and ownership> | `<repository>`: <entity and repository abstraction names> |
| Operational evidence | <Durable logs, records, events, or results> | `<repository>`: <log keywords, event, or result type> |
| Tests | <Behavior demonstrated> | `<repository>`: <representative test class names> |
```

Include the smallest useful set of concerns and drop the rest. A stable anchor is an enduring contract, responsibility, persisted entity, configuration key, or bounded-context role — write it so the row still reads correctly with the locator column deleted. Cite a stable interface, contract, or abstraction before an implementation type; name one primary locator per concern and at most two supporting ones. Identify non-code evidence by API operation, configuration key, persisted entity or attribute, event name, log keyword, or test class name, and say what behavior the cited tests demonstrate. Qualify an ambiguous identifier with its repository and bounded context. Locators stay greppable: names and keywords, never a revision, source path, directory, line number, namespace, or exact method name.

## Quality gate

- Every `str` or `ops` `Rules` bullet is one checkable obligation, shared across the governed scope.
- `Purpose` names the problem in this system, not the problem in general.
- `Concept` has at most one sentence of general pattern definition.
- Every `Rules` bullet relies on at least one decision of this system (bound, trigger, state store, signal, naming scheme, owner) or a governed name.
- Every `Rules` bullet has an `Implementation Map` row, reads `not verified`, or is a Decided rule whose code does not exist yet.
- No `Rules` bullet states a tunable value; no unchosen option or variant without a selection condition remains.
- `Example` is the real implementation or carries the `Sketch — not the implementation` label.
- No file path, directory, namespace, line number, or method name appears in the body.
- A `dom` page covers one business capability, and every `###` process under it carries the `Actor; Trigger; Action; Outcome` descriptor line.
- A scenario table appears only where the user asked for one, and every row it carries names a concrete business situation and fills `Input`, `Rule/Condition`, and `Output/Expected`.
- Every scenario row is anchored on a business term that survives a refactor, not on a class, method, field, table, or endpoint name.
- A situation with its own actor, trigger, and business outcome is promoted to its own `###` process.
- Process, state, and operation names match project terminology exactly.
- Every `Implementation Map` row survives deleting its `Semantic locator` cell, and every locator is greppable and unambiguous inside the named repository.
- Unverified coverage reads `not verified`; nothing claims an absence the search did not establish.
- No placeholder, open question, contradictory transition, or speculative claim remains.
