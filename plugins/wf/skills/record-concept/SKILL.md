---
name: record-concept
description: Persist a consequential shared business process, structural implementation pattern, or operational policy as a Crosscutting Concept. Own record identity, extend-or-create, file writing, and index synchronization; use doc-concept for the body. Called directly, by define-concept, or by grill-design.
---

# Record Concept

Capture **one shared approach** governing multiple building blocks into `docs/concepts/` the moment it crystallises. Run `/doc-concept` skill for its body unless the caller supplied a rendered body from that skill; `/doc-concept` owns all body templates and writing rules.

## Where the rule belongs

Runs first, before the Concept gate. Most rules that reach this skill belong somewhere else, and a rule filed in the wrong home is read at the wrong moment — a wording rule buried in a Concept fires during design and stays silent while the file is being written.

Split on **when the rule is needed**:

| The rule answers | Home | Written by |
|---|---|---|
| how a shared business process, implementation, or operational policy governs several building blocks | Concept, `docs/concepts/` | this skill — continue below |
| which option was chosen here, and why the others were not | feature design or standalone ADR | session ledger / `/to-zdesign`; |
| how to word, name, format, or lay out the file being written | an instructions file under `.github/instructions/`, scoped by `applyTo` | edit that file directly |
| what a contested term means | glossary, `CONTEXT.md` | `/record-term` |
| which command, path, or version this one repo uses | the repo's own convention file or memory | edit that file directly |

Two tests settle most cases:

- **Does it state a transferable approach?** A shared rule may cite this repo's implementation as evidence, but must explain the approach without that example. A command, path, or setting alone → a convention file.
- **Is it needed while deciding, or while typing?** Deciding → a record. Typing → write-time guidance, which loads automatically through `applyTo` at the moment it applies.

A rule can be shared across the system *and* have a write-time counterpart. Record the rule once as a Concept, and let the instructions file carry only the wording, naming, or layout that follows from it.

## When to write a Concept

Write one only when all three are true:

1. **Crosscutting** — a business process, structural pattern, or operational policy applies to multiple building blocks or workflows, not just one feature.
2. **Reusable** — other implementations in its scope should follow the same approach.
3. **Consequential** — it guides a meaningful design or operational choice and can be checked against behavior, code, tests, or configuration.

If any of the three is missing, skip the Concept — route it by *Where the rule belongs* above.

## Extend or create

Runs before any write. A near-duplicate record is worse than a longer one: it splits a decision area across two files instead of sharpening one.

1. Run `/index-docs`' skill **Scan and match** over the `Crosscutting Concepts` table with this rule's surface — its terms and the paths it governs.
2. A matched record's scope already covers this decision area → **extend it**: use `/doc-concept` for a body change and sharpen its `default` or `trigger` when needed. Resync its row via **Sync index row**. Stop here.
3. No match covers the area → **create** a new Concept.

## Lazy creation

Create `docs/concepts/` when the first Concept is ready — not before; do nothing if it exists.

## Record identity

A record is named `docs/concepts/{{kind}}-{{slug}}.md`. `{{kind}}` is the kind of the `/doc-concept` template the body came from — `dom`, `str`, or `ops` — so the directory listing groups the families; `{{slug}}` is the title in kebab-case. For `dom`, the title is the Business Capability the page covers, so the slug is that capability in kebab-case. Sharpen the slug when a name is already taken; the identity carries no counter, so nothing has to be renumbered.

A record carries no frontmatter — it opens directly with `# {{conceptTitle}}`.

## Body

Run `/doc-concept` skill to render or revise the body, or accept a body already rendered by it from `/define-concept`. Preserve its required headings and applicable optional sections. This skill writes the body and authors the index row in the same change.

## Authoring the index row

The `ARCHITECTURE.md` row is authored directly by this skill, not projected from the record — the record carries nothing to project.

1. `title` is the `# ` heading text, used as the record-name column linked to the record path.
2. Derive the Trigger condition with `/index-docs`' skill **Generate trigger condition**, passing the rendered body as `{{recordContent}}`.
3. Author `default` yourself — one sentence naming the choice to take when the design doesn't state one. A caller-supplied, user-confirmed `default` (from `/define-concept`) is used verbatim.
4. Run `/index-docs`' skill **Ensure section exists** for `Crosscutting Concepts`, then its **Sync index row** with `{{rowMetadata}}` = `title`, `triggerCondition`, `default` — never edit the table in `ARCHITECTURE.md` directly.

Superseding or retiring a Concept applies the marker to its index row via the same **Sync index row** call; the record itself carries no status field.

## Approval gate

- **Explicit direct request** ("record a Concept for X") — approval is already given; draft and write immediately.
- **Invoked by `define-concept`** — its questioning confirmation settled the concept. Write immediately without a second prompt.
- **Invoked by `grill-design`** — the caller already owns the decision to record, whether it came from the user's answer or from the caller's own assumption. Write immediately; never stop to offer, confirm, or defer. The user reviews the result in `git diff`.
