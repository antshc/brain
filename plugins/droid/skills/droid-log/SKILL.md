---
name: droid-log
description: Agent problem log — appends session problems (conflicting conventions, directory/filesystem access, tool access) to LOG.md. Apply during the LOG PROBLEMS step, after feedback loops pass.
---

# Log Problems

```
Log Problems Progress:
- [ ] Step 1: Identify problems from this invocation
- [ ] Step 2: Append one entry per problem to LOG_PATH (or skip silently if none)
```

## Store

Problems are appended to the `LOG_PATH` resolved by the agent during INPUT.

### Resolved path

Use the `LOG_PATH` value provided by the agent. INPUT guarantees it exists before this workflow runs.

## Step 1: Identify problems (runs once per invocation, after feedback loops pass)

List the files changed during this invocation. For each file or group of files, check whether a problem arose:
- A conflicting or ambiguous convention encountered
- A directory/filesystem access issue (permissions, missing paths, wrong cwd)
- A tool access issue (missing CLI, auth failure, unreachable service) — including any `STATUS: blocked` "Environment blockers" surfaced by `droid-feedback`
- Any other friction that cost time or blocked progress

**Discard** if it is: a one-off typo, a transient blip resolved on first retry, or a routine execution step. Only what a human reviewer would want to see, and possibly promote to `MEMORY.md`, qualifies.

**Emit**: "Files changed: [list]. Problem candidates: [list or 'none — reason per file']."

## Step 2: Append entries to LOG_PATH

For each problem found during this invocation, append an entry:

```md
## <task-id-or-title> — <date>
- **category**: convention-conflict | directory-access | tool-access | other
- **severity**: blocking | note
- **problem**: <one line>
- **context**: <file/path/tool involved>
- **workaround**: <what the agent did, or "blocked">
```

- One entry per problem. Multiple problems in the same invocation → multiple entries.
- **Discard** if it is: a one-off typo, a transient blip resolved on first retry, or a routine execution step. Only what a human reviewer would want to see, and possibly promote to `MEMORY.md`, qualifies.
- **Zero problems found** → skip silently, write nothing.

**Emit**: "Problems logged: [count/categories]" or "No problems to log."

## Hard Constraints

- Append only — never edit or delete existing entries.
- Write only to the supplied `LOG_PATH`. Never derive or use any other location.
- Do not record transient notes, one-off errors already fixed on retry, or routine execution steps.
