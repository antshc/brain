---
name: "csdroid-memory"
description: "csdroid agent decision memory using append-only JSONL."
---

## Store
The `decisions.jsonl` store file in the JSONL format

Resolve the path at runtime based on the detected OS:

- Linux/macOS: `$HOME/.copilot/memories/csdroid-memory/decisions.jsonl`
- Windows: `%USERPROFILE%\.copilot\memories\csdroid-memory\decisions.jsonl`

Initialize:
- `mkdir -p ~/.copilot/memories/csdroid-memory && touch ~/.copilot/memories/csdroid-memory/decisions.jsonl`

## Usage

1. Determine the operation type:

   **Before recording any decision** → Follow "Lookup workflow"  
   **No match found or new topic** → Follow "Add workflow"  
   **Existing decision changed** → Follow "Update workflow"  

2. Lookup workflow:
   - Read `decisions.jsonl`
   - Search all lines for entries where `topic`, `scope`, or `tags` overlap with the current decision
   - If a match is found and still applies, reuse it — stop here, do not duplicate

3. Add workflow:
   - Append exactly one JSON object line to `decisions.jsonl`
   - Set `confidence` per the **Confidence** rules
   - Do not record transient notes, temporary experiments, or routine steps

4. Update workflow:
   - Append a new JSON object line with `supersedes` set to the older entry's `id`
   - Never edit or delete old lines

## Record Schema

Required: `id`, `timestamp`, `agent`, `topic`, `decision`, `rationale`, `scope`, `tags[]`  
Optional: `supersedes`, `related[]`, `confidence` (`low` → `medium` → `high`)

## Confidence

- `low`: first reusable observation
- `medium`: independently confirmed across sessions/agents
- `high`: repeatedly validated and established

Increase only after independent successful validation. Never decrease.

## Hard Constraints

- Write only to the OS-resolved path defined in **Store**. Never use any other location.
- Do not record transient notes, temporary experiments, or routine execution steps.
- On every append, set `confidence` according to the **Confidence** rules above.
