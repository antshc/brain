# Rationale: {{title|short name of the change}}
<!-- @: One page. Sentence-case headings, no boilerplate. Replace every placeholder with content. -->

## Problem

{{problem|One paragraph. What we are trying to do, and what about the existing system or constraints makes the shape non-obvious. Name constraints the design honors: existing types to interop with, callers that cannot break, invariants that cross the boundary.}}

## Usage (caller's view)
<!-- @: Written first; the Shape and the sketch derive from it. On divergence, reconcile the sketch to the usage. -->

{{usage|README or quickstart the consumer reads, plus two or three realistic call sites in their own code: what they import, what they call, what comes back.}}

## Shape
<!-- @: Name load-bearing decisions; cite the principle by heading, e.g. `per Boundary discipline`; do not restate it. -->

{{shape|The recommended architecture. Data structures first, then how data flows through the signatures. State which invariants are encoded in types, where validation lives, and what the system deliberately does not do. Judge interface depth: what complexity the public surface hides, what stays exposed to callers, and why the interface is no larger than needed.}}

<!-- @: Architect Arena synthesis only: insert "## Synthesis decision" here with base candidate, adopted grafts, rejected ideas and run details. Omit in standalone Sketch and Arena candidate rationale. -->

## Tradeoffs accepted

- {{tradeoff|"we accept X in exchange for Y." Name anything a future reader might mistake for an oversight, including apparent premature optimization or premature simplification.}}

## Alternatives considered
<!-- @: Required. At least one concrete alternative shape. Judge each on interface depth, not implementation simplicity alone. -->

- {{alternative|Whole-shape alternative, the complexity it exposes to callers and hides, one line on why it lost. When constraints forced the answer, write "this was the only viable shape because ...". No flavors of the same shape.}}

## Contracts touched

- {{contract|One line per touched kind — API, Database, Resource, other, GUI — naming each resource or surface, e.g. "API: `GET /api/v2/orders`; GUI: Order details dialog". Write "None" when no contract changes.}}

## Open questions and risks

- {{question|Phrased as a question, so the human's answer is the resolution. Include unresolved technical questions, risks, and conflicts with ADRs or Concepts with the reason for deviating.}}

## Next implementation step

{{nextStep|One sentence: the first thing to build against the sketch.}}
