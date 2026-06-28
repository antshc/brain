---
name: csdroid-memory
description: C# decision memory — read, look up, add, update, and bump confidence on durable decisions stored in decisions.jsonl. Apply during DECISION CONTEXT and RECORD DECISIONS steps.
---

# Decision Memory

## Store

The `decisions.jsonl` store file in JSONL format, kept inside the harness root repository at `agent/decisions.jsonl`.

### Resolve repo

The store always lives in the **harness root repository** — the outermost repo, never a worktree or a nested `workspace/` source repo. Two layouts are supported:

- **Harness only** — no source repo under `workspace/`; the harness repo is the source repo.
- **Harness + workspace** — the source code lives in a separate repo under `workspace/`; the harness still owns the store.

This skill runs from inside a worktree, so resolving the harness root takes two steps that work for both layouts: find the **main** working tree of the current repo (worktrees share it via `--git-common-dir`), then climb out to the outermost enclosing repo. Resolve it **before** any read or write.

Linux/macOS:
```bash
HARNESS_ROOT=$(cd "$(git rev-parse --git-common-dir)/.." && pwd)
while parent=$(cd "$HARNESS_ROOT/.." && git rev-parse --show-toplevel 2>/dev/null); do
  HARNESS_ROOT=$parent
done
STORE="$HARNESS_ROOT/agent/decisions.jsonl"
```

Windows (PowerShell):
```powershell
$HarnessRoot = (Resolve-Path (Join-Path (git rev-parse --git-common-dir) "..")).Path
while ($parent = (git -C (Join-Path $HarnessRoot "..") rev-parse --show-toplevel 2>$null)) { $HarnessRoot = $parent }
$STORE = Join-Path $HarnessRoot "agent\decisions.jsonl"
```

Initialize the `decisions.jsonl` store if missing:
- Linux/macOS: `mkdir -p "$HARNESS_ROOT/agent" && touch "$STORE"`
- Windows (PowerShell): `md -Force (Split-Path $STORE) | Out-Null; if(!(Test-Path $STORE)){New-Item $STORE | Out-Null}`

## Usage

### 1. Read Workflow (mandatory before implementation)

- Read `decisions.jsonl` in full from the repo-resolved store path
- Filter all entries where `scope`, `tags`, or `topic` overlap with the current task
- **Emit** the matching decision IDs: "Applying decisions: [dec-XXX, dec-YYY]" or "No prior decisions apply"
- If the file doesn't exist or is empty → "No prior decisions"
- Apply matching decisions during implementation — do not contradict them without superseding first

### 2. Lookup Workflow (before recording)

- Search all lines for entries where `topic`, `scope`, or `tags` overlap with the candidate decision
- If a match is found and still applies → reuse it, do not duplicate
- If the existing decision needs updating → follow Update workflow

### 3. Add Workflow

- Append exactly one JSON object line to `decisions.jsonl`
- Set `confidence` per the **Confidence** rules
- Do not record transient notes, temporary experiments, or routine steps

### 4. Update Workflow

- Append a new JSON object line with `supersedes` set to the older entry's `id`
- Never edit or delete old lines when the decision content changes (a confidence bump is the only exception — see step 5)

### 5. Confidence Bump (after successful reuse)

- If you applied an existing decision during implementation AND feedback loops passed → check its current confidence
- If currently `low` → edit that record's line in place: change only `confidence` from `low` to `medium` and refresh its `timestamp`. Do NOT append a new record and do NOT set `supersedes`.
- If currently `medium` or `high` → no action needed

## Record Schema

Required: `id`, `timestamp`, `agent`, `topic`, `decision`, `rationale`, `scope`, `tags[]`
Optional: `supersedes`, `related[]`, `confidence` (`low` → `medium` → `high`)

## Confidence

- `low`: first reusable observation
- `medium`: independently confirmed across sessions/agents
- `high`: repeatedly validated and established

Increase only after independent successful validation. Never decrease.

## Hard Constraints

- Write only to the repo-resolved store path defined in **Store**. Never use any other location.
- Do not record transient notes, temporary experiments, or routine execution steps.
- On every append, set `confidence` according to the **Confidence** rules above.
- A confidence bump is the only edit-in-place operation: it changes `confidence` (and `timestamp`) on the existing line. All other changes must append a superseding record — never edit or delete old lines.
- **Must-emit after reading**: emit the list of decision IDs being applied (or "none"). This is observable output — do not skip silently.
- **Must-emit after recording**: emit the new decision ID (or "No new decisions to record"). This is observable output — do not skip silently.
