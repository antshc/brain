# explore-codebase is skill-agnostic

`explore-codebase` runs inside a caller-spawned subagent and owns target resolution, contract material, tool selection, and the read-only contract, carrying no knowledge of what it is asked to run. The caller owns delegation: it reads the skill's `Request` section, forms the work (a question, a prompt instruction of its own, or a skill name), depth, target, output shape, and the one output artifact the subagent may write, decides one or parallel subagents, and spawns each with the request verbatim, instructing it to run `explore-codebase`. With the skill unavailable, the caller spawns the explore agent with the same request. `research-system` names no lookup engine of its own — `research` and `technical-design` reach it by naming it as the work their `explore-codebase` subagent runs.

## Considered Options

- **Name the callable skills inside `explore-codebase`** — rejected: the engine then has to be edited every time a skill becomes delegable, and the list is a second, stale index of skills the roster already carries.
- **Keep `research-system` invoking `explore-codebase` for every lookup** — rejected: the engine ran inside its own passenger, and a direct invocation and a delegated one took different paths through the same skill.
- **`explore-codebase` spawns its own subagents** (previous decision) — rejected: the skill ran in the caller's context only to brief a subagent that could not read it, so every brief restated the routing rules; the caller, which knows its tracks and dependencies, could not shape the split; and a skill-less environment had no fallback.
- **Keep the read-only contract absolute and let each caller state its own exception** — rejected: every skill that writes a document would need its own carve-out sentence.

## Consequences

- Target resolution, the codebase index, and tool selection stay in one place — the subagent loads them from the skill instead of a caller brief.
- Each caller states its delegation shape (single, parallel, sequential) and consolidation; callers with several tracks (`define-concept`) hold that procedure once in their own skill.
- The read-only contract carries one generic exception: the caller's `@outputArtifact`.
- The explore-agent fallback lacks the skill's routing rules; the caller accepts weaker target resolution there.
