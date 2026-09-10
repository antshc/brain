---
name: write-flow
description: Use when the user asks to document a workflow, process, activity, feature behavior, decision logic, or flowchart as structured flow text, including flows with branches or subflows.
---

Write the behavior as **structured flow text**: a compact textual flow that preserves sequence, decisions, branches, and reusable subflows.

## Format

```text
Flow: <name>

Start
→ <action>
→ <decision>?
  → <outcome>: <action or result>
  → <outcome>:
      → <action>
      → Run <Subflow Name>
→ End

Subflow: <Subflow Name>

→ <action>
→ <decision>?
  → <outcome>: <action or result>
  → <outcome>: <action or result>
→ Return <result>
```

## Rules

- Write actions as short verb phrases: `Validate request`, `Create refund`, `Notify customer`.
- Write decisions as questions ending in `?`.
- Put each decision outcome on its own indented branch: `→ Yes:`, `→ No:`, or a domain-specific outcome.
- Keep the main flow focused on the primary path and important decisions.
- Extract a branch into a named subflow when it is reusable, independently meaningful, or would make the main flow deeply nested.
- Call subflows with `→ Run <Subflow Name>` and use the exact same name in `Subflow: <Subflow Name>`.
- End every main-flow path with `End` or a path that rejoins the main flow.
- End every subflow with `Return` or `Return <result>` when the caller needs an outcome such as `Success`, `Failure`, or `Retry`.
- Use `TBD: <missing behavior>` when required behavior is unknown; do not invent steps or decisions.
- Preserve externally supplied terminology, API names, states, and outcomes when they are relevant to the flow.
- Prefer shallow nesting. When branching becomes hard to scan, extract a subflow instead of adding more indentation.

## Parallel work

When independent actions happen concurrently, make the parallelism explicit:

```text
→ In parallel:
  → <action A>
  → <action B>
→ Continue when all complete
```

State a different join condition when applicable, such as `Continue when any completes`.

## Example

```text
Flow: Refund request

Start
→ Receive refund request
→ Validate eligibility
→ Eligible?
  → No: Reject request → Notify customer → End
  → Yes:
      → Run Payment Refund
      → Refund successful?
        → No: Run Refund Failure
        → Yes: Notify customer → End

Subflow: Payment Refund

→ Load payment
→ Submit refund
→ Refund accepted?
  → Yes: Return Success
  → No: Return Failure

Subflow: Refund Failure

→ Record failure
→ Retry allowed?
  → Yes: Return Retry
  → No: Notify operator → Return Failure
```

Return only the structured flow unless the user asks for explanation or another representation.