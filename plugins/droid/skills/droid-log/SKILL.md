---
name: droid-log
description: Agent problem log — appends session problems (conflicting conventions, directory/filesystem access, tool access) to LOG.md. Apply during the LOG PROBLEMS step, after feedback loops pass.
---

# Problem Log

## Store

Problems are appended to the `LOG_PATH` resolved by the agent during INPUT.

### Resolved path

Use the `LOG_PATH` value provided by the agent. INPUT guarantees it exists before this workflow runs.

## Write Workflow (runs once per invocation, after feedback loops pass)

For each problem found during this invocation — conflicting conventions, directory/filesystem access issues, tool access issues, or a `STATUS: blocked` environment error surfaced by `droid-feedback`'s "Environment blockers" section — append an entry:

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
