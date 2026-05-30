---
name: "csdroid-memory"
description: "Copilot-user-local decision memory using append-only JSONL."
---

## Context

This skill is standalone and uses local files only.

Persistent memory path (fixed):

On Linux:

`$HOME/.copilot/memories/csdroid-memory/decisions.jsonl`

On Windows:

`%USERPROFILE%\.copilot\memories\csdroid-memory\decisions.jsonl`

## Agent Usage

1. Resolve OS path from `Context`.
2. Read `decisions.jsonl` if present.
3. Search by `topic`, `scope`, and `tags`.
4. Reuse a valid prior decision when applicable.
5. For a new durable decision, create parent directory if needed.
6. Append exactly one JSON object line.
7. If replacing an older decision, set `supersedes` to that decision `id`.
8. Do not log transient notes or routine execution steps.

## Data Contract

Each line in `decisions.jsonl` must be one valid JSON object.

Required fields:
- `id` (string)
- `timestamp` (ISO-8601 string)
- `agent` (string)
- `topic` (string)
- `decision` (string)
- `rationale` (string)
- `scope` (string)
- `tags` (string array)

Optional fields:
- `supersedes` (string)
- `related` (string array)
- `confidence` (`low` | `medium` | `high`)

## Confidence Lifecycle

Use a monotonic 3-level model:
- `low`: first reusable observation.
- `medium`: independently confirmed across sessions/agents.
- `high`: repeatedly validated and established.

Bump rule:
- Increase confidence only after independent successful validation in real work.
- Never decrease confidence. Only `low` -> `medium` -> `high`;

## Hard Constraints

- Keep durable memory only in the OS-specific decision store path defined in `Context`.
- Do not log transient notes, temporary experiments, or routine execution steps.
- On every append, set/update `confidence` using the **Confidence Lifecycle** rules.
