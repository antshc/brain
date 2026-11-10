# Code-sketch contract

Canonical code-shape instructions for both `design sketch` and every `design architect` Arena candidate. The candidate runner and standalone route MUST use this same procedure, not copy its discipline into another prompt.

## Output contract

- Write a README-style consumer usage first, with two or three realistic call sites showing imports, calls, and results. Reconcile types to the usage, never the opposite. Unable to write credible usage → open question.
- Write real source files under the assigned `sketch/`, in the touched modules' primary language (or the task's language for greenfield). Never place all code in one Markdown file.
- Small changes use one source file; larger ones use a file per module or concern. `module-map.md` names each new, modified, or deleted real repo-relative target path, mapped to its sketch file, responsibility, owned state, and public surface.
- Every public type/function has a doc comment describing intent and invariants. Bodies raise the language's idiomatic `not implemented` error. Pseudocode comments describe tricky logic only; no working production code.
- Use [Rationale template](rationale.template.md) for `rationale.md`: problem, usage, shape, tradeoffs, whole-shape alternatives, open questions, next step. The Architect Arena synthesis additionally records its synthesis decision; standalone and candidate outputs omit that section.
- Screen every sketch using [Design red flags](red-flags.md), revising hits or recording unresolved ones. In a multi-candidate Arena screen each candidate before synthesis.

## Discipline

Run `principles` and read its indexed principle files named below fully before sketching. Apply them rather than copying their bodies here.

- **Foundational thinking:** choose data structures first; trace dominant access patterns and do not defer essential indexes/maps to 'later'.
- **Deep modules:** expose a small, capable interface and hide complexity in the callee. Keep transport/wire types private per **Boundary discipline**.
- **Separate before serializing shared state:** consider per-actor state merged at the read boundary when multiple actors write.
- **Encode lessons in structure:** prefer hard-to-misuse types over runtime checks, over comments.
- **Boundary discipline:** validate at entry points, use trusted domain types inside, pure business logic, thin shell.
- **Make operations idempotent:** account for repeat execution and crashes partway through state transitions.
- **Laziness protocol** and **Minimize reader load:** avoid long call chains; flatten when tracing a flow needs more than three files.
- **Exhaust the design space:** reject at least one concrete whole-shape alternative, judged by interface depth, not a variation of the same shape.
- **One source of truth:** derive rather than synchronize duplicated state or lists.
- **Agent reader:** a future agent reads few files and copies the nearest example. Make the locally obvious change safe for the whole repository; hide internals and provide one supported operation path.

## Acceptance

- Every usage call site resolves against the types and signatures.
- A reader traces input to output through signatures without executable bodies.
- Rationale has no unfilled placeholders; all red flags were screened.
- No production code was changed by the sketch procedure.
