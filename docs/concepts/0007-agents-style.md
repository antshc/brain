# Designing Effective Agents

**Status:** Accepted

## Purpose

A vague persona ("Frontend developer") or an agent that owns too many concerns drifts into generic, inconsistent behavior across invocations. Agent Design defines how agents are scoped, composed, and instructed so behavior stays predictable and reviewable.

## Design Guidance

- **Objective** State the concrete deliverable the agent must produce, not just its role.
- **Scope** Name the specific areas of concern the agent should focus on, implying what's out of scope.
- **Autonomy** State how independently the agent should act before checking in with the user.
- **Composition** Keep an agent focused on orchestration and its core judgment. For complex work, delegate specialized procedures and domain complexity to focused skills with clear inputs and outputs.
- **Persona** Define specific expertise and a working style, rather than a generic role.
- **Guardrails** State explicit **never** rules for irreversible or out-of-scope actions.
- **Output** Include a concrete output-format example.

## Examples

```md
Implement requested React features with minimal, maintainable changes.
Focus on accessibility, type safety, rendering, and tests.
For complex accessibility audits, follow the `/accessibility-audit` skill and apply its findings.
You are fully autonomous.
```