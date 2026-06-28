---
name: csdroid-memory
description: C# decision memory — read, look up, add, update, and bump confidence on durable decisions stored in decisions.jsonl. Apply during DECISION CONTEXT and RECORD DECISIONS steps.
---

# Decision Memory

## Store

The `decisions.jsonl` store file in JSONL format, kept inside the source repo at `agent/decisions.jsonl`.

### Resolve repo

Resolve which repo holds the store **before** any read or write. The current repository is the harness root; the actual source code may live in a separate repo under `workspace/`.

Linux/macOS:
```bash
harness_root=$(git rev-parse --show-toplevel)
src_git=$(find "$harness_root/workspace" -maxdepth 2 -name .git -type d 2>/dev/null | head -n1)
if [ -n "$src_git" ]; then
  SOURCE_REPO=$(dirname "$src_git")
else
  SOURCE_REPO=$harness_root
fi
STORE="$SOURCE_REPO/agent/decisions.jsonl"
```

Windows (PowerShell):
```powershell
$harnessRoot = git rev-parse --show-toplevel
$srcGit = Get-ChildItem -Path "$harnessRoot\workspace" -Filter .git -Recurse -Depth 1 -Directory -ErrorAction SilentlyContinue | Select-Object -First 1
if ($srcGit) { $SourceRepo = $srcGit.Parent.FullName } else { $SourceRepo = $harnessRoot }
$STORE = Join-Path $SourceRepo "agent\decisions.jsonl"
```

- If a `.git` directory is found under `workspace/` (including one subfolder level), use that source repo.
- Otherwise, fall back to the current (harness) repo.

Initialize the `decisions.jsonl` store if missing:
- Linux/macOS: `mkdir -p "$SOURCE_REPO/agent" && touch "$STORE"`
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
