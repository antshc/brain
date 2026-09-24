---
name: doc-concept
description: Document the body of an arc42 Crosscutting Concept using a business-process, structural implementation, or operational policy one-page template. Use to write or revise shared business process families, architecture or design patterns, or operational conventions; called by record-concept and define-concept.
---

# Document Concept

Render **body only**. `/record-concept` owns frontmatter, record identity, file writes, and index synchronization. Do not edit those surfaces here.

Choose by the shared concern, not the component where it was found; read only the selected template. The chosen row's **kind** is what `/record-concept` prefixes the filename with, so a record sorts next to its siblings.

| Concern | Kind | Template |
|---|---|---|
| Business processes — their triggers, stages, outcomes, and failure behavior | `domain` | [domain-business-process.md](./templates/domain-business-process.md) |
| Architecture/design patterns (including codebase-specific patterns), domain rules, user-facing validation, transactions, persistence, caching, concurrency, integration | `structure` | [structure-implementation.md](./templates/structure-implementation.md) |
| Security, error handling, testing, configuration, migration, installation, logging, disaster recovery, domain safety, runtime safety or batch operations | `ops` | [ops-policy.md](./templates/ops-policy.md) |

Keep one concept per page and aim for one page. Describe a shared approach that governs multiple building blocks; name the affected scope and the conditions under which it applies. If the subject crosses categories, select the template that explains its governing rule best; link related concepts instead of duplicating obligations. Show **how** it works with one representative scenario, code or test anchor where useful. Omit optional sections and inapplicable template prompts.

Each kind fixes its required `##` headings in order — `domain`: `Purpose`, `Definition`, `Process Matrix`, optional `Variants`, `Rules`, `Relationships`; `structure` and `ops`: `Purpose`, `Rules`, `Design Guidance`. Every kind then takes the same optional tail, in order: `Violation signals`, `Exceptions`, `Examples`, `Consequences`, `Implementation Map`. Preserve an existing record's headings when extending it; do not bulk-rewrite old records merely to choose another template.

Write one independently checkable obligation per `Rules` bullet, using MUST, MUST NOT, or SHOULD. Put the reason and application criteria in `Design Guidance`, self-contained without following a link. State a repo path or symbol only when it is itself governed; otherwise use code and tests as corroborating examples. Keep volatile commands and growing inventories in a linked runbook or code, not in the concept.

## Terminology

Use the project glossary's terms and the exact state, status, and operation names the contracts or source use. A name alone never establishes behavior — read what it does.

## Evidence

A Concept states settled behavior. Resolve open questions, alternatives, and recommendations before writing, and keep a codebase observation out of the normative rules until a decision makes it policy.

Verify every claim against current contracts, source, and tests. Write `not verified` rather than claiming an implementation is absent — an absence claim is earned only by searching the complete owning repository, and it goes stale the moment someone adds the thing.

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

- Every `Rules` bullet is one checkable obligation, shared across the governed scope rather than a copy of a matrix cell.
- The `Process Matrix` names exactly one main process, gives every subprocess its parent, and gives every separately triggered process its own row — each row carrying a trigger, an availability condition, ordered stages, an outcome, and failure behavior.
- Every variant names its parent process and differs only by data- or state-selected behavior; one with its own trigger or outcome is modelled as a process instead.
- Process, state, and operation names match project terminology exactly.
- Every `Implementation Map` row survives deleting its `Semantic locator` cell, and every locator is greppable and unambiguous inside the named repository.
- Unverified coverage reads `not verified`; nothing claims an absence the search did not establish.
- No placeholder, open question, contradictory transition, or speculative claim remains.
