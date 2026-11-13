# Wayfinder Cheat Sheet

Use this to choose the right Wayfinder ticket type.

| Type | Use when | Why | Example question |
|---|---|---|---|
| **Grilling** | Human judgment or a tradeoff is needed | Prevents the agent from inventing product or architecture decisions | Should tests reuse shared environments or create isolated ones? |
| **Research** | A decision depends on missing facts | Get evidence before deciding; do not mix research with implementation | What limitations does our current test infrastructure have? |
| **Experiment** | You need to try or observe something | A cheap experiment can resolve uncertainty faster than discussion | Can isolated test environments be provisioned cheaply enough? |
| **Task** | Prerequisite work blocks a decision | Unblock Wayfinding; never use it to implement the destination | What access or data must be obtained before we can evaluate the CI environment? |
| **Contract design** | A new contract, an inheritance-based abstraction, or a significant contract change | Agent designs radically different options with class diagrams (AFK); human chooses (HITL) | What interface should the test-environment provider expose, and should providers share a base class? |
| **Not yet specified** | You know an area matters but cannot state the question yet | Avoid speculative tickets based on assumptions | Keep it as fog until the exact question becomes clear |

## Rules

- One ticket = one clear question.
- Default to **Grilling** for decisions.
- **Research** = learn facts; automatically dispatch ready in-scope codebase/cloud/web/rationale questions.
- **Experiment** = verify a factual claim automatically; material risks select Prove or Challenge this through the router-disclosed Risk verification resource. Record method, mitigation evidence and residual risk in Open Questions Answer; human preference or acceptance remains HITL.
- **Task** = unblock a decision, not build the solution.
- **Contract design** = new contract, inheritance abstraction, or significant contract change; options first, human picks later.
- If the question is unclear, keep it under **Not yet specified**.
- After each resolved ticket, reconsider the remaining map.
- Wayfinder maintains a living HLD as decisions and evidence arrive; implementation comes afterward only with separate user authorization.

**Quick test:** What exactly is preventing us from making this decision?

## Artifact lifecycle

Use separate local Research/verification worktrees from pinned integration HEAD. Wayfinder commits verified artifacts and merges them into its local integration branch before HLD synchronization and ticket resolution. Research goes under `docs/research/<initiative-slug>/`; proof evidence and retained sketches under `docs/prototype/<initiative-slug>/`. No automatic push or PR.

## Source

- [Wayfinder skill](https://github.com/mattpocock/skills/blob/main/skills/engineering/wayfinder/SKILL.md)
