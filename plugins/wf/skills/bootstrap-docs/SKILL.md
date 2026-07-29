---
name: bootstrap-docs
description: Own the existence-and-creation mechanics for the domain-model documents — mandatorily create ARCHITECTURE.md and CONTEXT.md the moment either is missing, report (never create) whether docs/adr/, docs/concepts/, docs/services/ exist, and insert a skeleton section into ARCHITECTURE.md on request. Hosts ARCHITECTURE-FORMAT.md and CONTEXT-FORMAT.md — the two mandatory docs' templates — but owns only their top-level file skeleton; the index-table shapes and term-writing rules inside them stay owned by index-docs/record-term. Owns no templates, prose, or "when is it appropriate to create" criteria for the lazy docs — that stays with the owning skill. Invoked only when a caller's own existence check finds something missing.
---

# Bootstrap Docs

Own the *mechanics* of document/directory existence and creation, and host
[ARCHITECTURE-FORMAT.md](./ARCHITECTURE-FORMAT.md) / [CONTEXT-FORMAT.md](./CONTEXT-FORMAT.md) — the
templates for the two mandatory docs. Owning the file is not owning all of its content: this skill
only owns each template's top-level file skeleton (the mandatory headings created at bootstrap
time); the judgment call of *when* it's appropriate to write index rows or terms, and the shape of
those sections, belongs to the skill that owns that content (`record-term`, `index-docs`,
`record-adr`, `record-concept`, `record-service`).

## When to call this skill

Cheap to check, expensive to load in full. Callers do a **plain existence check** for
`ARCHITECTURE.md` and `CONTEXT.md` themselves first (a file-existence check, not a full read, and
not this skill). Invoke `bootstrap-docs` only when that check finds one of them missing, or when a
directory's existence needs reporting, or a section needs to be inserted — never "just in case"
every session. The mandatory-creation guarantee only needs to fire once per repo.

## Mandatory creation — ARCHITECTURE.md and CONTEXT.md

If `ARCHITECTURE.md` and/or `CONTEXT.md` don't exist, create them **immediately** — don't wait for
a term, structural rule, ADR, Concept, or service to be ready to capture.

- **`ARCHITECTURE.md`** is the index hub every other document links into. Fill in only the
  required sections (`# {{systemName}} Overview`, `## Context`) from what's already known about
  the codebase. Leave the optional sections (`Building blocks`, `Deployment View`, the
  `Architecture Decision Records` / `Crosscutting Concepts` indexes) out until there's content for
  them — `index-docs` adds those via *Ensure section exists* below.
- **`CONTEXT.md`** is the glossary every other document assumes as shared vocabulary. Create it
  with its `# {{contextName}}` heading and an empty `## Language` section — leave individual terms
  out until `record-term` captures the first one.

These are the **two non-lazy cases**. Every other document (`docs/adr/`, `docs/concepts/`,
`docs/services/`) stays genuinely lazy.

## Existence reporting — everything else

For `docs/adr/`, `docs/concepts/`, `docs/services/`: report present/absent only. Never create
these — return the answer to the caller (the owning skill), which decides whether *now* is the
right time to create, per its own trigger ("first ADR ready," "non-trivial service").

## Ensure section exists

Inputs: `{{sectionAnchor}}` (e.g. `## Architecture Decision Records`, `## Crosscutting Concepts`,
the `Services` table under `## Building blocks`), `{{skeletonContent}}` (caller-supplied).

If the section is missing from `ARCHITECTURE.md`, insert the skeleton at the appropriate place. If
it already exists, do nothing. This mechanic is content-agnostic — the skeleton always comes from
the caller, mirroring `index-docs`' own "never assume a schema" stance for the tables it scans and
syncs. `bootstrap-docs` doesn't know what an ADR or Concept table looks like; it only inserts what
it's given.

## Ownership

- Owns: `ARCHITECTURE.md`/`CONTEXT.md`'s mandatory creation, existence reporting for the other
  lazy docs, inserting a caller-supplied section skeleton, and the top-level file skeleton inside
  the hosted `ARCHITECTURE-FORMAT.md`/`CONTEXT-FORMAT.md` templates.
- Does **not** own: the Services/ADR/Concepts index-table shapes inside `ARCHITECTURE-FORMAT.md`
  (`index-docs`' job), the term-writing rules inside `CONTEXT-FORMAT.md` (`record-term`'s
  job), prose content, the "when is it appropriate to create" criteria for the lazy docs, or
  index-row content/sync (`record-adr`/`record-concept`/`record-service`/`index-docs`' job).
- Called by `grill-design` (or another grilling/modeling skill) only when its own existence check
  finds `ARCHITECTURE.md` or `CONTEXT.md` missing — never by `manage-backlog` or a separate setup
  skill.
