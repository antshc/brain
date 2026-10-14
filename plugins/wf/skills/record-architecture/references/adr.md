# Record ADR

Record **one point-in-time, localized architectural decision** into `docs/adr/` — what was decided, why, and which options were rejected. For a compact decision inside a design or decision list, load [decision-bullet.md](./decision-bullet.md) instead.

## Where it belongs

An ADR answers **which option was chosen and why the others were not**. How the decision is applied or implemented belongs elsewhere — a [Concept](./concept.md), a design doc, or the code — and the ADR links to it rather than restating it. Contested terminology → load [term.md](./term.md).

## ADR gate

Record only when all three are true:

1. **Hard to reverse** — changing your mind later carries meaningful cost.
2. **Surprising without context** — a future reader will wonder "why did they do it this way?"
3. **A real trade-off** — genuine alternatives existed; one was picked for specific reasons.

Qualifies: architectural shape; integration patterns between contexts; technology choices carrying lock-in (not every library); boundary and ownership decisions, where the explicit no-s matter as much as the yes-s; deliberate deviations from the obvious path; constraints invisible in the code (compliance, latency contracts); rejected alternatives whose rejection is non-obvious.

Any miss → write nothing, including on an explicit request. Return the miss and the narrower home: feature decision in the session ledger, a design doc, [Concept](./concept.md), or [term](./term.md).

## Scope

Set `@decisionScope` before **Extend or create**: the entity the decision was made for (`narrow`, e.g. tasks) or every member of a named class (`wide`, e.g. every append-only history store).

- Context states the scope explicitly → use it.
- Unstated → ask one question phrased so yes accepts the recommendation: "Does this apply only to `{{entity}}`, or to every `{{class}}`?" Recommend `narrow` unless context names a second member of the class. Invoked by `grill-design` → return the question to the caller as a pending write; write after the answer.
- Never widen from analogy, naming similarity, or a single case. A temporary mitigation or stopgap stays `narrow`.
- `wide` MUST name the class by a property a future reader can check (e.g. "append-only, never deleted"), not by listing entities.

## Extend or create

Runs before any write. A near-duplicate ADR splits authority over one decision area.

1. *Run `index-docs` skill for trigger-generation, scan/match, and row-sync; use **Scan and match*** over the `Architecture Decision Records` table in `ARCHITECTURE.md` and every matched building block's `Architecture Decision Records` table with this decision's surface — its terms and the paths it governs; for `wide`, also the class terms.
2. A matched ADR already owns this decision area and the decision still stands → **extend it**: amend the body and resync its row via **Sync index row**. Scope changed (e.g. `narrow` → `wide`) → rewrite the scope sentence and regenerate the Trigger condition and Default. Stop here.
3. A matched ADR owns the area but this decision reverses it → **rewrite it in place**; never create a second ADR:
   - Rename the file to `docs/adr/{{newSlug}}.md` and update every inbound link to the old path.
   - Rewrite the heading and body to state the new decision.
   - Add the previous decision to `## Considered Options` as `**{{previousDecision}}** — rejected: {{reasonItWasReversed}}`, keeping the options already listed.
   - **Sync index row** `supersede` on its row with the new path, title, Summary, Trigger condition, and Default.
4. No match → **create** a new ADR.

## Lazy creation

Create `docs/adr/` when the first ADR is ready — not before; do nothing if it exists.

## Record name

Name the file `docs/adr/{{slug}}.md`, `{{slug}}` the title in kebab-case. The name carries no counter; sharpen the slug when it is already taken by an unrelated ADR.

## Body

No frontmatter — the record opens directly with its heading.

```md
# {{decisionTitle}}

{{1-3 sentences: what context required a decision, what was decided, and why.}} {{scopeSentence|Applies only to <entity>. — or — Applies to every <class>: <checkable property>.}}

## Considered Options

- **{{rejectedOption}}** — rejected: {{reason}}

## Consequences

- {{nonObviousDownstreamEffect}}

See [{{conceptOrDocTitle}}]({{relativePath}}) for how it is applied.
```

### Rules

- **Considered Options is mandatory** — at least one genuine rejected alternative with its reason. None can be stated → the trade-off criterion fails; write nothing. Never invent an option or a reason.
- **Harvest options automatically** — collect every rejected alternative and its rejection reason from context without asking: the conversation, grill-design answers, the session ledger, linked docs, and the code. Record each as `**{{rejectedOption}}** — rejected: {{reason}}`.
- **User-supplied options** — when the user stated options or rejections, use all of them; rephrase each into the bullet form, terse and decision-focused, preserving its meaning. Never drop or weaken one.
- **Consequences** — only for non-obvious downstream effects; omit the heading otherwise.
- **Link line** — only when a Concept or document holds how the decision is applied; omit otherwise.
- **Scope sentence is mandatory** — states `@decisionScope` verbatim; entity-specific bounds (limits, windows, names) stay attributed to their entity even in a `wide` ADR.
- State the architectural decision in the title, not the problem.
- Explain why a decision is required in the body context.
- Include concrete abstraction, interface, event, field, service, topic, or component names only when they are part of the architectural contract.
- Keep implementation steps, method bodies, exact algorithms, and details that can change without changing the decision out of the ADR — link the doc that owns them.
- Include external protocol, API, or schema details only when the architecture depends on them.
- Prefer application abstractions over vendor-specific terminology when the vendor detail is not essential.

## Authoring the index row

An ADR that applies to exactly one building block is indexed in that block's `Architecture Decision Records` table inside `docs/building-blocks/{{slug}}.md` (or its repository's own ADR index when that repository documents itself). Every other ADR is indexed in `ARCHITECTURE.md`'s `Architecture Decision Records` table. Never both.

1. Row shape: `| [{{decisionTitle}}]({{pathToAdr}}) | {{summary}} | **Trigger:** {{triggerCondition}}. **Default:** {{default}} |` — `{{decisionTitle}}` identical to the ADR heading; `{{pathToAdr}}` relative to the indexing file.
2. Derive the Trigger condition: *Run `index-docs` skill for trigger-generation, scan/match, and row-sync; use **Generate trigger condition***, passing the written ADR as `{{recordContent}}`. `narrow` → trigger phrases name the entity; `wide` → name the class property and its domain synonyms, never one member alone.
3. Author the Summary yourself — 1-2 agent-optimized sentences stating the decision.
4. Author `default` yourself — one imperative sentence naming the choice to take when the design doesn't state one, bounded by `@decisionScope` (`narrow` names the entity). Never restate a rejected option as the default.
5. *Run `index-docs` skill for trigger-generation, scan/match, and row-sync; use **Ensure section exists*** for `Architecture Decision Records`, then its **Sync index row** with `{{rowMetadata}}` = `pathToAdr` (the previous path when renamed), `decisionTitle`, `summary`, and the `Trigger condition & Default` cell `**Trigger:** {{triggerCondition}}. **Default:** {{default}}` — never edit the table directly.

## Approval gate

- **Explicit direct request** that passes the gate — approval is given; write immediately.
- **Invoked by `grill-design`** — the user's answer is the approval. Write immediately; never offer, confirm, or defer, except an unsettled **Scope** question, returned to the caller. The user reviews the result in `git diff`.

Return the ADR path and the index row written.
