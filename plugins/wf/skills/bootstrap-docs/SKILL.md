---
name: bootstrap-docs
description: Own the existence-and-creation mechanics for ARCHITECTURE.md and CONTEXT.md — mandatorily create either the moment it's missing, and insert a caller-supplied skeleton section into ARCHITECTURE.md on request. Owns no templates, no prose, no directory creation for docs/adr, docs/concepts, or docs/services (each owned by the skill that writes into it), and no "when is it appropriate to create" criteria — that stays with the owning skill. Invoked only when a caller's own existence check finds ARCHITECTURE.md or CONTEXT.md missing, or when a caller needs a section inserted.
---

# Bootstrap Docs

Own the *mechanics* of `ARCHITECTURE.md`/`CONTEXT.md` existence, creation, and section-skeleton
insertion. Directory creation for `docs/adr/`, `docs/concepts/`, `docs/services/` belongs to the
skill that writes into that directory (`record-adr`, `record-concept`, `record-service`). Every
template, every piece of prose, and every "is now the right time?" judgment belongs to the skill
that owns that content — `record-term` (`CONTEXT-FORMAT.md`), `index-docs`
(`ARCHITECTURE-FORMAT.md`).

## When to call this skill

Cheap to check, expensive to load in full. Callers do a **plain existence check** for
`ARCHITECTURE.md` and `CONTEXT.md` themselves first (a file-existence check, not a full read, and
not this skill). Invoke `bootstrap-docs` only when that check finds one of them missing, or when a
directory's existence needs reporting, or a section needs to be inserted — never "just in case"
every session. The mandatory-creation guarantee only needs to fire once per repo.

## Mandatory creation

If `ARCHITECTURE.md` and/or `CONTEXT.md` don't exist, create them **immediately** — don't wait for
a term, structural rule, ADR, Concept, or service to be ready to capture.

- **`ARCHITECTURE.md`** is the index hub every other document links into. Fill in only the
  required sections (`# {{systemName}} Overview`, `## Context`) from what's already known about
  the codebase, using [ARCHITECTURE-FORMAT.md](../index-docs/ARCHITECTURE-FORMAT.md) (`index-docs`'
  template). Leave the optional sections (`Building blocks`, `Deployment View`, the
  `Architecture Decision Records` / `Crosscutting Concepts` indexes) out until there's content for
  them — `index-docs` adds those via *Ensure section exists* below.
- **`CONTEXT.md`** is the glossary every other document assumes as shared vocabulary. Create it
  with its `# {{contextName}}` heading and an empty `## Language` section — leave individual terms
  out until `record-term` captures the first one, using
  [CONTEXT-FORMAT.md](../record-term/CONTEXT-FORMAT.md) (`record-term`'s template).

These are the **two non-lazy cases**. Every other document (`docs/adr/`, `docs/concepts/`,
`docs/services/`) stays genuinely lazy — and each is created directly by the skill that writes
into it, not by `bootstrap-docs`.

## Ensure section exists

Inputs: `{{sectionAnchor}}` (e.g. `## Architecture Decision Records`, `## Crosscutting Concepts`,
the `Services` table under `## Building blocks`), `{{skeletonContent}}` (caller-supplied).

If the section is missing from `ARCHITECTURE.md`, insert the skeleton at the appropriate place. If
it already exists, do nothing. This mechanic is content-agnostic — the skeleton always comes from
the caller, mirroring `index-docs`' own "never assume a schema" stance for the tables it scans and
syncs. `bootstrap-docs` doesn't know what an ADR or Concept table looks like; it only inserts what
it's given.

