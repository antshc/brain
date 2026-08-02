# Writing Effective Agent Personas

**Status:** Accepted

## Purpose

A vague persona ("Frontend developer") lets an agent drift into generic, inconsistent behavior across invocations. Agent Persona Design fixes the traits every agent/skill instruction file must define so behavior stays predictable and reviewable.

## Design Guidance

- **Objective** State the concrete deliverable the agent must produce, not just its role.
- **Scope** Name the specific areas of concern the agent should focus on, implying what's out of scope.
- **Autonomy** State how independently the agent should act before checking in with the user.

## Examples

```md
Implement requested React features with minimal, maintainable changes.
Focus on accessibility, type safety, rendering, and tests.
You are fully autonomus.
```
