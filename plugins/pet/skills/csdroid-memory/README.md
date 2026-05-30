# csdroid-memory Skill

This skill provides toolless, durable decision memory for Copilot agents.
This repository plugin is an installation source. Durable memory is stored outside the repo.

## Decision store

- Canonical path: `$HOME/.copilot/memories/csdroid-memory/decisions.jsonl`
- Windows: `C:\Users\antsh\.copilot\memories\csdroid-memory\decisions.jsonl`
- Linux: `/home/<user>/.copilot/memories/csdroid-memory/decisions.jsonl`

## What is included

- `SKILL.md` - skill instructions.
- Usage examples in this README - reference records, not durable source of truth.

## How to use

1. Load/invoke the `csdroid-memory` skill.
2. Before making a decision, search `$HOME/.copilot/memories/csdroid-memory/decisions.jsonl`.
3. Reuse a valid prior decision when applicable.
4. If needed, create `$HOME/.copilot/memories/csdroid-memory`.
5. After a durable decision, append exactly one JSON object line to `$HOME/.copilot/memories/csdroid-memory/decisions.jsonl`.
6. If replacing a prior decision, set `supersedes` to the old decision `id`.

## Usage example

Read existing entries first, then append one durable decision line.

```json
{"id":"dec-100","timestamp":"2026-05-30T09:30:00Z","agent":"csdroid","topic":"testing-order","decision":"Run lsp diagnostics before build and tests.","rationale":"Surface syntax/type issues first for faster iteration.","scope":"plugins/pet","tags":["quality","feedback-loop"],"confidence":"medium"}
```

`dec-102` actualizes `dec-101` by superseding it. Old entries stay unchanged.

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

## Constraints

- Keep durable memory in `$HOME/.copilot/memories/csdroid-memory/decisions.jsonl`.
- Do not log transient notes, temporary experiments, or routine execution steps.
