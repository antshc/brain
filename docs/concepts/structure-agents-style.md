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
[structure-checklist-workflow](structure-checklist-workflow.md).

How to word the agent file itself is write-time guidance — see
[agent-skills.instructions.md](../../.github/instructions/agent-skills.instructions.md).

## Examples

```md
Implement requested React features with minimal, maintainable changes.
Focus on accessibility, type safety, rendering, and tests.
For complex accessibility audits, follow the `/accessibility-audit` skill and apply its findings.
You are fully autonomous.
```
