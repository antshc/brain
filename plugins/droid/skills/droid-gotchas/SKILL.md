---
name: droid-gotchas
description: Agent gotchas — reads skill-owned GOTCHAS.md before implementation, then distills session friction into new or extended one-line directives and writes them back after feedback loops pass. Apply during the GOTCHAS step (read) and the UPDATE GOTCHAS step (write).
---

# Gotchas

Copy this checklist and check off items as you complete them:
```
Gotchas Progress:
- [ ] Step 1: Read sibling GOTCHAS.md in full (or use FALLBACK.md)
- [ ] Step 2: Apply every directive during implementation
- [ ] Step 3 (after feedback loops pass): Identify problem candidates from this invocation
- [ ] Step 4: Distill each kept candidate into a one-line directive; dedup/extend or append to sibling GOTCHAS.md
```

## Store

Gotchas live in the sibling `GOTCHAS.md` reference. `FALLBACK.md` supplies technology-agnostic behavior when that reference is absent.

## Read Workflow (mandatory before implementation)

- When sibling `GOTCHAS.md` is present, read it in full.
- When it is absent, report the missing reference, read sibling `FALLBACK.md`, and emit "Gotchas guidance: GOTCHAS.md missing; using FALLBACK.md."
- When the loaded reference is empty → "No gotchas recorded yet."
- Apply every directive found during implementation — do not contradict one without reporting the conflict.

**Emit**: "Gotchas loaded: [summary]" or "No gotchas recorded yet."

## Write Workflow (mandatory after feedback loops pass)

### Step 1: Identify problem candidates

List the files changed during this invocation. For each file or group of files, check whether a problem arose:
- A conflicting or ambiguous convention encountered
- A directory/filesystem access issue (permissions, missing paths, wrong cwd)
- A tool access issue (missing CLI, auth failure, unreachable service) — including any `STATUS: blocked` "Environment blockers" surfaced by `droid-feedback`
- Any other friction that cost time or blocked progress

**Discard** if it is: a one-off typo, a transient blip resolved on first retry, or a routine execution step. Only friction that would help a future run avoid the same mistake qualifies.

**Emit**: "Files changed: [list]. Problem candidates: [list or 'none — reason per file']."

### Step 2: Distill and write each candidate

For each kept candidate, distill it into a single reusable directive: `- <directive>`, optionally followed by a short workaround clause when it adds concrete guidance, e.g. `- <directive> — <what to do instead>.`

Before writing, scan the existing lines under `## Gotchas` for one covering the same rule or topic:
- **Match found** → edit that line in place to extend/refine it with the new nuance. Never duplicate it.
- **No match** → append the new line under `## Gotchas`.

**Zero candidates found** → skip silently, write nothing. When sibling `GOTCHAS.md` is absent, do not create it; report "Gotchas update: reference missing; no directives persisted."

**Emit**: "Gotchas updated: [count added/extended]" or "No gotchas to record."

## Hard Constraints

- Write only sibling `GOTCHAS.md` when it is present. Never derive, create, or search for another location.
- May edit an existing line only when it is clearly the same rule being refined; otherwise append-only. Never delete or contradict an unrelated existing line without reporting the conflict.
- Never fabricate a directive that isn't grounded in this invocation's actual friction.
- Apply every directive read during the Read Workflow before implementation.
