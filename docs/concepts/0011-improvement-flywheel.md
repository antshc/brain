---
id: "0011"
title: Improvement Flywheel
trigger: >-
  an agent repeating a mistake a previous run already hit, deciding where a fix for agent behaviour is recorded,
  rewriting a skill for something a memory line would fix, session friction worth keeping, a recurring question
  the agent should not need to ask, a gotcha discovered mid-run, choosing between memory and a skill edit, an
  agent using the wrong tool or skipping a validation, a session ending with friction nothing has recorded, a
  document that misrouted the very run it was steering
summary: >-
  An observed agent failure is routed to the cheapest tier that closes it before anything is rewritten: a
  missing fact becomes a memory or gotcha line, while wrong routing, a missing read-back, or an absent guardrail
  becomes a change to the skill, instruction file, or agent body — including the document that was steering the
  failing run, which improves itself rather than waiting for a separate pass. Every session closes by sweeping
  its own context for failures and recording each fix, so every run makes the next one better without human
  curation, which is what makes the loop a flywheel rather than a backlog.
default: >-
  Sweep the session's own context for observed failures before it closes, and route each to the cheapest tier
  that fixes it — a memory or gotcha line for a missing fact, a change to the skill, instruction, or agent body
  that misrouted the run for wrong routing or a missing guardrail.
owns:
  - "placement of a fix for observed agent behaviour"
  - "the end-of-session improvement sweep"
applies_to:
  - plugins/**
  - skills/**
  - .github/instructions/**
  - .crew/**
related: ["0004", "0010"]
---

# Improvement Flywheel

## Purpose

When an agent misbehaves, the reflex is to rewrite the skill it was running — which grows the always-loaded
instructions for a failure a single remembered fact would have prevented, and leaves the real cause untouched
when the cause was tool routing rather than wording. Matching the fix to the kind of failure is what turns
scattered corrections into a loop that compounds.

## Rules

- An observed failure MUST be classified before any fix is written.
- A failure caused by a missing fact MUST be fixed in the memory tier, not by editing a skill.
- A failure caused by wrong tool routing, a missing read-back, or an absent guardrail MUST be fixed in the
  harness tier — the skill, instruction file, or agent body that routes the work.
- A fix MUST be written to exactly one tier.
- A durable fix MUST be recorded in the same session the failure was observed.
- A recurring question the agent asks MUST be treated as a gap in the source that should have answered it.
- A session MUST end by sweeping its own context for observed failures.
- A document that misrouted the run it was steering MUST be corrected in place, by that run.

## Design Guidance

Match the tier to the failure, cheapest first:

| Failure looks like | Tier | Where the fix lands |
|--------------------|------|---------------------|
| forgets a convention, re-asks a settled fact | memory | `/memories/repo/`, `/memories/`, or the per-repo gotchas, code style file |
| reaches for the wrong tool, edits without validating, misses a guardrail | harness | the `SKILL.md`, `.github/instructions/` file, or `*.agent.md` that routes the work |
| fails broadly and consistently across tasks and languages | model | outside this repo's reach — record the observation and stop |

Classify before fixing, because the two reachable tiers fail differently in both directions. A missing fact
written into a skill turns one project's convention into a permanent instruction every future run pays for; a
routing defect written into memory leaves the route itself unchanged, so the next run takes the same wrong turn
with a note about it.

The loop closes only when the fix lands in the source that failed to prevent the failure. A run that reports
friction and changes nothing has spent the observation without banking it, and the same failure arrives again at
full cost.

A skill edit is the expensive move: it spends always-loaded context on every future run, whether or not the
failure recurs. Reach for it when the failure is genuinely about routing or wording, and reach for memory when
the agent simply did not know something.

### The sweep at the end of a session

The session's own context is the evidence. Nothing else records what the agent tried, what it retried, and
where it was corrected, and that record is gone once the session closes — so the sweep runs before the session
ends, not from a backlog afterwards.

Read back the session and collect each failure signal — a correction the user had to issue, a retry after a
wrong turn, a question already settled in an earlier session, a validation reached only after prompting, a
search that should have been a single lookup. Classify each against the table above and write it to that one
tier. Discard the transient: a typo, a blip resolved on first retry, friction that would not recur. A session
that found nothing durable records nothing.

A document steering the run is a legitimate target of its own sweep. When the failure was that the document
sent the agent the wrong way, left a step unguarded, or read ambiguously enough to be misapplied, the correction
belongs in that document — the one place where the next reader is guaranteed to meet it. The alternative,
wrapping the flawed document in another that compensates, leaves the wrong turn in place and charges every
future run for both.

## Violation signals

- A skill growing a line that names one project's convention rather than a rule.
- The same clarifying question asked across sessions with no record changed.
- A fix written to both a memory file and a skill.
- A run reporting friction that leaves no durable trace anywhere.
- A session ending straight after its last task, with no read-back over its own context.
- A document added to compensate for a wrong turn in another, rather than fixing that one.
