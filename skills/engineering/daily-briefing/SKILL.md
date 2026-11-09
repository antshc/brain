---
name: daily-briefing
description: >-
  Report the current Jira user's blocked work items and unanswered or answered @mentions over a period, default one month, as chat Markdown. Use for 'daily briefing', 'standup update', 'what's blocked', 'where was I mentioned', or 'unanswered mentions'.
argument-hint: '[period] (e.g. "2 weeks", "3 months"; default: 1 month)'
---

# Daily Briefing

Two read-only Jira reports for the current user: blocked items assigned to them, and open items where they are `@mentioned` in a comment, bucketed by whether anyone answered. Output is chat Markdown only.

## Prerequisites

- **`atlassian`** skill from `wf@brain`, providing twg routing.
- **`preflight-atlassian`** skill generated in this repo by the `atlassian` skill's Install tactic, with `email`/`apiToken` in its `.atlassian.json.user`.
- Missing `atlassian` → ask the user to install or update `wf@brain` and stop. Missing preflight → ask the user to run `/atlassian install` in Copilot CLI and stop. Never authenticate or install anything yourself.

## Contract

- **Input:** optional period; empty → `1 month`.
- **Budget:** two twg searches in one shell call (plus pagination pages), then two local scripts in one shell call. No per-issue reads.
- **Read-only:** no twg write command, no Jira mutation, no report file.
- **Identity:** Preflight's `accountId` only; never a display name.
- **Output:** the Output template in the workflow reference, printed in chat.

## Workflow

Read [references/workflow.md](references/workflow.md) fully, then follow it. Run its scripts from this skill's base directory: `python3 <skillDir>/scripts/blocked.py` and `python3 <skillDir>/scripts/mentions.py`, where `<skillDir>` is the parent of this `SKILL.md`; they work from any working directory.

## Gotchas

- **MUST NOT** `find`/`grep`/`ls -R` to locate this skill's directory; use the parent of the `SKILL.md` path you were given.
- `<twg>` exit `127` → report missing "twg CLI". Auth error → report `email`/`apiToken` in `.atlassian.json.user`. **MUST NOT** run `twg login` or `twg setup`.

## Completion criteria

- Chat output has the header line and only non-empty sections, every key linked with the row's own `url`.
- Excluded lists cutoff-excluded and partial-comment issues, truncation, and the Blocked-clause fallback whenever they apply.
- No file written besides twg spill files in a temp directory; no twg write command run.
