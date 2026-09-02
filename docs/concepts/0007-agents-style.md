---
id: "0007"
title: Agent Design
trigger: >-
  writing or reviewing an `.agent.md`, composing an agent from skills, a vague or generic persona description,
  an agent owning specialized complexity, an agent drifting into inconsistent behavior across invocations,
  deciding how autonomous an agent should be, an agent with no stated output format, declaring which files or
  areas an agent covers, a family of related agents, one agent overriding another's phase
summary: >-
  Every agent defines a concrete objective, bounded scope, autonomy, specific expertise, a working style,
  explicit **never** guardrails, and a concrete output format. Complex agents delegate specialized procedures
  and domain complexity to focused skills with clear inputs and outputs, keeping behavior predictable and
  reviewable.
default: >-
  Give an agent one concrete deliverable, a bounded scope, stated autonomy, explicit never-rules, and a literal
  output-format block; delegate every specialized procedure to a skill.
owns:
  - "agent objective, scope, autonomy, guardrails, and output contract"
applies_to:
  - plugins/**/agents/**
related: ["0005", "0010"]
---

# Agent Design

## Purpose

A vague persona ("Frontend developer") or an agent that owns too many concerns drifts into generic, inconsistent
behavior across invocations. Agent Design fixes how agents are scoped, composed, and instructed so behavior
stays predictable and reviewable.

## Rules

- An agent MUST state the concrete deliverable it produces, not only its role.
- An agent MUST name the specific areas of concern it covers, in the form a caller can match against — globs where the areas are files.
- An agent MUST state how independently it acts before checking in.
- An agent MUST define specific expertise and a working style rather than a generic role.
- An agent MUST state explicit **never** rules for irreversible or out-of-scope actions.
- An agent MUST include a concrete output-format block.

## Design Guidance

Keep the agent body on orchestration and its own judgment; everything specialized moves behind a skill with
documented inputs and outputs. Delegation and the call style that carries it are owned by
[0010](0010-skill-composition.md), and the ordered-execution mechanism by
[0005](0005-checklist-workflow.md).

How to word the agent file itself is write-time guidance — see
[agent-skills.instructions.md](../../.github/instructions/agent-skills.instructions.md).

## Examples

```md
Implement requested React features with minimal, maintainable changes.
Focus on accessibility, type safety, rendering, and tests.
For complex accessibility audits, follow the `/accessibility-audit` skill and apply its findings.
You are fully autonomous.
```
