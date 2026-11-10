# Sketch

Single-pass sketch of one change: usage, types, signatures, module map, rationale. Skip `design/design.md`, arena, how/why grounding, evidence routing, and checkpoint. Write only artifacts; write no production code and edit no repo source.

## Inputs

- **Task**: the change to sketch; verbatim request, story, spec, or a `deep-modules/comparison.md` recommendation. Required.
- [**Scope**]: repo paths or subsystems the change touches. Derive from Task and Repo docs when missing.

## Constraints

- **MUST** write usage before types; on divergence, reconcile the sketch to the usage. Usage cannot be written → record the missing information as an open question.
- **MUST** follow Repo docs rules in `SKILL.md`.
- **MUST** ground in existing code before sketching against it. Unreadable touched system → report "Sketch incomplete" with missing evidence; never invent its shape.
- **MUST** write artifacts only under the artifact root, per Artifact location in `SKILL.md`.

## Workflow

1. Read Repo docs. Done when each present doc is read or none exist.
2. Ground in the touched system: entry points, callers, types the change interacts with; for wide lookups, form an Explore request using the `research` contract and send it verbatim to `hunter`. If Hunter is unavailable, record the blocked lookup and continue independent work. Skip for greenfield. Done when you can state existing types to interop with, callers that cannot break, and boundary invariants.
3. Write the usage: README-style quickstart plus two or three realistic call sites in the consumer's code. Done when each call site shows imports, calls, and results.
4. Sketch types and signatures per Artifact layout in `SKILL.md`, applying the discipline bullets in `arena/runner-prompt.md`; ignore its candidate and orchestrator framing. Done when data traces from input to output through types and signatures alone and every call site type-checks against the sketch.
5. Screen against `design/design-red-flags.md`; revise each hit or record it as an open question. Done when every red flag is checked.
6. Write `rationale.md` from `design/rationale-template.md`; leave Synthesis decision empty. Done when no placeholder remains and Alternatives considered names at least one whole-shape alternative.
7. Report per Output. Done when Completion criteria hold.

## Output

- Artifacts: `synthesis/sketch/`, `synthesis/module-map.md`, `synthesis/rationale.md` under the artifact root.
- Final message: absolute artifact paths, usage excerpt, module map, open questions. Then stop.
- Later request to review, implement, or hand off → resume `design/design.md` at Phase C, E, or D.

## Completion criteria

- Usage is written and every call site resolves against the sketch.
- Every public signature has a `not implemented` body and a doc comment stating intent and invariants.
- `synthesis/rationale.md` follows the template.
- Every red flag hit is revised or recorded as an open question.
- No file outside the artifact root changed.
