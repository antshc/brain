---
name: csdroid-memory
description: C# decision memory — read, look up, add, update, and bump confidence on durable decisions stored in decisions.jsonl. Apply during DECISION CONTEXT and RECORD DECISIONS steps.
---

# Decision Memory

## Store

The `decisions.jsonl` store file in JSONL format, kept inside the harness root repository at `agent/decisions.jsonl`.

### Resolve repo

The store always lives at `$CSDROID_HARNESS_ROOT/agent/decisions.jsonl` — the harness root, never a worktree or nested `workspace/` repo. Load the environment before any read or write by sourcing the `csdroid-setup` skill's `load-env` script (see `csdroid-setup` → **Load environment** for the variables and layouts). It sources `.csdroid.env` if present, else falls back to inline detection.

Linux/macOS:
```bash
. <csdroid-setup-dir>/load-env.sh
STORE="$CSDROID_HARNESS_ROOT/agent/decisions.jsonl"
```

Windows (PowerShell):
```powershell
. <csdroid-setup-dir>/load-env.ps1
$STORE = Join-Path $Env:CSDROID_HARNESS_ROOT "agent\decisions.jsonl"
```

Initialize the `decisions.jsonl` store if missing:
- Linux/macOS: `mkdir -p "$CSDROID_HARNESS_ROOT/agent" && touch "$STORE"`
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

### 6. Commit & Push (once, after recording)

- Run **once** at the end of the RECORD DECISIONS step, after any Add / Update / Confidence Bump has written to the store.
- Operate in `$CSDROID_HARNESS_ROOT` (resolved in **Store**) — never the worktree.
- Stage `decisions.jsonl` on top of whatever is already staged, then commit and push. If nothing is staged, skip the commit (no empty commits).
- **Emit** the commit SHA, or "nothing to commit".

Linux/macOS:
```bash
git -C "$CSDROID_HARNESS_ROOT" add agent/decisions.jsonl
if git -C "$CSDROID_HARNESS_ROOT" diff --cached --quiet; then
  echo "nothing to commit"
else
  git -C "$CSDROID_HARNESS_ROOT" commit -m "chore(agent): update decision memory"
  git -C "$CSDROID_HARNESS_ROOT" rev-parse HEAD
  git -C "$CSDROID_HARNESS_ROOT" push
fi
```

Windows (PowerShell):
```powershell
git -C $Env:CSDROID_HARNESS_ROOT add agent/decisions.jsonl
git -C $Env:CSDROID_HARNESS_ROOT diff --cached --quiet
if ($LASTEXITCODE -eq 0) {
  Write-Output "nothing to commit"
} else {
  git -C $Env:CSDROID_HARNESS_ROOT commit -m "chore(agent): update decision memory"
  git -C $Env:CSDROID_HARNESS_ROOT rev-parse HEAD
  git -C $Env:CSDROID_HARNESS_ROOT push
}
```

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
- Commit & push runs **once** per RECORD DECISIONS step, always from `$CSDROID_HARNESS_ROOT` (never the worktree), and always pushes. Skip the commit only when nothing is staged.
