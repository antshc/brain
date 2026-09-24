# Draft ADR

Draft one point-in-time, localized architectural decision. Run only on an explicit request for an ADR or a standalone decision file. For a compact decision inside a design or decision list, call `/doc-decision` directly.

## ADR gate

Check whether the decision is hard to reverse, surprising without its context, and a real trade-off between viable alternatives. These are reasons to preserve an ADR rather than a local design decision. Architectural shape, integration patterns, technology lock-in, ownership boundaries, intentional deviations, and invisible constraints can qualify. If a criterion is missing, explain the narrower fit; honor an explicit request to draft the ADR anyway.

Shared domain, structural, or operational rules that future work must follow belong in `/record-concept`; contested terminology belongs in `/record-term`.

## Extend or create

Before writing, inspect existing ADRs in `docs/adr/` and any decision files the caller identifies. If one already owns the same decision area, extend that file and preserve its identity. Otherwise, create one standalone ADR. Do not invoke `/index-docs` or add an `ARCHITECTURE.md` row.

If writing into `docs/adr/`, create the directory lazily. Assign the next id from the highest four-digit filename prefix plus one (`0001` if empty). Name the file `docs/adr/{{nnnn}}-{{slug}}.md`.

## Render the body

Use for the title and body of the ADR:

```md
# {{decisionTitle}}

<!-- 1-3 sentences: what context required a decision and what was decided. -->
```

The body can be a single paragraph.

### Rules

- State the architectural decision in the title, not the problem.
- Explain why a decision is required in the body context.
- State what is chosen and the important implementation boundary in the body decision.
- Include concrete abstraction, interface, class, event, field, claim, service, topic, or component names when they are part of the architectural contract.
- Include high-level implementation details when they materially define the decision.
- Include references to external protocol, API, or schema details from the Appendix only when the architecture depends on them.
- Keep method bodies, local variables, exact algorithms, and details that can change without changing the decision outside the ADR.
- Prefer application abstractions over vendor-specific terminology when the vendor detail is not essential.
- Add rationale, alternatives, consequences, or implementation steps only when explicitly requested.

### Optional sections

Add only when explicitly requested, and only when the evidence supports them; do not invent rationale or alternatives:

- **Considered Options** — rejected alternatives worth preserving.
- **Consequences** — non-obvious downstream effects.

Write the rendered body after the frontmatter. When the user requests text only, return the rendered draft without creating a file. Never update `ARCHITECTURE.md` as a side effect.
