---
id: "0005"
title: Checklist-Driven Workflow
trigger: >-
  authoring a skill with a sequential multi-step procedure, a step that can fail and require returning to an
  earlier step, a task needing resumable progress tracking, progress that must survive a context reset, an agent
  drifting out of sequence, naming a checklist header
summary: >-
  Embeds a literal Markdown checklist in a skill's instructions that the agent copies into its working notes at
  task start and checks off step by step, so ordered, resumable, multi-step procedures survive context resets
  and failures without drifting off sequence.
default: >-
  Embed a literal, fenced checklist the agent copies into its working notes whenever a procedure has three or
  more ordered steps, or whenever progress must survive a context reset.
owns:
  - "ordered, resumable execution tracking inside a skill"
applies_to:
  - plugins/**
  - skills/**
related: ["0004", "0007", "0008", "0009"]
---

# Checklist-Driven Workflow

## Purpose

A skill or agent task with multiple actions needs an explicit, ordered process when skipping an action, losing
progress after a context reset, or failing to return after an error would break correctness. A Checklist-Driven
Workflow embeds a literal Markdown checklist the agent copies into its working notes at task start, checks off
one item at a time, and re-consults before declaring the task done — giving it a durable record of execution
state rather than a recollection of one.

## Rules

- A skill whose actions are order-sensitive MUST number them.
- A skill with three or more sequential actions, or whose progress must survive a context reset, MUST embed a
  copied checklist.
- The checklist MUST be emitted as literal, fenced Markdown (`- [ ] N. ...`), not as prose describing the order.
- The fenced checklist MUST be preceded by the literal line
  `Copy this checklist and check off items as you complete them:`.
- The checklist header MUST be named after its own task or section (`<Task name> Progress:`), never a generic
  `Progress:`.
- Each checklist item MUST have its own numbered subsection giving the exact command or action and the artifact
  it produces.
- Each item MUST name concrete inputs, outputs, and scripts.
- The failure and retry path MUST be stated explicitly.

## Design Guidance

The copied checklist is what makes the workflow resumable: prose describing an order is re-derived on every
turn, where a checked-off list is read. Naming the header after the task keeps multiple checklists — an agent's
own plus each of its skills' — distinguishable when they land in working notes together.

Minimal skill instruction to embed:

```
## <Task name> Workflow

Copy this checklist and check off items as you complete them:
\```
<Task name> Progress:
- [ ] 1. <action> (run <script>)
- [ ] 2. <action> (edit <file>)
- [ ] 3. <action> (run <script>)
\```
**1. <action>**

Run: `<command>`

<what it produces>

...

If item <N> fails, return to item <M>.
```

Distinct from [0004](0004-completeness-sweep.md): a checklist orders sequential execution *during* the task; a
Completeness Sweep is a closing pass that checks coverage *after* implementation is believed done.

## Exceptions

- An agent/skill family that wants uniform structure for every action (e.g. `codey`/`chorey` and their `crew-*`
  skills) may embed a literal checklist even for 1–2 actions, trading minor ceremony for consistency across the
  whole family. The 3+/order-sensitive bar remains the default for skills outside such a family.
