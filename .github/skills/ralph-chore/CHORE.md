# CHORE

After the Verify steps pass, review all changed skills, agents, and templates together for refactoring candidates:

- **Mixed responsibilities** → split into one skill per responsibility
- **Duplicated rules across skills** → extract to one owning skill, run it by name
- **Rationale that is the decision criterion** → keep it as one clause on the rule's own line — it tells the agent how to resolve a case the rule didn't cover
- **Known failure mode** → keep as one counterexample line — it blocks a wrong behaviour the positive rule doesn't
- **History ("we used to…"), benefits aimed at a human reviewer, rationale that restates the rule** → delete
- **Hedging and filler** ("you may want to", "it's important to") → imperative verb
- **Vague step** → verifiable action with a stated done condition
- **Synonyms for one concept** → single canonical term
- **Example that only restates the rule** → drop it; keep one minimal example at most
- **`description` frontmatter without a trigger** → rewrite as "Use when …"
- **Existing skill text** the new content reveals as stale or contradictory