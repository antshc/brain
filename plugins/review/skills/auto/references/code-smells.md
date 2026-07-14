# Code Smell Baseline (Fowler)

Use this checklist to evaluate the changes. Ground
every conclusion using the LSP analysis and in specific code evidence, not on the patch alone.

A fixed set of Martin Fowler code smells (_Refactoring_, ch. 3) used by the Standards
axis. Match each against the diff. Two rules bind this baseline:

- **Always a judgement call.** Each smell is a labelled heuristic ("possible Feature Envy"),
  never a hard violation. Report it as a suggestion, not a defect.
- **Skip what tooling enforces.** This repo runs `.editorconfig`, StyleCop analyzers, and
  SonarQube in CI. Do NOT raise style-only or analyzer-covered concerns. This baseline is
  about design smells, not formatting.

Each smell reads *what it is* → *how to fix*:

- **Mysterious Name** — a function, variable, or type whose name doesn't reveal what it does or holds. → rename it; if no honest name comes, the design's murky.
- **Duplicated Code** — the same logic shape appears in more than one hunk or file in the change. → extract the shared shape, call it from both.
- **Feature Envy** — a method that reaches into another object's data more than its own. → move the method onto the data it envies.
- **Data Clumps** — the same few fields or params keep travelling together (a type wanting to be born). → bundle them into one type, pass that.
- **Primitive Obsession** — a primitive or string standing in for a domain concept that deserves its own type. → give the concept its own small type.
- **Repeated Switches** — the same `switch`/`if`-cascade on the same type recurs across the change. → replace with polymorphism, or one map both sites share.
- **Shotgun Surgery** — one logical change forces scattered edits across many files in the diff. → gather what changes together into one module.
- **Divergent Change** — one file or module is edited for several unrelated reasons. → split so each module changes for one reason.
- **Speculative Generality** — abstraction, parameters, or hooks added for needs the spec doesn't have. → delete it; inline back until a real need shows.
- **Message Chains** — long `a.b().c().d()` navigation the caller shouldn't depend on. → hide the walk behind one method on the first object.
- **Middle Man** — a class or function that mostly just delegates onward. → cut it, call the real target direct.
- **Refused Bequest** — a subclass or implementer that ignores or overrides most of what it inherits. → drop the inheritance, use composition.

## LSP focus for this axis

Build on the **`LSP baseline`** section of your prompt. Use LSP **relationships**, not contract diffs, following the `LSP Progressive Depth Code Analysis` framework from `/lsp-depth-guidance`:

- Start from the baseline's **Fan-out** column (wide spread hints at Shotgun Surgery, Divergent Change, Feature Envy).
- **Feature Envy / Message Chains** — run call hierarchy on changed methods to see whose data they reach through.
- **Shotgun Surgery / wide fan-out** — run find-references across files to measure how far a single change ripples.
- **Data Clumps / Primitive Obsession** — inspect type usage and parameter groups repeated across the changed symbols.
- **Divergent Change** — check whether one changed file gathers edits for several unrelated reasons.

Escalate to Level 2/3 only where a structural smell is plausible from the baseline; otherwise stay at Level 1.

> Shared review rules (evidence, scope, deduplication) apply to this axis. See `<skill-directory>/references/review-rules.md`.