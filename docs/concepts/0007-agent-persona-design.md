# Writing Effective Agent Personas

**Status:** Accepted

## Purpose

A vague persona ("Frontend developer") lets an agent drift into generic, inconsistent behavior across invocations. Agent Persona Design fixes the traits every agent/skill instruction file must define so behavior stays predictable and reviewable.

## Design Guidance

Every agent persona (`.agent.md`, `SKILL.md` role section) must define:

- **Expertise** — specific, not generic. `Expert in React 18+ with TypeScript` beats `Frontend developer`.
- **Working style** — state whether the agent asks clarifying questions or assumes defaults, and whether it is concise or thorough.
- **Guardrails** — explicit **never** rules for irreversible or out-of-scope actions, e.g. `Never modify production configuration files directly`.
- **Output format** — a concrete example of expected output (review comment shape, code pattern, file layout).

## Examples

```md
You are an expert in React 18+ with TypeScript.
Ask a clarifying question only when requirements conflict; otherwise assume sane defaults and proceed.
Never modify production configuration files directly.
Output review comments as: `**Issue:** ... **Fix:** ...`
```
