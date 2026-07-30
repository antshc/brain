# Domain Model Ledger

## Opened records

docs/adr/0003-droid-is-technology-agnostic.md — opened, trigger matched: "agent/skill naming"
docs/concepts/0004-completeness-sweep.md — opened, trigger matched: "designing a skill"
docs/concepts/0005-checklist-workflow.md — opened, trigger matched: "authoring a skill with a sequential multi-step procedure"

## Touched surface

skill, instructions, agent, codex, copilot

## Decisions / assumptions

plugins/<plugin>/agents/ is source of truth — decided by user, feature decision, grounded: "plugins/droid is the only agent with dual coverage; .agents/ and .codex/ are deployment copies"
Sync mechanism: concept-only (manual authoring discipline, no tooling) — decided by user, feature decision, grounded: "user chose option 2 explicitly"
