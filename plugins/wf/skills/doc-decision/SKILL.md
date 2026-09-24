---
name: doc-decision
description: Render an established architectural decision as a compact bullet. Use for decision lists, design appendices, and `**Decisions**` sections. Owns formatting, not ADR placement or indexing.
---

# Document Decision

Render one architectural decision from established context as a compact bullet. Use only decision facts established by the caller or grounded in the source material.

## Template

```md
- **{{decisionTitle}}**: {{context}}. {{decision}} {{rationale}}.
```

- `{{decisionTitle}}`: the architectural decision, not the problem.
- `{{context}}`: why a decision is required.
- `{{decision}}`: what is decided, including architecturally significant abstractions, contracts, fields, components, and high-level implementation details.

## Rules

- Keep each decision to one bullet.
- State the architectural decision in the title, not the problem.
- Explain why a decision is required in `{{context}}`.
- State what is chosen and the important implementation boundary in `{{decision}}`.
- The rationale should explain **why this decision is preferable in this context**, not repeat the decision itself.
- Include concrete abstraction, interface, class, event, field, claim, service, topic, or component names when they are part of the architectural contract.
- Include high-level implementation details when they materially define the decision.
- Include references to external protocol, API, or schema details from the Appendix only when the architecture depends on them.
- Keep method bodies, local variables, exact algorithms, and details that can change without changing the decision outside the ADR.
- Prefer application abstractions over vendor-specific terminology when the vendor detail is not essential.
- Add rationale, alternatives, consequences, or implementation steps only when explicitly requested.

**Done when:** the bullet matches the template and every rule above has been applied.
