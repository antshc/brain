# Constraint-First Agent Reasoning

## Purpose

Prevent an agent from replacing an explicitly required mechanism with a seemingly equivalent shortcut. When the mechanism itself protects context, responsibility boundaries, verification, or workflow semantics, following that mechanism is part of correctness, not an implementation preference.

## Approach

Resolve hard process constraints before optimizing execution. State the required mechanism, prohibit the likely substitute, and give a terse rationale when the reason is not obvious from the desired outcome. The rationale explains the property being protected so the agent does not reinterpret the constraint as optional.

Close the common escape hatch explicitly: a faster, simpler, smaller, or apparently equivalent route does not override the required mechanism. Define a fail-closed path when the mechanism cannot be used instead of allowing improvisation.

This policy constrains observable decisions and actions; it does not require exposing hidden chain-of-thought.

## Rules

- MUST treat explicit process `MUST` and `MUST NOT` requirements as hard constraints before optimizing the approach.
- MUST state the required mechanism and the forbidden substitution when an equivalent-looking shortcut is plausible.
- MUST include a terse rationale when the mechanism protects a property not evident from the requested outcome.
- MUST explicitly preserve the constraint even when another route appears faster, simpler, smaller, or sufficient.
- MUST define fail-closed behavior when the required mechanism is unavailable or fails.
- MUST NOT substitute another mechanism merely because it can produce an equivalent outcome.
- MUST NOT optimize around, reinterpret, or weaken an explicit hard constraint.

## Example

When codebase exploration is required, MUST invoke the exploration subagent and MUST NOT explore directly in the parent agent.

Reason: delegation preserves the parent context for orchestration and isolates exploration responsibility.

Even when direct exploration appears faster or sufficient, MUST delegate it. If the subagent cannot be invoked, stop and report the blocker.
