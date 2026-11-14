# Sketch

One canonical code-sketch procedure reused standalone, for Deep Module options, Wayfinder and inside the Architect Arena. Usage first; types, signatures, module map, and rationale follow. No production code or source edits.

Read [Code-sketch contract](../references/sketch-contract.md) in full before starting. It owns output shape, local discipline, red flags and acceptance criteria; Design owns shared Principles loading. No parallel copy of those rules.

## Contexts

| Context | Inputs | Output location | Extra work |
| --- | --- | --- | --- |
| **Standalone** (`design sketch`) | Verbatim task/story/spec or resolved decisions; optional scope | `<artifact-root>/synthesis/` | Ground in code; one sketch; report and stop |
| **Wayfinder** | Ticket question and supplied grounding, `@helperDispatch`, pinned worktree | Exact caller-assigned package root | Return package to Wayfinder for prototype approval before local integration |
| **Candidate** (Architect Arena or Deep Module option) | Task, supplied grounding/repo docs, isolated read-only working tree, assigned candidate path | `<artifact-root>/candidate-<n>/` (or Arena revision candidate) | Return to caller; no Arena, implementation or independent user handoff |

The artifact root is `<repo-root>/tmp/design-<slug>/` per `SKILL.md`. Explicit caller roots override temporary defaults. In every context the package contains `rationale.md`, `module-map.md`, and `sketch/` with language-native source files. Candidate outputs must be independent and structurally distinct when Arena uses multiple runners.

## Workflow

1. **Repository contract.** Read the architecture, relevant ADRs/Concepts, and glossary. Candidate context reuses the supplied files, reading any not already loaded. Record deviations as open questions.
2. **Ground.** Standalone: inspect affected entry points, callers, types, and boundary invariants. For wide lookups use Research Explore, forwarding `@helperDispatch`; with it directly spawn read-only general-purpose evidence workers, otherwise send the request to Hunter; if unavailable, record the blocked lookup and continue independent work. Skip only for genuinely greenfield work. Candidate/Wayfinder: use supplied grounding and inspect only missing local evidence. Unreadable touched code → report 'Sketch incomplete'; never invent its shape.
3. **Usage.** Write quickstart and two or three concrete consumer call sites before designing the types. Explicitly state incompatible callers and invariants.
4. **Shape.** Apply Design’s shared Principles rule for this phase; draft module map, types, signatures, and `not implemented` bodies. Confirm every call site resolves. Follow [Code-sketch contract](../references/sketch-contract.md), not an Arena-specific copy of its rules.
5. **Screen.** Load the shared red flags and correct every hit or record an open question.
6. **Rationale.** Use the shared rationale template, with concrete whole-shape alternatives and no placeholders. Candidate/Wayfinder: leave choice to caller; Deep Module writes per-option proposed rationale. Standalone: omit synthesis decision.
7. **Finish.** Candidate/Wayfinder: return the assigned package to caller and stop; no commits, merges or cleanup of caller-owned worktrees. Standalone: report absolute artifact paths, usage excerpt, module map, and open questions, then stop.

## Follow-up

Later review or implementation request can resume `design architect` at its Review, Implement, or Hand-off phase using the standalone `synthesis/` package. Never silently implement as part of `design sketch`.
