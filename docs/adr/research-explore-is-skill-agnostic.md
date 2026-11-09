# Research Explore route is skill-agnostic

The `research` skill's Explore route runs inside a caller-spawned subagent and owns target resolution, contract material, tool selection, and the read-only contract, carrying no knowledge of what it is asked to run. The caller owns delegation: it reads the `research` skill's `Explore request` section, forms the work (a question, a prompt instruction of its own, or a skill name), depth, target, output shape, and the one output artifact the subagent may write, decides one or parallel subagents, and spawns each with the request verbatim, instructing it to run the `research` skill's Explore route. With Research unavailable, the caller spawns the explore agent with the same request. `research` codebase inspection spawns Explore subagents for its lookups; `design-review` reaches it by running `research`.

Agnosticism covers the caller's `@work` only. Tool selection loads the `graphify` skill for graph queries and the local NuGet tactic for restored package inspection, so their specific rules apply without changing caller work.

## Considered Options

- **Keep the engine as a separate `explore-codebase` skill** (previous decision) — rejected: two search entry points split triggers ('where is' vs 'research X'), and callers had to pick between them; `research` is now the single entry point and the engine is its Explore route.
- **Name the callable skills inside the Explore route** — rejected: the engine then has to be edited every time a skill becomes delegable, and the list is a second, stale index of skills the roster already carries.
- **Keep the former `research-system` skill invoking the Explore route for every lookup** — rejected: the engine ran inside its own passenger, and a direct invocation and a delegated one took different paths through the same skill.
- **The Explore route spawns its own subagents** (previous decision) — rejected: the skill ran in the caller's context only to brief a subagent that could not read it, so every brief restated the routing rules; the caller, which knows its tracks and dependencies, could not shape the split; and a skill-less environment had no fallback.
- **Keep the read-only contract absolute and let each caller state its own exception** — rejected: every skill that writes a document would need its own carve-out sentence.
- **Keep tool skills out of the Explore route and inline their CLI calls** — rejected: repo-local tool rules (graph health preflight, corpus, degraded mode) never load, and the inlined commands drift from the tool skill.

## Consequences

- Target resolution, the codebase index, and tool selection stay in one place — the subagent loads them from the skill instead of a caller brief.
- Each caller states its delegation shape (single, parallel, sequential) and consolidation; callers with several tracks (`define-concept`) hold that procedure once in their own skill.
- The read-only contract carries one generic exception, the caller's `@outputArtifact`, plus a per-user `rg` install when missing — a tool prerequisite outside every repository.
- The explore-agent fallback lacks the skill's routing rules; the caller accepts weaker target resolution there.
- The Explore route routes Graphify through its tool skill and NuGet inspection through a bundled tactic; adding a delegable work skill still needs no edit here.
