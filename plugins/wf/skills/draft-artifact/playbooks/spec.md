# Spec

## Purpose

Render one specification (PRD) containing one or more Requirement sets from supplied requirements and resolved decisions.

## Inputs

Problem, user-facing solution, Requirement sets, decisions, testing decisions, exclusions, notes and current context. A Requirement set groups a Stakeholder requirement with Functional requirements, Business rules and Edge cases. Optional: accepted design rationale, selected sketch manifest and existing spec. The caller owns design selection, artifact packaging and publication metadata.

## Required resources

Read the router's Spec template and shared requirements resources. For `normalize`, preserve the supplied fragment and return after Shared requirements rules.

## Workflow

1. **Reconcile inputs.** Respect the domain glossary, applicable Concepts/ADRs and supplied decisions. Treat missing evidence or conflicting source obligations as gaps; do not interview or choose an architecture during authoring. Done when each Requirement set and known decision has a source.
2. **Render.** Fill the Spec template. Keep behavior solution-agnostic and testable, separate from implementation decisions. Done when every source requirement/rule/edge case is represented.
3. **Contracts.** Inventory touched kinds API, Database, Resource, other and GUI from supplied context and verified local contracts. Invoke the router's Contracts producer per kind. Order outputs API → Database → Resource → other → GUI. Done when each kind has a substantive delta, or no contract change is recorded in the run summary.
4. **Check.** Apply shared requirements rules to authored behavior. Remove skill names, paths, invocation instructions and template directives from the entire publishable body, including inlined contract output. Done when required deltas have a `Legend:` line, a `#### header` and `<details>` per surface, with `+`, `-`, `%` or `~` delta lines; missing or hand-written deltas block readiness.

## Accepted design content

Map the selected `rationale.md` into the body; for an Architect Arena package, fall back to the base candidate's `rationale.md` only for sections the synthesis leaves empty:

- Problem and caller usage → **Problem Statement** and **Solution**, user-facing.
- Behavior the design commits to → **Requirements**, solution agnostic.
- Module shape, types, invariants, tradeoffs, rejected alternatives, and synthesis decision when present → **Implementation Decisions** as prose, after the **Design sketch** decision.
- Open questions and risks → **Further Notes**.
- Contracts touched → seed list for the Contracts gate; never copied into the body as a delta.

The body MUST NOT name design routes, candidate labels, or the run's local paths.

The caller supplies only the selected accepted package and manifest; never select Arena candidates or package artifacts here. Include the binding Design sketch decision only when such a package exists, listing Sketch index first. The body names neither design routes, candidate labels nor local run paths. Only its `{{artifactUrl}}` placeholders may remain while the caller attaches artifacts.

## Update behavior

Update matching requirement sets and decisions in place. Preserve unaffected content and source identifiers; report conflicting authority instead of silently replacing requirements.

## Completion criteria

- The template's required sections cover all supplied Requirement sets, decisions, testing choices and exclusions.
- Contracts Delta exists exactly when contracts change; every listed kind has authoritative producer output.
- No authoring directives or skill references remain; artifact URL placeholders are the sole permitted publication-time placeholders.
- Missing decisions/evidence are reported separately; no publication or readiness is claimed for unsupported content.

## Output

Return a short outcome title and the checked spec body. The caller adds initiative/branch/repository metadata, approves, publishes and attaches selected artifacts.
