---
name: resume-template
description: Resumes interrupted or long-running agent work from durable execution trails, decisions, verified state, gotchas, and unresolved next actions.
---

# Context & continuity Skill Template

## Inputs
- `{{workspace|Repository or project and prior run}}`
- `{{state|Ledger, commits, task tracker, and prior handoff}}`

## Workflow
1. Read the latest durable handoff, commit history, and task state. *Done when* completed and pending work is distinguished.
2. Verify current repository, runtime, and ownership state before trusting the previous session. *Done when* stale assumptions and dirty work are visible.
3. Restore active constraints, prior decisions, and non-obvious gotchas; select the next incomplete action. *Done when* restarting requires no repeated discovery.
4. Record any new evidence and a restartable next step. *Done when* the updated ledger matches actual state.

## Guardrails
- MUST NOT rerun completed work solely because a fresh session lacks memory.
- MUST NOT treat stale notes as stronger evidence than the live workspace.

## Completion criteria
- Continuation starts from the verified frontier with preserved decisions and known risks.

## Handoff
- `{{resumeNote|Last verified state, outstanding work, gotchas, next action}}`

## Related recipe
- [Gotchas and persistent memory](../../gotchas-and-persistent-memory.md)
