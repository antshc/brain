# Code-smells review

Follow the parent's shared review contract. Match the complete change against the baseline below, grounded in LSP analysis and specific code evidence, not the patch alone. Return `AXIS: code-smells`.

## Code smell baseline (Fowler)

A fixed set of Martin Fowler code smells (*Refactoring*, ch. 3). Match each against the diff.

- **Judgement calls**: treat smells as labelled heuristics internally, never hard violations. Report suggestions, not defects.
- **Skip what tooling enforces**: do not raise style-only or analyzer-covered concerns; review design, not formatting.

Each smell states the pattern and proposed fix:

- **Mysterious Name**: a function, variable, or type whose name does not reveal what it does or holds. Rename it; if no honest name fits, reconsider the design.
- **Duplicated Code**: the same logic shape appears in more than one hunk or file in the change. Extract the shared shape and call it from both.
- **Feature Envy**: a method reaches into another object's data more than its own. Move the method onto that data's owner.
- **Data Clumps**: the same fields or parameters keep travelling together. Bundle them into one type.
- **Primitive Obsession**: a primitive or string stands in for a domain concept that deserves its own type. Give the concept a small type.
- **Repeated Switches**: the same switch or if-cascade on the same type recurs across the change. Replace it with polymorphism or one shared map.
- **Shotgun Surgery**: one logical change forces scattered edits across many files. Gather what changes together into one module.
- **Divergent Change**: one file or module is edited for several unrelated reasons. Split it so each module changes for one reason.
- **Speculative Generality**: abstractions, parameters, or hooks are added for needs the spec does not have. Delete or inline them until a real need appears.
- **Message Chains**: long `a.b().c().d()` navigation the caller should not depend on. Hide the walk behind one method on the first object.
- **Middle Man**: a class or function mostly delegates onward. Remove it and call the real target directly.
- **Refused Bequest**: a subclass or implementer ignores or overrides most of what it inherits. Replace inheritance with composition.

## Deep modules

**Shallow Module**: a public surface grows without matching depth: redundant near-twin entry points, thin pass-through wrappers, leaked stream/disposable ownership, classitis/dead surface, or upward/cross-module reach. Narrow the surface, merge twins, do the work internally, or remove the layer.

## LSP workflow

1. Enumerate changed symbols: types, methods, properties, fields, interfaces, records, constructors. Keep this shallow, then perform one reference sweep per symbol to measure fan-out across files and callers. Wide spread hints at Shotgun Surgery, Divergent Change, or Feature Envy; use it to select deeper checks.
2. Deepen where a smell is plausible:
   - **Feature Envy / Message Chains**: trace outgoing calls from changed methods to identify whose data they reach through and the navigation length.
   - **Shotgun Surgery / wide fan-out**: inspect the reference sweep across files to establish how far a single change ripples.
   - **Data Clumps / Primitive Obsession**: inspect types and documentation, then references to changed types and parameters for recurring field/parameter groups.
   - **Divergent Change**: list the document's symbols and inspect changed symbols for unrelated reasons to change.
   - **Shallow Module**: trigger on a new interface/public member, added parameters, widened return type (especially `Stream`, `IDisposable`, collections, internal types), or visibility widened to public. List symbols as a worklist; inspect each signature's surface cost; resolve implementations and outgoing calls for depth versus pass-through; inspect references for unused surface and caller-owned disposal/null checks; search workspace symbols for near-twins converging on the same private helper; resolve reached dependencies for upward or cross-feature concrete dependencies. Judge every worklist member. Flag nothing for a small surface with self-contained depth, no ownership leak, and clean boundaries.
3. Escalate call hierarchy and cross-file inspection only where the fan-out sweep suggests a structural smell. Otherwise retain the shallow relationship snapshot. Prefer representative samples; stop once the smell is confirmed or ruled out.

## Finding rules

- Emit only net-new actionable smells, including minor ones when their benefit is concrete.
- Use the shared contract's JSON shape, five-finding limit, diff anchors, deduplication, and explicit failure result.

## Comment format

Return each `REVIEW_COMMENT` as a posting-ready body: `concrete design issue → maintenance impact → smallest refactor`.

- One issue; name the exact symbols or code paths that demonstrate the pattern. Keep smell names and heuristic classifications internal.
- Explain the concrete cost to change, understand, or use the code in one sentence; frame the refactor as a suggestion, not a proven defect.
- Suggest the smallest refactor that reduces that cost while preserving behavior; avoid speculative abstractions.
- Start with the issue, without classification labels or prefixes (`suggest`, `suggestion`, `nit`, `bug`). Keep only essential context; remove praise, repetition, hedging, and background.