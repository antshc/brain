---
name: csdroid-log
description: C# agent problem log — appends session problems (conflicting conventions, directory/filesystem access, tool access) to LOG.md. Apply during the LOG PROBLEMS step, after feedback loops pass.
---

# Problem Log

## Store

Problems are appended to `LOG.md`, kept inside the harness root at the fixed path `$HARNESS_ROOT/agent/LOG.md` — never recursively scanned, never the worktree cwd.

### Resolve repo

Use the `HARNESS_ROOT` value provided to you by the agent (substitute its literal absolute value for `$HARNESS_ROOT`; it defaults to the current working directory when no argument was given).

```bash
STORE="$HARNESS_ROOT/agent/LOG.md"
```

Initialize if missing: `mkdir -p "$HARNESS_ROOT/agent" && touch "$STORE"`.

## Write Workflow (runs once per invocation, after feedback loops pass)

For each problem found during this invocation — conflicting conventions, directory/filesystem access issues, tool access issues, or a `STATUS: blocked` environment error surfaced by `csdroid-feedback`'s "Environment blockers" section — append an entry:

```md
## <task-id-or-title> — <date>
- **category**: convention-conflict | directory-access | tool-access | other
- **severity**: blocking | note
- **problem**: <one line>
- **context**: <file/path/tool involved>
- **workaround**: <what the agent did, or "blocked">
```

- One entry per problem. Multiple problems in the same invocation → multiple entries.
- **Discard** if it is: a one-off typo, a transient blip resolved on first retry, or a routine execution step. Only what a human reviewer would want to see, and possibly promote to `agent/MEMORY.md`, qualifies.
- **Zero problems found** → skip silently, write nothing.

**Emit**: "Problems logged: [count/categories]" or "No problems to log."

## Hard Constraints

- Append only — never edit or delete existing entries.
- Write only to the repo-resolved fixed path. Never derive or use any other location.
- Do not record transient notes, one-off errors already fixed on retry, or routine execution steps.
