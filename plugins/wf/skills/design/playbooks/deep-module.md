# Deep module

Design a deep module interface, compare genuinely different shapes, and recommend a seam. Standalone: report and stop, no production code or code sketch unless separately requested. Architect can invoke this route to resolve a verified contract finding.

## Route

- **Direct request:** deepen a module interface, find deepening opportunities, select seam placement, or improve testability/AI navigation. User asks for a sketch too → run `design sketch` after the recommendation; asks to implement → use `design architect` with the recommendation as grounding.
- **Contract finding:** Challenge this verified an interface, invariant, ordering, error mode, configuration, seam, or adapter defect. Propose a corrected interface through this route before Architect applies it. Challenge this itself reports findings, not fixes.

## Procedure

1. Read [Deep modules](../references/deep-modules.md) fully. Name the module, interface, seam, and dependency categories using its vocabulary and the repository glossary.
2. Run [Design It Twice](../references/design-it-twice.md) on the target module; produce `deep-modules/problem.md`, three or more `option-<n>.md`, and `comparison.md` under the artifact root from `SKILL.md`.
3. Present the recommended interface, alternatives, tradeoffs, evidence, and `comparison.md` path. Contract finding → return the recommendation as a proposed correction to its caller; standalone → stop.
