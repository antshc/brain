---
name: crew-gotchas
description: "Read and update a repository-local gotchas-memory GOTCHAS.md with reusable directives discovered during implementation or review. Use when Codey or Chorey enters its GOTCHAS or UPDATE GOTCHAS step."
---

# Gotchas

Gotchas live in the `GOTCHAS_PATH` resolved by the calling agent through `/gotchas-memory` (auto-created there if missing). Write only that path — never derive or search for another location.

## Read Workflow (mandatory before the agent's main work)

Read `GOTCHAS_PATH` in full when provided. Unresolved or empty → "No gotchas recorded yet."

Apply every directive found during the agent's work — never contradict one without reporting the conflict.

**Emit**: "Gotchas loaded: [summary]" or "No gotchas recorded yet."

## Write Workflow (mandatory at the agent's UPDATE GOTCHAS step, including its `partial` and `blocked` exits)

### 1. Identify problem candidates

List the files changed during this invocation. For each file or group, check whether a problem arose:

- A conflicting or ambiguous convention
- A directory/filesystem access issue (permissions, missing paths, wrong cwd)
- A tool access issue (missing CLI, auth failure, unreachable service) during verification
- A missing applicable `chore-<stack>-rules` skill or Copilot instruction noted during review
- Any other friction that cost time or blocked progress

**Discard** one-off typos, transient blips resolved on first retry, and routine execution steps. Only friction that would help a future run avoid the same mistake qualifies.

**Emit**: "Files changed: [list]. Problem candidates: [list or 'none — reason per file']."

### 2. Distill and write each candidate

Distill each kept candidate into one reusable directive: `- <directive>`, optionally `- <directive> — <what to do instead>.` when the workaround adds concrete guidance. A discovery-gap becomes a note line, e.g. `- [note] chore-py-rules missing — Chorey was not configured.`

Scan the existing lines under `## Gotchas` for one covering the same rule or topic:

- **Match** → edit that line in place to extend/refine it. Never duplicate.
- **No match** → append under `## Gotchas`.

Zero candidates → write nothing.

**Emit**: "Gotchas updated: [count added/extended]" or "No gotchas to record."

## Hard Constraints

- Edit an existing line only when it is clearly the same rule being refined; otherwise append-only. Never delete or contradict an unrelated line without reporting the conflict.
- Never fabricate a directive not grounded in this invocation's actual friction.
