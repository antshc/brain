---
id: "0010"
title: Skill Composition
trigger: >-
  splitting one skill into two, a procedure needed by more than one skill, an agent body restating a skill's
  steps, deciding whether a skill is model- or user-invoked, choosing what a new skill is responsible for, one
  skill reaching another skill's behaviour, a skill accumulating unrelated responsibilities, the same steps
  appearing in two skills
summary: >-
  A skill is responsible for one purpose, and behaviour needed by more than one caller is owned by exactly one
  skill that the others reach by name rather than restate. Invocation is a design choice, not a formatting one:
  a skill keeps a description only when an agent or another skill must reach it unprompted, because that
  description is loaded on every turn whether or not it fires.
default: >-
  Give each skill one purpose and invoke a sibling skill's documented action by name instead of restating its
  steps; keep a skill model-invoked only when an agent or another skill must reach it unprompted.
owns:
  - "division of a capability across skills"
  - "skill-to-skill and agent-to-skill invocation style"
  - "model- versus user-invocation choice"
applies_to:
  - plugins/**
  - skills/**
related: ["0001", "0007", "0009"]
---

# Skill Composition

## Purpose

A capability that grows past one skill can be divided two ways, and each has a failure the other avoids: copying
the shared steps into every skill that needs them leaves several drifting implementations of one behaviour,
while giving every fragment its own model-invoked skill spends always-loaded description budget on skills the
agent never needs to find. This Concept fixes how a capability is divided and how the pieces reach each other.

## Rules

- A skill MUST be responsible for exactly one purpose, nameable in a single phrase.
- A skill that needs behaviour outside its own purpose MUST reach it by invoking the skill that owns it.
- Behaviour needed by more than one caller MUST be owned by exactly one skill.
- A caller MUST reach another skill's behaviour by invoking its documented action, naming it as
  `` `/{{skillName}}` `` **{{ActionName}}**.
- A caller MUST NOT restate, paraphrase, or inline the steps of the skill it invokes.
- The same procedure MUST NOT be written in two skills.
- An action MUST document the values it reads and what it returns, so a caller can invoke it without reading
  the skill's internals.
- A skill MUST keep a `description` only when an agent or another skill must reach it unprompted; otherwise it
  MUST set `disable-model-invocation: true`.
- An agent body MUST carry only its objective, workflow, and verdict, and MUST delegate every specialised
  procedure to a skill it invokes by name.

## Design Guidance

Divide by counting callers, not by size:

| Callers | Home | Reached by |
|---------|------|------------|
| one skill | that skill, inline | nothing — it is not shared |
| several skills or agents | the one skill that owns the purpose | `` `/{{skillName}}` `` **{{ActionName}}** |
| a human only | a user-invoked skill, no `description` | the human typing its name |

A skill extends itself the same way it shares: when the behaviour it needs sits outside its own single purpose,
it invokes the skill that owns that purpose instead of growing a second responsibility. `record-adr` reaching
`/index-docs` to sync its row is the shape — the row mechanics stay owned by one skill, and every record-writing
sibling gets them by calling rather than copying.

Invocation is the second cut, and it is paid for in different currencies. A model-invoked skill spends context
on every turn for a description that may never fire; a user-invoked skill spends nothing there but makes you the
index that has to remember it exists. Split off a model-invoked skill only when you have a trigger word you
actually type, or when another skill must reach it.

`codey` is the reference shape: its body carries the workflow and the status verdict, and delegates every
specialised procedure — `/crew-gotchas`, `/crew-implement`, `/crew-feedback` — passing each resolved path.
`chorey` reaches the same three skills, so neither agent carries a second copy.

Two related records own adjacent areas: [0001](0001-resource-access-skill.md) owns *what* a skill encapsulates
when its purpose is infrastructure access, and [0009](0009-skill-owned-code.md) owns where a skill's code and
tests live. This record owns the division and the call style only.

How to word a description, name a skill, or lay out its folders is write-time guidance, not design — see
[agent-skills.instructions.md](../../.github/instructions/agent-skills.instructions.md).

## Violation signals

- The same steps, table, or checklist appearing in two `SKILL.md` files.
- An agent body carrying a procedure one of its skills already documents.
- A caller spelling out the command a skill wraps, instead of naming the skill.
- A skill whose description needs "and" to state what it does.
- A model-invoked skill no agent and no other skill ever reaches.
