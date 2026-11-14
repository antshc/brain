# Research owns direct investigation; callers own Hunter delegation

Research owns route selection, local target resolution, contract-first search, Graphify, NuGet, evidence collection, verification and synthesis. Each route executes in the invoking agent without subagents. Hunter is a read-only wrapper that loads Research and the supplied route, or lets Research infer it. All routes are available; only selected and triggered resources load.

Callers delegate research by spawning Hunter with a complete question, route when known, target/ref and return shape, instructing it to load Research. Loading Research directly runs in the current agent and never triggers Hunter. Existing review/proof workers invoke Research directly for their own evidence. Independent questions may have separate Hunters only when the caller chooses that decomposition.

How explains current behavior directly. The Explainer role and prompt are removed; explanation and diagram guidance live in How/report. Why searches its seven evidence categories and synthesizes in the same agent while preserving source coverage, null results and confidence tiers.

Repository evidence uses local checkouts and resolved package caches only. Missing checkout/ref is a blocker; remote documentation and PR discussion never replace missing implementation evidence. Graph coverage uses main checkouts; source evidence stays in the requested worktree. Preserve read-only query, cache and tooling exceptions from Research.

Callers own exact report paths and bases. Hunter returns complete reports inline for the caller to save; only an explicitly assigned evidence artifact is writable. Direct Research may save its exact caller-selected final report. No default report directory or filename.

## Alternatives considered

- Caller-selected routes only: precise but duplicates routing knowledge; retain optional explicit routes plus automatic selection.
- Multiple Hunters coordinated by the caller: useful for independent questions; optional caller behavior, never internal Research fan-out.
- Research-owned evidence and explanation agents: rejected because Hunter forbids nested agents and direct execution should work without delegation.

Hunter omits the tool allowlist so available web/cloud/MCP capabilities remain accessible. This is [documented custom-agent behavior](https://docs.github.com/en/copilot/reference/custom-agents-configuration); Research’s read-only/no-subagent rules still constrain use. Missing tools/access remain explicit evidence gaps.
