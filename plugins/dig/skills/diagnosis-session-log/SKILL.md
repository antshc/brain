---
name: diagnosis-session-log
description: Own the diagnosis log (default /memories/session/diagnosis-{{bugSlug}}.md, or a caller-supplied folder) — its location, template, resume check, shared log events, entry rules, and blocked state. Use when another skill needs to open, resume, write, or block the diagnosis log; the caller adds its own events.
---
# Track Session Log

The log is the run's whole memory: a later run with no memory of this one continues from it alone. It records facts, never intentions.

Every skill working the same bug writes to the same log. The caller supplies its own event table; this skill owns everything else.

## Location

`bugSlug :=` short kebab-case name of the symptom; `logDir :=` caller-supplied folder, else `/memories/session` (session memory); `logPath := {{logDir}}/diagnosis-{{bugSlug}}.md`.

## Open

If `$logPath` exists and this conversation did not write it, **resume**:

1. Read the whole log.
2. Re-verify against the workspace: `Commit` matches `git rev-parse HEAD`; every `Artifacts` bullet marked `present` exists. Log any drift as an event.
3. Run `Setup`, then re-run the recorded loop; its verdict must match the last recorded one. On mismatch, log it and resume from the earliest phase it invalidates.
4. Continue at `Next step`, keeping bullet IDs consecutive.

No `$logPath` → create it from `session-log.template.md` (resolved from this skill's base directory) and fill its `Summary`.

Done when `$logPath` exists and, on resume, the drift and loop verdict are logged.

## Write

Write each **log event** the moment it happens, before the next action. The caller's event table extends these:

| Log event | Write |
|---|---|
| A phase starts | `### {{phase name}}` under `Investigation`; `Summary` → `Status` |
| A file is created, modified, or removed | Its `Artifacts` bullet |
| Any event | `Summary` → `Next step` |

Every entry:

- One bullet per event; unreached sections keep placeholders.
- Re-checkable evidence: copy-pasteable command, redacted signal lines only, `path:line` for code claims. A conclusion names the bullet ID that proves it.
- Secrets by env var name (`$API_TOKEN`); outputs redacted (`<REDACTED>`).
- Dead ends too — rejected loops, falsified hypotheses, empty probes.

## Blocked

Set `Status: blocked`, record what was tried, set `Next step` to what unblocks it, and stop.
