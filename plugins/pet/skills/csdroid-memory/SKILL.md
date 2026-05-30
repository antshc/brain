---
name: "csdroid-memory"
description: "Toolless, skill-local decision memory using append-only JSONL."
domain: "decision-governance"
confidence: "high"
source: "manual"
tools:
---

## Context

This skill is standalone and uses local files only.

Persistent memory path (fixed):

`<skill-dir>/decisions.jsonl`

In this skill:

`plugins/pet/skills/csdroid-memory/decisions.jsonl`

## Required Workflow

Before making a new durable decision:
1. Read `plugins/pet/skills/csdroid-memory/decisions.jsonl` if it exists.
2. Search related entries by topic, scope, and tags.
3. Reuse valid prior decisions when applicable.

After making a new durable decision:
1. Append exactly one JSON object line to `plugins/pet/skills/csdroid-memory/decisions.jsonl`.
2. If it supersedes an earlier entry, set `supersedes` to the previous `id`.
3. Keep entries durable and reusable (no transient notes).

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

- Keep memory local to `plugins/pet/skills/csdroid-memory/decisions.jsonl`.
- Do not log transient notes, temporary experiments, or routine execution steps.
