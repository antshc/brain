---
name: crew-gotchas
description: "Apply repository-local gotcha rules and produce reusable rule updates from implementation or review friction. Use through crew-memory when Codey or Chorey enters its GOTCHAS or UPDATE GOTCHAS step."
---

# Gotchas

`/crew-memory` passes the current entries under its `GOTCHAS.md` `## Gotchas` section as `GOTCHAS RULES`. Operate only on those supplied rules. Never locate, read, or write a `GOTCHAS.md` file; `/crew-memory` owns storage.

## Read Workflow (mandatory before the agent's main work)

Read every supplied `GOTCHAS RULES` entry. Missing or empty rules → "No gotchas recorded yet."

Apply every directive found during the agent's work — never contradict one without reporting the conflict.

**Emit**: "Gotchas loaded: [summary]" or "No gotchas recorded yet."

## Write Workflow (mandatory at the agent's UPDATE GOTCHAS step, including its `partial` and `blocked` exits)

### 1. Identify problem candidates

List the files changed during this invocation. For each file or group, check whether a problem arose:

- A conflicting or ambiguous convention
- A directory/filesystem access issue (permissions, missing paths, wrong cwd)
- A tool access issue (missing CLI, auth failure, unreachable service) during verification
- A missing `/crew-chore` skill, stack rule file, or Copilot instruction noted during review
- Any other friction that cost time or blocked progress

**Discard** one-off typos, transient blips resolved on first retry, and routine execution steps. Only friction that would help a future run avoid the same mistake qualifies.

**Emit**: "Files changed: [list]. Problem candidates: [list or 'none — reason per file']."

### 2. Distill each candidate and return rule updates

Distill each kept candidate into one reusable directive: `- <directive>`, optionally `- <directive> — <what to do instead>.` when the workaround adds concrete guidance. A discovery-gap becomes a note line, e.g. `- [note] crew-chore missing — Chorey was not configured.`

Scan `GOTCHAS RULES` for one covering the same rule or topic:

- **Match** → return an exact replacement that extends/refines that rule. Never duplicate.
- **No match** → return the new rule to append.

Return `RULE UPDATES` to `/crew-memory` as exact `replace <existing rule> with <refined rule>` or `append <new rule>` operations. Zero candidates → return no updates. Do not persist the updates yourself.

**Emit**: "Gotchas updated: [count added/extended]" or "No gotchas to record."

## Hard Constraints

- Edit an existing line only when it is clearly the same rule being refined; otherwise append-only. Never delete or contradict an unrelated line without reporting the conflict.
- Never fabricate a directive not grounded in this invocation's actual friction.
