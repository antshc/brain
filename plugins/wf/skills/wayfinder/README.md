# Wayfinder Cheat Sheet

Use this to choose the right Wayfinder ticket type.

| Type | Use when | Why | Example question |
|---|---|---|---|
| **Grilling** | Human judgment or a tradeoff is needed | Prevents the agent from inventing product or architecture decisions | Should tests reuse shared environments or create isolated ones? |
| **Research** | A decision depends on missing facts | Get evidence before deciding; do not mix research with implementation | What limitations does our current test infrastructure have? |
| **Prototype** | You need to try or observe something | A cheap experiment can resolve uncertainty faster than discussion | Can isolated test environments be provisioned cheaply enough? |
| **Task** | Prerequisite work blocks a decision | Unblock Wayfinding; never use it to implement the destination | What access or data must be obtained before we can evaluate the CI environment? |
| **Not yet specified** | You know an area matters but cannot state the question yet | Avoid speculative tickets based on assumptions | Keep it as fog until the exact question becomes clear |

## Rules

- One ticket = one clear question.
- Default to **Grilling** for decisions.
- **Research** = learn facts.
- **Prototype** = try something.
- **Task** = unblock a decision, not build the solution.
- If the question is unclear, keep it under **Not yet specified**.
- After each resolved ticket, reconsider the remaining map.
- Wayfinder ends with decisions; implementation comes afterward unless the map explicitly overrides that rule.

**Quick test:** What exactly is preventing us from making this decision?

## Source

- [Wayfinder skill](https://github.com/mattpocock/skills/blob/main/skills/engineering/wayfinder/SKILL.md)
