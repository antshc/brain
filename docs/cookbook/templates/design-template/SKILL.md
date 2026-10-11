---
name: design-template
description: Designs consumer-first APIs, module boundaries, data models, and architectural tradeoffs for new components, refactoring, or shared interfaces.
---

# Architecture & contracts Skill Template

## Inputs
- `{{consumer|Caller scenarios and usage examples}}`
- `{{constraints|Runtime, compatibility, and quality bounds}}`

## Workflow
1. Write caller-side usage for `{{contract|Proposed interface}}` before implementation. *Done when* typical and failure paths are clear.
2. Model domain invariants and choose minimal public data shapes. *Done when* invalid states and ownership boundaries are addressed.
3. Compare viable contracts or prototypes against consumer needs; identify red flags and unnecessary indirection. *Done when* tradeoffs are documented.
4. Define the supported public path, hidden internals, and compatibility impact. *Done when* an implementer can apply the selected contract.

## Guardrails
- MUST NOT expose implementation mechanics solely for caller convenience.
- MUST NOT treat implementation ease as stronger evidence than consumer usage.

## Completion criteria
- Contract examples, invariants, alternatives, rationale, and migration impact are recorded.

## Handoff
- `{{design|Public contracts, responsibilities, tradeoffs, and open risks}}`
