---
name: architecture-template
description: Designs architecture boundaries, public API contracts, domain invariants, and module responsibilities from caller usage and evaluated alternatives.
---

<!-- @: Copy into a concrete skill folder; rename folder and frontmatter name, then replace all task placeholders. -->

# Architecture and contracts

## Consumer scenarios
1. Write representative caller usage for {{feature|Capability or API}}. *Done when* success, error, and compatibility behavior are clear.
- {{consumerNeeds|Required inputs, outputs, ownership, and failure behavior}}

## Contract
2. Define minimal public types, operations, and domain invariants. *Done when* callers need no internal implementation knowledge.
- {{contract|Signatures or protocol schema}}
- {{boundaries|Owned state, provided and consumed interfaces}}
- MUST NOT expose internal mechanics as public APIs merely for convenience.

## Alternatives and tradeoffs
3. Compare viable designs for complexity, safety, and consumer experience. *Done when* each rejected option has a concise reason.
- {{alternatives|Candidates, evidence, costs, failure modes}}

## Decision
- Selected: {{decision|Chosen contract and rationale}}
- Compatibility: {{migration|Impact on existing callers and migration}}
- Unresolved: {{openDesign|Risks and decision owners}}

## Completion criteria
- Caller examples use the selected contract without relying on unspecified internals.
- The selected design preserves invariants and records material tradeoffs.
