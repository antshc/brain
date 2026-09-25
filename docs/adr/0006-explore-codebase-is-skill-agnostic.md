# explore-codebase is skill-agnostic

`explore-codebase` owns subagent delegation, target resolution, contract material, and tool selection, and carries no knowledge of what it is asked to run. It is the engine for any codebase exploration: the caller supplies a question, a prompt instruction of its own, or a skill name — plus its inputs verbatim and the one output artifact the subagent may write — and `explore-codebase` passes them through and returns the caller's own output shape unaltered. `inspect-system` consequently names no lookup engine of its own — `research` and `technical-design` reach it by naming it to `explore-codebase`.

## Considered Options

- **Name the callable skills inside `explore-codebase`** (status quo — `/probe-concept` "for a Concept evidence packet", `inspect-*` "for an as-built write-up") — rejected: the engine then has to be edited every time a skill becomes delegable, and the list is a second, stale index of skills the roster already carries.
- **Keep `inspect-system` invoking `/explore-codebase` for every lookup** — rejected: with `research` and `technical-design` already dispatching `inspect-system` through the engine, the engine ran inside its own passenger, and a direct invocation and a delegated one took different paths through the same skill.
- **Let each caller drive its own subagent for inspection work** — rejected: target resolution, the codebase index, and tool selection would be restated at every call site, which is the duplication the engine exists to remove.
- **Keep the read-only contract absolute and let each caller state its own exception** — rejected: every skill that writes a document would need its own carve-out sentence, and a subagent reading only the engine's brief would see a contract its task cannot satisfy.

## Consequences

- The read-only contract carries one generic exception: the output artifact the caller names.
- A caller dispatching an inspection now states three things — the question, the skill to run, and that skill's document as the permitted artifact.
- A caller with no matching skill reaches the same engine with a prompt instruction, instead of driving its own subagent.
