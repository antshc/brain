# Research is a router; only Research spawns its route agents

Research routes each independent question to Explore, How, Why, Cloud, or Web, loads that route's playbook, and spawns the route's agents: `hunty` (How evidence, lookups, Graphify and NuGet tactics), `explainy` (How explanation), `whyy` and `composy` (Why investigation and synthesis), `cloudy` (AWS/Azure), and `weby` (other external sources). Each agent is a prompt file under `research/agents/`, filled by the router and run in a `general-purpose` worker with the role's model from the `subagents` skill. Agents never spawn subagents or load `research`; they return gaps to the router. Callers load Research in their own session, never inside a wrapper subagent, and never spawn route agents directly. A pure lookup uses Explore: one `hunty` pass per lookup, verdicts returned inline to the calling agent.

The request text is the only input: Research discovers questions, route, Why depth, targets, framing, and destination from it. Reports save to the agent session workspace (`files/research/`) with links presented to the user, or to a location the request names; pure lookups return inline. `hunty` uses local checkouts only, Graphify for covered relationships, and the NuGet tactic for restored package-cache evidence; missing local checkouts or refs are blockers, never filled by remote lookup, clone, or fetch.

## Alternatives considered

- Registering `hunter` as a plugin agent that many skills spawned directly. Callers inside workers spawned it again, nesting subagents, and every caller duplicated the Explore request contract.
- Folding lookups into How. Callers such as Design Grill need raw cited verdicts without an explanation or report file; a separate Explore route returns exactly that.
- Generic `subagents` Dispatch for route workers. Dispatch hid which prompt and model each route used; per-route prompt files make the spawn explicit while `subagents` keeps only model selection.
- Registering each route agent. Prompt files keep the agents private to Research, so other skills cannot bypass routing.
