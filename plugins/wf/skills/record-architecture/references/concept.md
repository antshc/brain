# Concept

Render or record **one shared approach** governing multiple building blocks. Use the selected mode:

- `concept-body`: follow **Body** through **Quality gate**, then return the body and kind. MUST NOT write files, name records, sync indexes, invoke a recording skill, or switch modes.
- `concept-record`: follow the recording sections below; apply **Body** through **Quality gate** when rendering or revising. Reuse a compliant body supplied by the caller without rendering or interviewing again. Write the record and its index row in the same change.

All sections outside **Body** through **Quality gate** apply only to `concept-record`.

## Where the rule belongs

Runs first, before the Concept gate. Most rules that reach this skill belong somewhere else, and a rule filed in the wrong home is read at the wrong moment — a wording rule buried in a Concept fires during design and stays silent while the file is being written.

Split on **when the rule is needed**:

| The rule answers | Home | Written by |
|---|---|---|
| how a shared business process, implementation, or operational policy governs several building blocks | Concept, `docs/concepts/` | this skill — continue below |
| which approach was chosen and its structural decisions | Concept, `docs/concepts/` | this skill — continue below |
| why it was chosen, and the rejected alternatives | standalone ADR linking to the Concept, or feature design when it fails the ADR gate | load [adr.md](./adr.md); otherwise session ledger / feature design |
| how to word, name, format, or lay out the file being written | an instructions file under `.github/instructions/`, scoped by `applyTo` | edit that file directly |
| what a contested term means | glossary, `GLOSSARY.md` | load [term.md](./term.md) |
| which command, path, or version this one repo uses | the repo's own convention file or memory | edit that file directly |

Two tests settle most cases:

- **Is it reusable inside this system?** Reusable means the next implementer in this system's scope follows the same decided approach. It does not mean the text is portable to other systems — keep what makes it specific. A command, path, or setting alone → a convention file.
- **Is it needed while deciding, or while typing?** Deciding → a record. Typing → write-time guidance, which loads automatically through `applyTo` at the moment it applies.

A rule can be shared across the system *and* have a write-time counterpart. Record the rule once as a Concept, and let the instructions file carry only the wording, naming, or layout that follows from it.

## When to write a Concept

Write one only when all three are true:

1. **Crosscutting** — a business process, structural pattern, or operational policy applies to multiple building blocks or workflows, not just one feature.
2. **Reusable** — the next implementer in this system's scope follows the same decided approach.
3. **Consequential** — it guides a meaningful design or operational choice and can be checked against behavior, code, tests, or configuration.

If any of the three is missing, skip the Concept — route it by *Where the rule belongs* above.

## Extend or create

Runs before any write. A near-duplicate record is worse than a longer one: it splits a decision area across two files instead of sharpening one.

1. *Run `index-docs` skill for trigger-generation, scan/match, and row-sync; use **Scan and match*** over the `Crosscutting Concepts` table with this rule's surface — its terms and the paths it governs.
2. A matched record's scope already covers this decision area → **extend it**: apply **Grounding** and **Body** through **Quality gate** for a body change and sharpen its `default` or `trigger` when needed. Resync its row via **Sync index row**. Stop here.
3. No match covers the area → **create** a new Concept.

## Lazy creation

Create `docs/concepts/` when the first Concept is ready — not before; do nothing if it exists.

## Record identity

A record is named `docs/concepts/{{kind}}-{{slug}}.md`. `{{kind}}` is the selected body template's kind — `dom`, `str`, or `ops` — so the directory listing groups the families; `{{slug}}` is the title in kebab-case. For `dom`, the title is the Business Capability the page covers, so the slug is that capability in kebab-case. Sharpen the slug when a name is already taken; the identity carries no counter, so nothing has to be renumbered.

A record carries no frontmatter — it opens directly with `# {{conceptTitle}}`.

## Grounding

Runs before Body. Give every rule a source and check it by that source:

