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

Cross-skill invocation uses the call style owned by [0010](0010-skill-composition.md) — run `` `/{{skillName}}` `` **{{ActionName}}** —
so the owning skill's documented actions stay the interface and its internals stay private.

A capability with two directions — a conversion to and from some format, an encode paired with a decode — counts
as one consumer set, not two: both directions live in the single skill that owns the capability, and every
sibling reaches either by invoking it.

## Violation signals

- Two skill folders containing the same function or module name.
- An `import` or `sys.path` insertion that reaches into a sibling skill's directory.
- A `tools/src/modules/` entry with exactly one consumer.
- An edit to a file under `plugins/` that the pre-commit hook overwrites on the next commit.
- A vendored third-party library inside a skill with its own separate test suite and requirements file.
