---
name: investigation-template
description: Investigates unknown code paths, legacy runtime behavior, dependency flows, and design rationale through source tracing, evidence collection, and uncertainty reporting.
---

<!-- @: Copy into a concrete skill folder; rename folder and frontmatter name, then replace all task placeholders. -->

# Investigation

## Question
- Resolve {{question|Behavior or design rationale}} within {{scope|Repository and boundaries}}.

## Evidence trail
1. Trace actual inputs through responsible code and observable outputs. *Done when* each boundary has a concrete source.
2. Collect code, history, runtime evidence, exact search terms, empty results, and contradictions. *Done when* evidence can be independently revisited.
3. Separate observations from interpretation. *Done when* every conclusion has source support.

## Findings
- {{findings|Observed behavior and responsible symbols with references}}

## Uncertainty
- {{unknowns|Inferences, contradictions, and missing evidence}}
- MUST NOT present inferred intent as established fact.
- MUST NOT treat `_backup/` or `_in-progress/` as current source.

## Completion criteria
- The answer follows a verifiable code or evidence path, with uncertainties explicit.
