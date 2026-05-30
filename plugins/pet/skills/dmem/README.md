# dmem Skill

This skill provides toolless, local decision memory for durable decisions.

## What is included

- `SKILL.md` - skill instructions.
- `decisions.jsonl` - append-only decision store.

## How to use

1. Load/invoke the `dmem` skill.
2. Before making a decision, search `decisions.jsonl`.
3. Reuse a valid prior decision when applicable.
4. After a durable decision, append exactly one JSON object line to `decisions.jsonl`.
5. If replacing a prior decision, set `supersedes` to the old decision `id`.

## Usage example

Read existing entries first, then append one durable decision line.

```json
{"id":"dec-001","timestamp":"2026-05-30T10:00:00Z","agent":"csdroid","topic":"build-loop","decision":"Run targeted tests after each C# change set.","rationale":"Fast feedback with lower CI risk.","scope":"plugins/pet","tags":["testing","feedback-loop"],"confidence":"medium"}
{"id":"dec-002","timestamp":"2026-05-30T11:00:00Z","agent":"csdroid","topic":"build-loop","decision":"Run lsp + build first, then targeted tests.","rationale":"Build failures should fail fast before test selection.","scope":"plugins/pet","tags":["testing","build","feedback-loop"],"supersedes":"dec-001","confidence":"high"}
```

`dec-002` actualizes `dec-001` by superseding it. Old entries stay unchanged.

## JSONL contract

Required fields:
- `id`
- `timestamp` (ISO-8601)
- `agent`
- `topic`
- `decision`
- `rationale`
- `scope`
- `tags` (array of strings)

Optional fields:
- `supersedes`
- `related` (array of strings)
- `confidence` (`low` | `medium` | `high`)

### Skill Confidence Lifecycle

Skills use a three-level confidence model. Confidence only goes up, never down.

| Level | Meaning | When |
|-------|---------|------|
| `low` | First observation | Agent noticed a reusable pattern worth capturing |
| `medium` | Confirmed | Multiple agents or sessions independently observed the same pattern |
| `high` | Established | Consistently applied, well-tested, team-agreed |

Confidence bumps when an agent independently validates an existing skill - applies it in their work and finds it correct. If an agent reads a skill, uses the pattern, and it works, that's a confirmation worth bumping.

## Constraints

- Keep memory local to `plugins/pet/skills/dmem/decisions.jsonl`.
- Do not log transient notes, temporary experiments, or routine execution steps.
