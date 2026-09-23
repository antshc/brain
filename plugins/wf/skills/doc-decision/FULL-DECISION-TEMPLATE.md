# Full Decision Template

Use for the title and body of a standalone ADR. The caller owns record metadata and placement.

## Template

```md
# {{decisionTitle}}

<!-- 1-3 sentences: what context required a decision and what was decided. -->
```

The body can be a single paragraph.

## Rules

- State the architectural decision in the title, not the problem.
- Explain why a decision is required in the body context.
- State what is chosen and the important implementation boundary in the body decision.
- Include concrete abstraction, interface, class, event, field, claim, service, topic, or component names when they are part of the architectural contract.
- Include high-level implementation details when they materially define the decision.
- Include references to external protocol, API, or schema details from the Appendix only when the architecture depends on them.
- Keep method bodies, local variables, exact algorithms, and details that can change without changing the decision outside the ADR.
- Prefer application abstractions over vendor-specific terminology when the vendor detail is not essential.
- Add rationale, alternatives, consequences, or implementation steps only when explicitly requested.

## Optional sections

Add only when explicitly requested:

- **Considered Options** — rejected alternatives worth preserving.
- **Consequences** — non-obvious downstream effects.