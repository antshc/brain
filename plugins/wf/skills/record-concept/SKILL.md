---
name: record-concept
description: Persist a consequential shared domain behavior, structural implementation pattern, or operational policy as a Crosscutting Concept. Own frontmatter, numbering, extend-or-create, file writing, and index synchronization; use doc-concept for the body. Called directly, by define-concept, or by grill-design.
---

# Record Concept

Capture **one shared approach** governing multiple building blocks into `docs/concepts/` the moment it crystallises. Use [CONCEPT-FORMAT.md](./CONCEPT-FORMAT.md) for the frontmatter; Run `/doc-concept` skill for its body unless the caller supplied a rendered body from that skill.

## Where the rule belongs

Runs first, before the Concept gate. Most rules that reach this skill belong somewhere else, and a rule filed in the wrong home is read at the wrong moment — a wording rule buried in a Concept fires during design and stays silent while the file is being written.

Split on **when the rule is needed**:

| The rule answers | Home | Written by |
|---|---|---|
| how shared domain behavior, implementation, or operational policy governs several building blocks | Concept, `docs/concepts/` | this skill — continue below |
| which option was chosen here, and why the others were not | feature design or standalone ADR | session ledger / `/to-zdesign`; `/draft-decision` on explicit ADR request |
| how to word, name, format, or lay out the file being written | an instructions file under `.github/instructions/`, scoped by `applyTo` | edit that file directly |
| what a contested term means | glossary, `CONTEXT.md` | `/record-term` |
| which command, path, or version this one repo uses | the repo's own convention file or memory | edit that file directly |

Two tests settle most cases:

- **Does it state a transferable approach?** A shared rule may cite this repo's implementation as evidence, but must explain the approach without that example. A command, path, or setting alone → a convention file.
- **Is it needed while deciding, or while typing?** Deciding → a record. Typing → write-time guidance, which loads automatically through `applyTo` at the moment it applies.

A rule can be shared across the system *and* have a write-time counterpart. Record the rule once as a Concept, and let the instructions file carry only the wording, naming, or layout that follows from it.

## When to write a Concept

Write one only when all three are true:

1. **Crosscutting** — a domain behavior, structural pattern, or operational policy applies to multiple building blocks or workflows, not just one feature.
2. **Reusable** — other implementations in its scope should follow the same approach.
3. **Consequential** — it guides a meaningful design or operational choice and can be checked against behavior, code, tests, or configuration.

If any of the three is missing, skip the Concept — route it by *Where the rule belongs* above. Do not draft an ADR as a side effect.

## Extend or create

Runs before any write. A near-duplicate record is worse than a longer one: it splits authority over a decision area, and the `owns` key can then name only one of them.

1. Run `/index-docs`' skill **Scan and match** over the `Crosscutting Concepts` table with this rule's surface — its terms and the paths it governs.
2. A matched record whose scope or `owns` already covers this decision area → **extend it**: use `/doc-concept` for a body change and sharpen `default`, `owns`, `trigger`, or `applies_to` when needed. Resync its row via **Sync index row**. Stop here.
3. No match covers the area → **create** a new Concept. Its `owns` phrases must not collide with any existing record's — a phrase belongs to exactly one record.

## Lazy creation

Create `docs/concepts/` when the first Concept is ready — not before; do nothing if it exists.

## Next record number

Highest four-digit `NNNN` filename prefix in `docs/concepts/`, plus 1, zero-padded to four digits. An empty or absent directory returns `0001`.

## Frontmatter is mandatory

Every Concept opens with the YAML frontmatter block defined in [CONCEPT-FORMAT.md](./CONCEPT-FORMAT.md#frontmatter). It is the machine-readable contract for the record, and the source of truth for its `ARCHITECTURE.md` index row.

1. Author `id`, `title`, `trigger`, `summary`, `applies_to` before writing the body — they force the "does this apply to me?" decision up front.
2. Derive `trigger` with `/index-docs`' skill **Generate trigger condition**, then write the returned value into frontmatter — not straight into the table.
3. `related` is bidirectional: adding `related: ["0009"]` here means adding this record's id to `0009`'s `related` in the same change. A one-directional link is lost to any reader arriving from the other side.
4. Superseding or retiring a Concept applies the marker to its index row via `/index-docs`' skill **Sync index row**; the record itself carries no status field.

## Body

Run `/doc-concept` skill to render or revise the body, or accept a body already rendered by it from `/define-concept`. Preserve its required headings and applicable optional sections. This skill alone combines the body with frontmatter and writes the record.

## Keeping the index in sync

When a Concept is added, superseded, or retired, Run `/index-docs`' skill **Ensure section exists** for `Crosscutting Concepts`, then its **Sync index row** in the same change — never edit the table in `ARCHITECTURE.md` directly.

Pass `{{rowMetadata}}` **from the record's frontmatter**, so the table stays a projection of the files rather than a hand-maintained duplicate:

| Column | Frontmatter key |
|--------|-----------------|
| `#` | `id` (linked to the record path) |
| `Concept` | `title` |
| `Trigger condition` | `trigger` |
| `Summary` | `summary` |

If a row and its record disagree, the frontmatter wins — resync the row, don't edit the file to match the table.

## Approval gate

- **Explicit direct request** ("record a Concept for X") — approval is already given; draft and write immediately.
- **Invoked by `define-concept`** — its questioning confirmation settled the concept. Write immediately without a second prompt.
- **Invoked by `grill-design`** — the caller already owns the decision to record, whether it came from the user's answer or from the caller's own assumption. Write immediately; never stop to offer, confirm, or defer. The user reviews the result in `git diff`.
