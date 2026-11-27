# Sketch

One canonical code-sketch procedure reused standalone, for Deep Module options, Wayfinder and inside Architect local comparison or Arena. Usage first; types, signatures, module map, and rationale follow. No production code or source edits.

Read [Code-sketch contract](../references/sketch-contract.md) in full before starting. It owns output shape, local discipline, red flags and acceptance criteria; Design owns shared Principles loading. No parallel copy of those rules.

## Contexts

| Context | Inputs | Output location | Extra work |
|---|---|---|---|
| **Standalone** (`design sketch`) | Verbatim task/story/spec or resolved decisions; optional scope | `<artifact-root>/synthesis/` | Ground in code; one sketch; report and stop |
| **Wayfinder** | Topic question and supplied grounding, pinned worktree; runs in Wayfinder's session | Exact caller-assigned package root | Return package to Wayfinder for prototype approval before local integration |
| **Candidate** (Architect local comparison, Arena or Deep Module option) | Task, supplied grounding/repo docs, isolated read-only working tree, assigned candidate path | Exact caller-assigned candidate path, including `<artifact-root>/local/candidate-<n>/` or Arena/revision paths | Return to caller; no Arena, implementation or independent user handoff |

The artifact root is `<repo-root>/tmp/design-<slug>/` per `SKILL.md`. Explicit caller roots override temporary defaults. In every context the package contains `rationale.md`, `module-map.md`, and `sketch/` with language-native source files. Candidate outputs must be independent and structurally distinct when Arena uses multiple runners.

## Workflow

1. **Repository contract.** Read the architecture, relevant ADRs/Concepts, and glossary. Candidate context reuses the supplied files, reading any not already loaded. Record deviations as open questions.
2. **Ground.** Standalone: inspect affected entry points, callers, types, and boundary invariants. For wide lookups, spawn the wf plugin's `codebase` agent per lookup with the bounded question, target checkout/ref, and thoroughness; it returns cited findings inline. Spawn it per the `research` skill's `codebase` spawn rule, including the model and effort from the `subagents` skill's `codebase` role. Blocked lookup → record it and continue independent work. Skip only for genuinely greenfield work. Wayfinder: use supplied grounding and send wide gaps to `codebase` the same way. Candidate (runs in Architect local comparison, an Arena or Design It Twice worker): use supplied grounding, inspect only missing local evidence directly, and report wide gaps as unknowns; never load `research` or spawn subagents. Unreadable touched code → report 'Sketch incomplete'; never invent its shape.
3. **Usage.** Write quickstart and two or three concrete consumer call sites before designing the types. Explicitly state incompatible callers and invariants.
4. **Shape.** Apply Design’s shared Principles rule for this phase; draft module map, types, signatures, and `not implemented` bodies. Confirm every call site resolves under the [Code-sketch contract](../references/sketch-contract.md).
5. **Screen.** Load the shared red flags and correct every hit or record an open question.
6. **Rationale.** Use the shared rationale template, with concrete whole-shape alternatives and no placeholders. Candidate/Wayfinder: leave choice to caller; Deep Module writes per-option proposed rationale. Standalone: omit synthesis decision.
7. **Finish.** Candidate/Wayfinder: return the assigned package to caller and stop; no commits, merges or cleanup of caller-owned worktrees. Standalone: report absolute artifact paths, usage excerpt, module map, and open questions, then stop.

## Follow-up

Later review or implementation request can resume `design architect` at its Review, Implement, or Hand-off phase using the standalone `synthesis/` package. Never silently implement as part of `design sketch`.
