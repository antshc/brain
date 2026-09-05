---
name: record-concept
description: Capture one structural, reusable, backbone-defining architectural rule as a Crosscutting Concept the moment it crystallises. Owns CONCEPT-FORMAT.md, the "when to write a Concept" gate, numbering, and the choice between extending an existing record and creating a new one. Called directly by explicit user request, or invoked by grill-design.
---

# Record Concept

Capture **one backbone rule** — the top-level decomposition, or a pattern every feature of a given kind must follow — into `docs/concepts/` the moment it crystallises. Use [CONCEPT-FORMAT.md](./CONCEPT-FORMAT.md) for the template.

## Where the rule belongs

Runs first, before the Concept gate. Most rules that reach this skill belong somewhere else, and a rule filed in the wrong home is read at the wrong moment — a wording rule buried in a Concept fires during design and stays silent while the file is being written.

Split on **when the rule is needed**:

| The rule answers | Home | Written by |
|---|---|---|
| which building block to reach for, what shape the system takes | Concept, `docs/concepts/` | this skill — continue below |
| which option was chosen here, and why the others were not | ADR, `docs/adr/` | `/record-adr` |
| how to word, name, format, or lay out the file being written | an instructions file under `.github/instructions/`, scoped by `applyTo` | edit that file directly |
| what a contested term means | glossary, `CONTEXT.md` | `/record-term` |
| which command, path, or version this one repo uses | the repo's own convention file or memory | edit that file directly |

Two tests settle most cases:

- **Would the sentence still be true in another repo, with different tooling?** Yes, and it constrains what gets built → a record. No, it names one project's command, path, or setting → a convention file.
- **Is it needed while deciding, or while typing?** Deciding → a record. Typing → write-time guidance, which loads automatically through `applyTo` at the moment it applies.

A rule can be genuinely structural *and* have a write-time counterpart. Record the rule once as a Concept, and let the instructions file carry only the wording, naming, or layout that follows from it.

## When to write a Concept

Write one (instead of, or in addition to, an ADR) only when all three are true:

1. **Structural** — it shapes the top-level decomposition or mandates a pattern, rather than settling one local question.
2. **Reusable** — future features of the same kind are expected to follow it every time.
3. **Backbone-defining** — it is one of the foundational decisions that hold the architecture together and constrain everything built on top of it.

If any of the three is missing, skip the Concept — route it by *Where the rule belongs* above; an ADR (see `record-adr`) is the usual next fit.

## Extend or create

<!-- Deliberately duplicated in record-adr and record-concept: each skill must be self-contained. Do not factor out. -->

Runs before any write. A near-duplicate record is worse than a longer one: it splits authority over a decision area, and the `owns` key can then name only one of them.

1. Run `/index-docs`' skill **Scan and match** over the `Crosscutting Concepts` and `Architecture Decision Records` tables with this rule's surface — its terms and the paths it governs.
2. A matched record whose scope or `owns` already covers this decision area → **extend it**: add the `Rules` line or guidance to the body, and sharpen `default`, `owns`, `trigger`, or `applies_to` to cover the new case. Resync its row via **Sync index row**. Stop here.
3. No match covers the area → **create** a new Concept. Its `owns` phrases must not collide with any existing record's — a phrase belongs to exactly one record.

## Lazy creation

Create `docs/concepts/` when the first Concept is ready — not before; do nothing if it exists.

## Next record number

<!-- Deliberately duplicated in record-adr and record-concept: each skill must be self-contained. Do not factor out. -->

Highest four-digit `NNNN` filename prefix in `docs/concepts/`, plus 1, zero-padded to four digits. An empty or absent directory returns `0001`.

## Frontmatter is mandatory

Every Concept opens with the YAML frontmatter block defined in [CONCEPT-FORMAT.md](./CONCEPT-FORMAT.md#frontmatter). It is the machine-readable contract for the record, and the source of truth for its `ARCHITECTURE.md` index row.

1. Author `id`, `title`, `trigger`, `summary`, `applies_to` before writing the body — they force the "does this apply to me?" decision up front.
2. Derive `trigger` with `/index-docs`' skill **Generate trigger condition**, then write the returned value into frontmatter — not straight into the table.
3. `related` is bidirectional: adding `related: ["0009"]` here means adding this record's id to `0009`'s `related` in the same change. A one-directional link is lost to any reader arriving from the other side.
4. Superseding or retiring a Concept applies the marker to its index row via `/index-docs`' skill **Sync index row**; the record itself carries no status field.

## Body

Write `Purpose`, `Rules`, and `Design Guidance` per [CONCEPT-FORMAT.md](./CONCEPT-FORMAT.md#section-skeleton). `Design Guidance` states the pattern in general terms and stands on its own — a reader applies it without opening any file it points at ([Design Guidance is self-contained](./CONCEPT-FORMAT.md#design-guidance-is-self-contained)).

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

<!-- Deliberately duplicated in record-adr and record-concept: each skill must be self-contained. Do not factor out. -->

- **Explicit direct request** ("record a Concept for X") — approval is already given; draft and write immediately.
- **Invoked by an interview-style caller** (`grill-design`) — the caller already owns the decision to record, whether it came from the user's answer or from the caller's own assumption. Write immediately; never stop to offer, confirm, or defer. The user reviews the result in `git diff`.

