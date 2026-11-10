# Sketch

Draft one sketch of the code for one change: usage, types, signatures, module boundaries, rationale. Write only the Output artifacts; write no production code and edit no repo source.

## Inputs

- **Task** — the change to sketch; verbatim request, story, spec, or resolved decisions. Required.
- [**Scope**] — repo paths or subsystems the change touches. Derive from Task and Repo docs when missing.

## Constraints

- **MUST** write the usage before the types; on divergence, reconcile the sketch to the usage. Rationale: the caller's experience is the spec. If the usage cannot be written, report the missing information as an open question.
- **MUST** conform to accepted ADRs and Concepts; name with glossary terms, no synonyms; place modules per the documented architecture. Record any deviation and its reason under Open questions and risks.
- **MUST** write artifacts only under `<repo-root>/tmp/sketch-<slug>/`; `<slug>` is a kebab-case name of the Task. Never write to the session folder or system `/tmp`.
- **MUST** ground in existing code before sketching against it. If a touched system cannot be read, report "incomplete" with the missing evidence; do not invent its shape.

## Workflow

1. Read Repo docs: architecture, relevant ADRs and Concepts, glossary; skip absent ones. *Done when* each present doc is read or none exist.
2. Ground in the touched system. Read the entry points, callers, and types the change interacts with; for wide lookups, form an Explore request using the `research` contract and send it verbatim to `hunter`. If Hunter is unavailable, record the blocked lookup and continue independent work. Skip only for greenfield work. *Done when* you can state existing types to interop with, callers that cannot break, and invariants crossing the boundary.
3. Write the usage: README-style quickstart plus two or three realistic call sites in the consumer's code. *Done when* each call site shows imports, calls, and results.
4. Load principles: *run `principles` skill to load verbatim, from its indexed list, the engineering principles cited by name in Discipline*: Foundational thinking, Deep modules, Boundary discipline, Separate before serializing shared state, Encode lessons in structure, Make operations idempotent, Laziness protocol, Minimize reader load, Exhaust the design space. *Done when* each named principle file is read fully.
5. Sketch the types and signatures per Sketch format, applying Discipline. *Done when* a reader can trace data from input to output from types and signatures alone, and every usage call site type-checks against the sketch.
6. Screen the sketch against [references/red-flags.md](../references/red-flags.md); read it fully. Revise on every hit, or record the hit as an open question when it cannot be removed. *Done when* every red flag is checked.
7. Write the rationale from [references/rationale.template.md](../references/rationale.template.md); read it fully. *Done when* no placeholder or directive remains and Alternatives considered names at least one concrete alternative shape.
8. Report per Output. *Done when* Completion criteria hold.

## Sketch format

- Order: usage, module map, types and signatures.
- Small change: one file with new types and signatures.
- Larger work: `module-map.md` listing each module with its single responsibility, owned state, and public surface; one sketch file per module.
- Bodies: raise the language's idiomatic `not implemented` error. Pseudocode comments (`// TODO` or the language's equivalent) mark tricky logic only.
- Doc comments state intent and invariants on every public type and function.
- Language: the repo's primary language for the touched modules; for greenfield, the language the Task names.

## Discipline

Principles are cited by name, loaded in step 4.

- **Data structures first.** Get the core types right and the code follows. Trace each dominant access pattern through the structure; "we'll add a map, index, or cache later" means the structure is wrong, per *Foundational thinking*.
- **Deep interface.** Compare the capability hidden behind the public surface to the size of that surface. Prefer a simple interface that pulls complexity into the callee, even when the implementation becomes less simple, per *Deep modules*. Keep transport and wire types off the public API, per *Boundary discipline*.
- **Shared state.** When two actors might both write, ask what happens. If the answer is not "nothing", default to per-actor state merged at the read boundary, per *Separate before serializing shared state*.
- **Types over checks.** Hard-to-misuse types beat runtime checks beat prose comments, per *Encode lessons in structure*.
- **Edge validation.** Validate at boundaries, trust types inside; business logic as pure functions; thin shell, per *Boundary discipline*.
- **One source of truth.** Derive instead of sync.
- **Idempotent transitions.** Where state changes, ask what happens when the operation runs twice or crashes halfway, per *Make operations idempotent*.
- **Short call chains.** When tracing a flow needs more than three files, flatten the hierarchy, per *Laziness protocol* and *Minimize reader load*.
- **Shape alternatives.** Consider whole-shape alternatives, not point fixes, per *Exhaust the design space*; put the rejected ones in the rationale.
- **Agent reader.** Assume the next contributor is an agent that sees only files it opened, copies the nearest example, and takes the shortest path that compiles. Prefer the shape where a change that looks right from one file is right for the whole repo.

## Output

- Artifacts under `<repo-root>/tmp/sketch-<slug>/`: sketch file or files (plus `module-map.md` for larger work), and `rationale.md` containing the usage.
- Final message: absolute artifact paths, the usage excerpt, the module map when present, and the open questions.
- Incomplete: report "Sketch incomplete" with the missing evidence; never guess.

## Completion criteria

- Usage is written and every call site resolves against the sketch.
- Every public signature meets Sketch format bodies and doc comments.
- `rationale.md` follows the template.
- Every red flag hit is revised or recorded as an open question.
- No file outside `<repo-root>/tmp/sketch-<slug>/` was changed.
