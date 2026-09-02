# CHORE

Review all changed skills, agents, and templates together as one unit for behavior-preserving refactors.

## Rules

- Mixed responsibilities → split into one skill per responsibility.
- Duplicated rule across skills → extract to the owning skill; others reference it by name.
- Rationale that is a decision criterion (resolves a case the rule doesn't cover) → keep, one clause on the rule's line.
- Known failure mode (blocks a wrong behavior the positive rule doesn't) → keep, one counterexample line.
- Rationale that restates the rule, history, or human-reviewer justification → delete.
- Hedging/filler ("you may want to", "it's important to") → imperative verb.
- Vague step → verifiable action with a stated done condition.
- Synonyms for one concept → single canonical term.
- Example that restates the rule → drop; keep at most one minimal example.
- `description` frontmatter without a trigger → rewrite as "Use when …".
- Existing skill text contradicted or made stale by new content → update or flag.
