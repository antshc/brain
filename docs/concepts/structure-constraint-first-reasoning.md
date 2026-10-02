# Constraint-First Reasoning

## Purpose

Agents may reinterpret a required mechanism as a preference and replace it with an equivalent-looking shortcut.
Constraint-First Reasoning makes the process itself part of correctness so explicit delegation, isolation, or
workflow boundaries are not optimized away.

## Rules

- Explicit `MUST` and `MUST NOT` requirements are hard constraints on both planning and execution.
- The agent MUST resolve hard constraints before optimizing for speed, simplicity, fewer tool calls, or equivalent output.
- The agent MUST NOT consider alternatives that violate a hard constraint.
- When a mechanism is required, the agent MUST use that mechanism rather than reproduce its behavior directly.
- The agent MUST NOT substitute another agent, skill, tool, search path, or direct implementation unless substitution is explicitly allowed.
- A process constraint SHOULD include one terse reason when the reason explains an architectural property the agent might otherwise optimize away.
- The rationale MUST explain why the constraint exists; it MUST NOT weaken the constraint or turn it into a preference.
- When useful, state the expected temptation explicitly: even if another path appears faster, smaller, simpler, or sufficient, the required mechanism still applies.
- If the required mechanism is unavailable, the agent MUST follow the defined failure path rather than improvise around the constraint.

## Pattern

```md
MUST <required behavior>.
MUST NOT <undesired substitution>.

Reason: <one sentence explaining why the constraint exists>.

Even if <obvious optimization>, MUST still <required behavior>.
If <required mechanism> is unavailable, <defined failure behavior>.
```

## Example

```md
When codebase exploration is required, MUST invoke the `exploration` subagent.
MUST NOT explore the codebase directly or substitute another exploration mechanism.

Reason: exploration is isolated to preserve the parent agent's context for orchestration and keep
exploration responsibility bounded.

Even when direct exploration appears faster, smaller, or sufficient, MUST delegate it.
If the exploration subagent cannot be invoked, STOP and report the blocker.
```

## Violation Signals

- "I can do this directly because it is faster."
- Reproducing a delegated procedure in the parent agent.
- Replacing a named required mechanism with an equivalent-looking tool or workflow.
- Treating a `MUST` as one candidate approach during planning.
- Using the rationale to justify an exception not stated by the instruction.
