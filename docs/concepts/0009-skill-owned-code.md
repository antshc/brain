---
id: "0009"
title: Skill-Owned Code
status: Accepted
trigger: >-
  a skill needing a helper script, deciding where a skill's Python lives, adding a module to
  `tools/src/modules/`, adding a mapping to the pre-commit sync hook, two skills needing the same logic,
  placing a skill's tests, vendoring a library inside a skill, a skill importing another skill's code
summary: >-
  A skill owns the code it needs: its scripts and their tests live inside the skill folder, and
  `tools/src/modules/` is reserved for code genuinely shared across plugins, which the pre-commit hook syncs into
  each consumer. Logic needed by several skills in one plugin is owned by exactly one of them and reached by
  invoking that skill, never by importing across skill folders — so a plugin never carries two copies of the same
  implementation.
default: >-
  Put a skill's Python and its tests inside the skill folder; promote to `tools/src/modules/` only once a second
  plugin needs the same code.
owns:
  - "skill helper-code placement"
  - "skill test placement"
applies_to:
  - plugins/**
  - skills/**
  - tools/src/modules/**
  - .githooks/pre-commit
related: ["0001", "0005"]
---

# Skill-Owned Code

## Purpose

A skill that outgrows prose needs somewhere to put its scripts, and the two obvious answers — always vendor it
locally, or always centralise it — each produce a failure the other avoids: local copies drift, and premature
centralisation adds a sync mapping for code only one plugin will ever run.

## Rules

- A skill MAY own Python code inside its own folder.
- A skill that owns code MUST place that code's tests alongside it, inside the same skill folder.
- `tools/src/modules/<module>/` MUST be used only for code consumed by more than one plugin.
- A module under `tools/src/modules/` MUST have a mapping in `.githooks/pre-commit` for each destination that
  consumes it.
- The copy of a synced module inside `plugins/` MUST NOT be edited; the source under `tools/src/modules/` is
  authoritative.
- Logic needed by more than one skill in the same plugin MUST be owned by exactly one skill.
- A skill MUST NOT import code from a sibling skill's folder; it MUST invoke the owning skill instead.
- The same implementation MUST NOT exist in two skill folders.

## Design Guidance

Placement follows the number of consumers, not the size of the code:

| Consumers | Home | Sync |
|-----------|------|------|
| one skill | that skill's folder, tests beside it | none |
| several skills, one plugin | the one skill that owns the capability; siblings invoke it | none |
| more than one plugin | `tools/src/modules/<module>/`, tests under `tools/tests/` | pre-commit mapping per destination |

Cross-skill invocation uses the Resource Access Skill call style — run `` `/{{skillName}}` `` **{{ActionName}}** —
so the owning skill's documented actions stay the interface and its internals stay private
([0001](0001-resource-access-skill.md)).

`map-markdown-adf` is the reference shape: it owns the only ADF implementation in the `atl` plugin, in both
directions, with its tests beside it, and `fetch-page`, `fetch-work`, `publish-page`, and `publish-work` all reach
conversion by invoking the skill.

## Violation signals

- Two skill folders containing the same function or module name.
- An `import` or `sys.path` insertion that reaches into a sibling skill's directory.
- A `tools/src/modules/` entry with exactly one consumer.
- An edit to a file under `plugins/` that the pre-commit hook overwrites on the next commit.
- A vendored third-party library inside a skill with its own separate test suite and requirements file.
