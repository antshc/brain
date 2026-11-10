# Sketch

One canonical code-sketch procedure reused standalone and inside the Architect Arena. Usage first; types, signatures, module map, and rationale follow. No production code or source edits.

Read [Code-sketch contract](../references/sketch-contract.md) in full before starting. It owns the output shape, principles, discipline, red flags, and acceptance criteria. No parallel copy of those rules.

## Contexts

| Context | Inputs | Output location | Extra work |
| --- | --- | --- | --- |
| **Standalone** (`design sketch`) | Verbatim task/story/spec or resolved decisions; optional scope | `<artifact-root>/synthesis/` | Ground in code; one sketch; report and stop |
| **Candidate** (called by `design architect` Arena) | Task, supplied grounding/repo docs, isolated read-only working tree, assigned candidate path | `<artifact-root>/candidate-<n>/` (or Arena revision candidate) | Do not run Arena, re-ground without need, or send user-facing output |

The artifact root is `<repo-root>/tmp/design-<slug>/` per `SKILL.md`. In both contexts the package contains `rationale.md`, `module-map.md`, and `sketch/` with language-native source files. Candidate outputs must be independent and structurally distinct when Arena uses multiple runners.

## Workflow

1. **Repository contract.** Read the architecture, relevant ADRs/Concepts, and glossary. Candidate context reuses the supplied files, reading any not already loaded. Record deviations as open questions.
2. **Ground.** Standalone: inspect affected entry points, callers, types, and boundary invariants. For wide lookups send a verbatim Research Explore request to Hunter; if unavailable, record the blocked lookup and continue independent work. Skip only for genuinely greenfield work. Candidate: use Phase A grounding and inspect only missing local evidence. Unreadable touched code → report 'Sketch incomplete'; never invent its shape.
3. **Usage.** Write quickstart and two or three concrete consumer call sites before designing the types. Explicitly state incompatible callers and invariants.
4. **Shape.** Read the named Principles required by the shared contract; draft module map, types, signatures, and `not implemented` bodies. Confirm every call site resolves. Follow [Code-sketch contract](../references/sketch-contract.md), not an Arena-specific copy of its rules.
5. **Screen.** Load the shared red flags and correct every hit or record an open question.
6. **Rationale.** Use the shared rationale template, with concrete whole-shape alternatives and no placeholders. Candidate: leave synthesis decision to Arena. Standalone: omit synthesis decision.
7. **Finish.** Candidate: return the assigned package to Arena and stop. Standalone: report absolute artifact paths, usage excerpt, module map, and open questions, then stop.

## Follow-up

Later review or implementation request can resume `design architect` at its Review, Implement, or Hand-off phase using the standalone `synthesis/` package. Never silently implement as part of `design sketch`.
