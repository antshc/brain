# Code-smells review

Follow the parent's shared review contract. Match the complete change against the baseline below. Return `AXIS: code-smells`.

## Code smell baseline (Fowler)

A fixed set of Martin Fowler code smells (*Refactoring*, ch. 3). Match each against changed code and relevant existing implementations.

- **Judgement calls**: treat smells as labelled heuristics internally, never hard violations. Report suggestions, not defects.
- **Skip what tooling enforces**: do not raise style-only or analyzer-covered concerns; review design, not formatting.

Each smell states the pattern and a candidate refactor. Preserve intentional boundaries; recommend a refactor only when it reduces demonstrated maintenance cost without adding stronger coupling.

- **Mysterious Name**: a function, variable, or type whose name does not reveal what it does or holds. Rename it; if no honest name fits, reconsider the design.
- **Duplicated Code**: changed code repeats logic for the same responsibility in changed or existing code. Extract the shared logic when both should evolve together; preserve coincidental similarity.
- **Feature Envy**: a method depends excessively on another owner's internals, not merely many outgoing calls. Move the behavior to that owner when it restores encapsulation.
- **Data Clumps**: the same fields or parameters keep travelling together. Bundle them into one type.
- **Primitive Obsession**: a primitive or string stands in for a domain concept that deserves its own type. Give the concept a small type.
- **Repeated Switches**: changed code adds or extends type-based dispatch repeated in changed or existing code, requiring coordinated updates. Consolidate dispatch in a shared map or existing polymorphic boundary when simpler than the switches.
- **Shotgun Surgery**: one concept requires coordinated edits at independent maintenance points, not merely many changed files. Gather the scattered responsibility behind one boundary.
- **Divergent Change**: one module mixes distinct responsibilities with independent reasons to change, not merely several edits in one PR. Separate those responsibilities.
- **Speculative Generality**: abstractions, parameters, or hooks are added for needs the spec does not have. Delete or inline them until a real need appears.
- **Message Chains**: long `a.b().c().d()` navigation the caller should not depend on. Hide the walk behind one method on the first object.
- **Middle Man**: a class or function mostly delegates without a useful boundary or policy. Inline it when direct calls preserve intended isolation.
- **Refused Bequest**: a subclass or implementer ignores or overrides most of what it inherits. Replace inheritance with composition.

## Deep modules

**Shallow Module**: a boundary imposes caller burden without hiding meaningful complexity, not merely a short implementation. Evidence may include redundant entry points, pass-through layers, leaked resource ownership, or exposed implementation dependencies. Narrow the surface, merge twins, internalize obligations, or remove the layer when the boundary serves no useful purpose.

## Investigation guidance

Use the baseline to identify plausible design concerns, then select evidence that supports or rules them out. Inspect relevant implementations, callers, ownership, and maintenance points as needed. Counts, chain length, and superficial similarity alone are insufficient.

## Finding rules

- Report only smells introduced or materially worsened by the change. Existing code may establish the pattern; anchor the finding to the changed contribution.
- Emit only when code evidence shows a concrete maintenance cost and a proportionate, behavior-preserving refactor. Check intentional-boundary explanations before reporting; omit preference-only alternatives.
- Use the shared contract's JSON shape, five-finding limit, diff anchors, deduplication, and explicit failure result.

## Finding content

Supply the concrete design issue, demonstrated maintenance cost, and smallest behavior-preserving refactor to the shared conversation draft. Name exact symbols/code paths; keep smell names and heuristic classifications internal. Frame the refactor as a suggestion, not a proven defect; avoid speculative abstractions.
