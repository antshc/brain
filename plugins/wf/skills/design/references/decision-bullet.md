# Compact Decision

Render one established architectural decision as one bullet. Use only caller-established or source-grounded facts. Return the bullet for the slice's `**Decisions**`; this renderer does not write records or sync indexes.

```md
- **{{decisionTitle}}**: {{context}}. {{decision}} {{rationale}}.
```

- Title states the architectural decision, not the problem.
- Context explains why a decision is required.
- Decision states the choice and important implementation boundary.
- Rationale explains why this choice is preferable here, not the choice again.
- Name abstractions, interfaces, classes, events, fields, claims, services, topics, or components when part of the architectural contract.
- Include high-level implementation details only when they materially define the decision.
- Reference external protocol, API, or schema details from the Appendix only when the architecture depends on them.
- Keep method bodies, local variables, exact algorithms, and changeable details outside the bullet.
- Prefer application abstractions over nonessential vendor terminology.
- Add rationale, alternatives, consequences, or implementation steps only when explicitly requested.
- Follow the caller's provenance boundary: ADRs, Concepts, Architecture, and tickets are named or linked only in `Source Material`, never in decision bullets.

**Done when:** exactly one bullet matches the template, contains only established decision facts, and follows the rules above.