| Rule source | Check | Record shows it as |
|---|---|---|
| **Implemented** — target code exists | *Run `explore-codebase` skill to find where the rule is implemented — locate symbol, callers, flow.* Code contradicts the rule → stop; ask the user which wins. | `Implementation Map` row |
| **Decided** — target code does not exist yet | Decision comes from the user, the caller, or an ADR. Do not search for an implementation; do not mark it `not verified`. | Rule only, no map row; add the row once code exists |
| **Ported** — rule comes from another project | Restate it in the target's stack and conventions; it then counts as Implemented or Decided. | Per the resulting source |

For ported content:

- Remove every source-stack detail (e.g. `npm run typecheck`, a JS-specific path, a tool the target does not use). Replace it with the target's equivalent, or lift it to the decision: "MUST run the project's configured verification commands before commit from the code not the prompt text."
- Rewrite source-project examples to match how the target implements the concept — its language, structure, and rules — not a syntax translation.
- Keep a source-project parameter (marker, prefix, signal, name) only when the target's code uses it or the user confirms the target chose it; otherwise use the target's own equivalent or drop it.

**Gate:** every rule has code or a decision behind it; no ported record keeps a source-stack detail.

## Body

Choose by the shared concern, not the component where it was found; read only the selected template. Return the chosen row's **kind** with the body.

| Concern | Kind | Template |
|---|---|---|
| Business capabilities — the processes that deliver them, and the scenarios each process handles | `dom` | [domain-business-process.md](../templates/domain-business-process.md) |
| Architecture/design patterns (including codebase-specific patterns), domain rules, user-facing validation, transactions, persistence, caching, concurrency, integration | `str` | [structure-implementation.md](../templates/structure-implementation.md) |
| Security, error handling, testing, configuration, migration, installation, logging, disaster recovery, domain safety, runtime safety or batch operations | `ops` | [ops-policy.md](../templates/ops-policy.md) |

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

## Authoring the index row

A Concept governing multiple building blocks is indexed in `ARCHITECTURE.md`'s `Crosscutting Concepts` table — the row below. A Concept that applies to exactly one Building block is indexed in that block's own `Concepts` table inside its `docs/building-blocks/{{slug}}.md` record instead (or its repository's own Crosscutting Concepts when that repository documents itself) — same authoring rules, different table; never both.

The `ARCHITECTURE.md` row (or the block's row) is authored directly by this skill, not projected from the record — the record carries nothing to project.

1. `title` is the `# ` heading text, used as the record-name column linked to the record path.
2. Author `summary` — 1-2 plain-text sentences describing what the Concept covers; no link.
3. Load [defaults.md](./defaults.md) and author `default` under its contract. A caller-supplied, user-confirmed `default` (from `define-concept`) is used verbatim after the contract check; report a mismatch rather than silently rewriting it.
4. Derive the Trigger condition: *Run `index-docs` skill for trigger-generation, scan/match, and row-sync; use **Generate trigger condition***, passing the rendered body as `{{recordContent}}` and the authored default as `{{rowValues}}`. Confirm every clause's applicability is discoverable.
5. *Run `index-docs` skill for trigger-generation, scan/match, and row-sync; use **Ensure section exists*** for `Crosscutting Concepts`, then its **Sync index row** with `{{rowMetadata}}` = `title`, `summary`, and the `Trigger condition & Default` cell `**Trigger:** {{triggerCondition}}. **Default:** {{default}}` — never edit the table in `ARCHITECTURE.md` directly.

Superseding or retiring a Concept applies the marker to its index row via the same **Sync index row** call; the record itself carries no status field.

## Approval gate

- **Explicit direct request** ("record a Concept for X") — approval is already given; draft and write immediately.
- **Invoked by `define-concept`** — its questioning confirmation settled the concept. Write immediately without a second prompt.
- **Invoked by `grill-design`** — the caller already owns the decision to record, whether it came from the user's answer or from the caller's own assumption. Write immediately; never stop to offer, confirm, or defer. The user reviews the result in `git diff`.
