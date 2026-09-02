---
id: "0010"
title: Skill Composition
trigger: >-
  splitting one skill into two, a procedure needed by more than one skill, an agent body restating a skill's
  steps, deciding whether a skill is model- or user-invoked, choosing what a new skill is responsible for, one
  skill reaching another skill's behaviour, a skill accumulating unrelated responsibilities, the same steps
  appearing in two skills, a family of related agents sharing a workflow, one agent extending or overriding
  another, an agent file pointing at another agent file
summary: >-
  A skill is responsible for one purpose, and behaviour needed by more than one caller is owned by exactly one
  skill that the others reach by name rather than restate. A family of agents sharing a workflow follows the same
  rule: the workflow becomes a flow skill each member invokes, and a member carries only what it overrides — an
  agent file never points at another agent file. Invocation is a design choice, not a formatting one:
  a skill keeps a description only when an agent or another skill must reach it unprompted, because that
  description is loaded on every turn whether or not it fires.
default: >-
  Give each skill one purpose and invoke a sibling skill's documented action by name instead of restating its
  steps; give a family of agents one flow skill they each invoke, leaving each member only its overrides; keep a
  skill model-invoked only when an agent or another skill must reach it unprompted.
owns:
  - "division of a capability across skills"
  - "composition of a family of related agents"
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
- A workflow shared by a family of agents MUST live in one flow skill each member invokes.
- A member of such a family MUST carry only the phases it overrides, and MUST NOT restate the shared workflow.
- An agent file MUST NOT point at another agent file: a skill name resolves, an agent's install path does not.
- One flow skill MUST NOT serve two families whose steps differ, because it then branches on its caller.

## Design Guidance

Divide by counting callers, not by size:

| Callers | Home | Reached by |
|---------|------|------------|
| one skill | that skill, inline | nothing — it is not shared |
| several skills or agents | the one skill that owns the purpose | `` `/{{skillName}}` `` **{{ActionName}}** |
| a human only | a user-invoked skill, no `description` | the human typing its name |

A skill extends itself the same way it shares: when the behaviour it needs sits outside its own single purpose,
it invokes the skill that owns that purpose instead of growing a second responsibility. The owned mechanics stay
in one place, and every sibling that needs them gets them by calling rather than copying.

Invocation is the second cut, and it is paid for in different currencies. A model-invoked skill spends context
on every turn for a description that may never fire; a user-invoked skill spends nothing there but makes you the
index that has to remember it exists. Split off a model-invoked skill only when you have a trigger word you
actually type, or when another skill must reach it.

An agent body holds its objective, its ordered workflow, and the verdict it returns; every procedure that could
be stated without knowing which agent is running it belongs in a skill the body invokes by name. Two agents
needing the same procedure is the clearest signal it was never the agent's to hold.

A family of agents — one general member and several specialised ones — is the same cut seen from the agent side.
The temptation is to copy the general member and edit it, or to have each specialist read the general one as a
parent. Copies drift on every base change; the parent pointer has no addressing mechanism behind it, because an
agent knows neither its own install path nor a way to name a sibling file. Both dissolve once the shared workflow
moves into a **flow skill**: each member is then frontmatter, a flow-skill invocation, and only the phases it
overrides — a delta, not a copy. Two families with genuinely different steps get two flow skills, because one
skill serving both would branch on its caller, which is worse than the duplication it avoids.

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
