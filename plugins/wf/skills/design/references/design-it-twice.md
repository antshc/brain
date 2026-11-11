# Design It Twice

Parallel interface-design procedure for the `design deep-module` route. First idea is rarely the best (Ousterhout). Use the vocabulary in `references/deep-modules.md`. Adapted from mattpocock/skills `codebase-design` (MIT).

Write every output under `<artifact-root>/deep-modules/`.

## Frame

Target: the module named by the user, or the module whose contract a verified Challenge this finding breaks.

Write `problem.md`:

- Constraints any new interface must satisfy; for a contract finding, the finding's command, output, and the intent it breaks are hard constraints.
- Each dependency and its category per *Dependency categories*.
- A rough illustrative code sketch making the constraints concrete; not a proposal.

Standalone → show `problem.md` to the user, then continue immediately without waiting.

## Spawn designers

*Run `subagents` skill to dispatch independent workers with role-based models* using **Dispatch** with 3+ designer briefs and the ordered `architect runners` pool. Each MUST produce a **radically different** interface.

Give each a separate technical brief: file paths, coupling details, dependency categories, what sits behind the seam, absolute paths of `design/references/deep-modules.md` and the repo glossary, and its output path `option-<n>.md`. Assign one constraint per designer:

1. Minimize the interface: 1–3 entry points; maximize leverage per entry point.
2. Maximize flexibility: support many use cases and extension.
3. Optimize for the most common caller: make the default case trivial.
4. (when cross-seam dependencies exist) Design around ports & adapters.

Each `option-<n>.md` contains:

1. Interface: types, methods, params, invariants, ordering, error modes.
2. Usage example from a real caller.
3. What the implementation hides behind the seam.
4. Dependency strategy and adapters.
5. Trade-offs: where leverage is high, where thin.

## Compare

Write `comparison.md`: each option in sequence, then a prose comparison by **depth**, **locality**, and **seam placement**. End with an opinionated recommendation; propose a hybrid when elements combine well. No neutral menus.

Contract finding → also rerun the finding's command against a probe of the recommended interface when a safe runnable target exists; record the result in `comparison.md`.

## Hand back

- Standalone → present `comparison.md` contents and the recommendation; stop unless the user asked to sketch or implement.
- Contract finding → return the recommended interface as the finding's proposed correction to the step that raised it, citing `comparison.md`.
