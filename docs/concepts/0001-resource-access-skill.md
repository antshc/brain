---
id: "0001"
title: Resource Access Skill
trigger: >-
  a skill encapsulating access to a ticket tracker, docs backend, or other external infrastructure, vendor
  commands or IDs appearing in a caller, swapping the backend behind an existing skill, index-table read/write
  ownership, a new external API reached from more than one place
summary: >-
  Access to one category of infrastructure is encapsulated behind a single skill's documented actions, so all
  vendor-specific knowledge — commands, IDs, formats — lives inside that skill and the backend can be replaced
  without touching a caller. Examples: `manage-backlog` (GitHub issues, swappable for Jira) and `manage-docs`
  (local markdown files).
default: >-
  Put vendor-specific knowledge for one infrastructure category inside a single skill and let callers reach it
  through that skill's documented actions.
owns:
  - "encapsulation of external infrastructure behind a skill"
applies_to:
  - plugins/**
  - skills/**
related: ["0003", "0009", "0010"]
---

# Resource Access Skill

## Purpose

A feature skill that needs infrastructure — a ticket tracker, a docs backend, an external API — risks coupling
its callers directly to a specific vendor or tool. A Resource Access Skill encapsulates access to one category
of infrastructure, similar to the iDesign Resource Access layer, so the backend can be replaced without
affecting its callers.

## Rules

- A Resource Access Skill MUST own all vendor-specific knowledge for its infrastructure category — commands,
  IDs, formats.
- Vendor-specific knowledge for that category MUST NOT appear in a caller.
- An action MUST document the values it reads and what it returns.
- An action's inputs MUST be read as `{{placeholder}}` variables already present in the caller's context, not
  declared as a formal call-site argument list.
- The skill's set of actions MUST stay stable when its backend is swapped.

## Design Guidance

Direct use of the underlying infrastructure tool is still allowed; what is barred is a caller inlining that
command *in place of* a skill reference it is otherwise making. The call style itself is owned by
[0010](0010-skill-composition.md).

Swapping a backend — GitHub → Jira, local files → a wiki — rewrites the skill's internals only. Callers and
their invocation style stay unchanged, which is the whole return on the encapsulation.

## Exceptions

- `trigger-indexer` writes directly to the file containing an index table (e.g. `ARCHITECTURE.md`), even when that file is otherwise owned by another Resource Access Skill (`manage-docs`). It is not itself an instance of this Concept — there is no swappable vendor backend involved, only index-table mechanics — so this carve-out does not weaken the Concept's ownership boundary for any other file content.
