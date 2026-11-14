# Design It Twice

Parallel interface-design procedure for the `design deep-module` route. First idea is rarely the best (Ousterhout). Use the vocabulary in `references/deep-modules.md`. Adapted from mattpocock/skills `codebase-design` (MIT).

Write under the exact caller-assigned option root; standalone uses `<artifact-root>/deep-modules/`. Read shared sketch/rationale resources from the Design router before option generation.

## Frame

Target: the module named by the user, or the module whose contract a verified Challenge this finding breaks.

Write `problem.md`:

- Constraints any new interface must satisfy; for a contract finding, the finding's command, output, and the intent it breaks are hard constraints.
- Each dependency and its category per *Dependency categories*.
- A rough illustrative code sketch making the constraints concrete; not a proposal.

Standalone → show `problem.md` to the user, then continue immediately without waiting.

## Spawn designers

*Load and follow the `subagents` skill to dispatch independent workers using role-based models and isolated outputs* using **Dispatch** with 3+ designer briefs and the ordered `architect runners` pool. Each MUST produce a **radically different** interface.

Use skill-capable `general-purpose` designers. Pass Design’s shared Principles rule with the task, route, phase and mandatory names; each designer loads in its own context before shaping an interface. Give each a separate technical brief: file paths, coupling details, dependency categories, what sits behind the seam, absolute paths of `design/references/deep-modules.md` and the repo glossary, and its isolated package path `option-<n>/`. Each designer follows the Sketch playbook in Candidate context with supplied grounding; no Arena or implementation. Assign one constraint per designer:

1. Minimize the interface: 1–3 entry points; maximize leverage per entry point.
2. Maximize flexibility: support many use cases and extension.
3. Optimize for the most common caller: make the default case trivial.
4. (when cross-seam dependencies exist) Design around ports & adapters.

Each option uses Code Sketch: write credible caller usage first, then language-native source files with signatures, invariants and nonimplemented bodies under `sketch/`, `module-map.md`, and its own Markdown `rationale.md`. Explain interface/seam, hidden complexity, dependency strategy/adapters, errors/ordering, trade-offs, constraints and unknowns; link its source sketches. One shared rationale or Markdown-only interface does not satisfy the contract. Label candidate trade-offs as proposed; recommendation is not user acceptance. Done when each package satisfies the shared sketch contract.

## Compare

Write `comparison.md`: links to each option package/rationale in sequence, then a prose comparison by **depth**, **locality**, and **seam placement**. End with an opinionated recommendation; propose a hybrid when elements combine well. No neutral menus.

Contract finding → also rerun the finding's command against a probe of the recommended interface when a safe runnable target exists; record the result in `comparison.md`.

## Hand back

- Standalone → present `comparison.md` contents and the recommendation; stop unless a separate implementation handoff was requested.
- Contract finding → return the recommended interface as the finding's proposed correction to the step that raised it, citing `comparison.md`.

- Wayfinder → return candidate paths/revision to Contract design Options; retain worktree without merging. Only after user Choice does Wayfinder merge selected sketches/rationale and considered-option notes.
