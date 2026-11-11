# Hunter owns the skill-agnostic Explore procedure

Hunter runs Explore for caller-supplied questions, prompt instructions, and named skills. It resolves targets, reads contracts, selects tools, enforces read-only rules, and returns evidence. The caller reads the Research skill's Explore request contract, forms the work and return shape, and dispatches Hunter with that request verbatim. If Hunter is unavailable, the caller reports the blocked evidence request and continues independent work.

Research routes current-system questions to How. How owns discovery, depth, evidence dispatch and reconciliation, explanation, and delivery; Hunter executes the Explorer prompt. The Explainer synthesizes verified findings and selects useful diagrams. Callers own artifact destinations and supply exact `@outputPath` values and `@outputBase` for relative paths; all Research routes return inline findings when no save is requested. Research has no default report directory, filename, or lens suffix. It returns pure lookup verdicts inline. Hunter uses local checkouts only, Graphify for covered relationships, and the NuGet tactic for resolved package-cache evidence. Missing local checkouts or refs are blockers; Hunter does not use remote repository tools, clone, or fetch to fill them. A caller may name the one output artifact Hunter is allowed to write.

## Alternatives considered

- Keeping Explore as a separate skill or Research worker route split ownership between the agent and skill. Callers had to instruct each worker to load that route.
- Listing callable skills inside Explore would require a second roster to keep current. The caller already knows which question, prompt, or skill it needs.
- Having Explore spawn its own workers would move the split away from the caller that knows the independent tracks and dependencies.
- Inlining Graphify commands would bypass the graph health, corpus, and fallback rules maintained by its tool skill.
