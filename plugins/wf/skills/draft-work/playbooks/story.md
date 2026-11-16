# Story

## Purpose

Draft one atomic, testable user story advancing one Functional slice owned by one Deployable.

## Inputs

Optional Initiative tag; required Deployable kind (`[FE]` or `[BE]`), Feature, Functional slice, Stakeholder requirement, addressed Functional requirements, Business rules, Edge cases, error conditions and Acceptance criteria. Derive omitted fields from the standalone requirement in context; preserve supplied source fields verbatim. Use `GLOSSARY.md` and `ARCHITECTURE.md` when available.

An Initiative tag is SCREAMING_SNAKE_CASE. A Functional slice is one deployable-local end-to-end behavior.

## Required resources

Read the router's Story template and local requirements resources. For `normalize`, apply Requirements rules and return without full-template rendering.

## Workflow

1. **Assemble.** Render the Title and addressed requirements from the template; keep scope within one slice. Done when required fields and verbatim sources are accounted for.
2. **Derive criteria.** Write single, self-contained pass/fail checks, verifiable without reading code. Use `{{outcome}} when {{condition}}` for behaviors; `If {{condition}}, {{actor}} must {{outcome}}` for invariants and edge cases. Vary subjects. Cover input, processing, integration, state and failure; fold every applicable rule, edge case and error into its own criterion without separate rule/edge-case sections. Done when each source obligation maps to an observable criterion with an exact result.
3. **Normalize.** Apply requirements rules to authored Title, Requirements and criteria. Preserve supplied Feature, Functional slice, Stakeholder requirement and Functional requirements verbatim; report source conflicts separately. Done when each criterion implies concrete code changes, belongs to the slice and can be tested by QA.
4. **Contracts.** For changed contracts, invoke the router's Contracts producer per touched kind; put its output in Technical notes. Done when every changed kind passes its producer's completion criteria.

## Update behavior

Preserve unaffected content, source wording and existing decisions. Derive only missing fields or authorized changes; return unresolved source conflicts.

## Completion criteria

- Title uses the exact template format; optional Initiative tag immediately precedes Deployable kind.
- One slice and one owning Deployable; every addressed requirement appears.
- Every criterion is observable, exact and covers its source obligations; no leaked implementation remains outside protected source text.
- Technical appendices follow template conditions; required contract deltas are complete.

## Output

Return one template body without wrapper prose. Report source conflicts to the caller separately.
