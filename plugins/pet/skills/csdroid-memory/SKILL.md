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

## Required Workflow

Before making a new durable decision:
1. Resolve the decision store path from `Context` for the current OS.
2. Read the decision store file if it exists.
3. Search related entries by topic, scope, and tags.
4. Reuse valid prior decisions when applicable.

After making a new durable decision:
1. Create the decision store parent directory if it does not exist.
2. Append exactly one JSON object line to the decision store file.
3. If it supersedes an earlier entry, set `supersedes` to the previous `id`.
4. Keep entries durable and reusable (no transient notes).

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

## Hard Constraints

- Keep durable memory only in the OS-specific decision store path defined in `Context`.
- Do not log transient notes, temporary experiments, or routine execution steps.
