---
name: continuity-template
description: Restores interrupted agent sessions, long-running task context, persistent memory, and non-obvious gotchas from execution history verified against live state.
---

<!-- @: Copy into a concrete skill folder; rename folder and frontmatter name, then replace all task placeholders. -->

# Session continuity

## Prior execution trail
- {{trail|Last checkpoint, task tracker, commits, decisions, and known gotchas}}
1. Identify finished, incomplete, and abandoned work from durable records. *Done when* progress is not inferred solely from chat summaries.

## Live-state reconciliation
2. Compare the trail with current files, worktrees, runtime, and permissions. *Done when* stale facts and unrelated changes are visible.
- MUST NOT overwrite newer work based on old notes.

## Recovery point
- {{frontier|Last verified outcome and first unfinished task}}
- {{constraints|Standing instructions, non-obvious failure patterns, owner decisions}}
3. Resume from the first incomplete work unit. *Done when* no completed investigation or implementation is repeated without cause.
- MUST NOT repeat work solely because the session is new.

## Next handoff
4. Record decisions, changed files, check results, blockers, and a concrete next action. *Done when* a new session can continue without guesswork.
- {{next|Durable note and task reference}}

## Completion criteria
- The continuation point reflects current state and preserves original constraints.

## Related recipe
- [Gotchas and persistent memory](../../gotchas-and-persistent-memory.md)
