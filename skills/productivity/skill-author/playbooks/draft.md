# Draft phase

Write or rewrite one skill from a brief or request. Apply every rule in [best-practices.md](../references/best-practices.md) and [wording.md](../references/wording.md); fill [SKILL.template.md](../templates/SKILL.template.md). Ground every fact in the input or the environment; record each gap as an assumption instead of guessing.

## Inputs

- **Input** — skill brief or free-text request, verbatim.
- **Target** — skill folder path; derive from the brief, or from repository layout (`plugins/<plugin>/skills/<name>/`, `skills/<area>/<name>/`, or `.github/skills/<name>/`).
- [**Existing skill**] — when rewriting, the current files.

## Steps

1. **Load rules.** Read best-practices.md, wording.md, and the template in full, plus repository agent-skill instructions (e.g. `.github/instructions/*skill*.instructions.md`) when present; repository rules win on conflict. *Done when* all are read.
2. **Resolve identity.** Set name (verb-prefix family, matches folder), target path, plugin, invocation mode, callers. Check the environment for name collisions and neighbouring skills to compose with instead of duplicating. *Done when* name and path are unique and invocation mode is justified by callers.
3. **Inventory (rewrite only).** List every rule, step, constraint, failure behavior, pointer, completion criterion, route trigger/playbook/output, routing policy, and tactic trigger/consumer/result of the existing skill. *Done when* every sentence maps to an item.
4. **Select composition.** Apply Route composition in best-practices.md and Block selection in the template: inline Workflow for one short procedure; Routing plus playbooks for related substantial outcomes; inline short tactics, extract bulky/conditional/shared techniques. Add Loop, Reference, or free-form only when needed. Define route triggers, owned outputs, selection, ambiguity, continuation, combined-request order, and tactic consumers/results. *Done when* each chosen block and file has a reason; no unnecessary folder is planned.
5. **Write description.** Follow Description shape: imperative What sentence with the leading word first, then 2–5 user-phrase triggers (one per branch), optional sibling redirect; check every forbidden description character. *Done when* it states what, when, and any redirect, and passes the character table.
6. **Fill body.** Fill every placeholder; delete unused sections and all `<!-- @: -->` directives of the template. Apply instruction precision: constraint pattern for critical rules, a failure policy per critical step, degrees of freedom matched to task risk, output contract with no-result and incomplete outcomes. *Done when* no placeholder or template directive remains and each step has a checkable completion condition.
7. **Disclose and place resources.** For extracted route procedures fill playbook.template.md; for extracted techniques fill tactic.template.md. Push branch-specific or bulky knowledge into `references/`, scaffolds into `templates/`, fragile repeated operations into `scripts/`. Create only needed files inside the target skill. Link every playbook, tactic, and reference directly from its `SKILL.md` with a loading condition; use one authoritative definition per method. Keep shared invariants in the body and selection out of playbooks; prevent loading chains. *Done when* links resolve inside the skill, route/tactic coverage is complete, unused directories/directives are absent, and `SKILL.md` body is under 300 lines.
8. **Register.** For a new plugin, create its manifest and register it in the repository marketplace and README following existing entries. *Done when* the plugin is discoverable the same way as its siblings, or no new plugin was created.
9. **Self-check.** Walk every section of best-practices.md and every Before finishing item; mark each applied or not applicable. For rewrites, confirm every inventory item is preserved or deliberately changed per the input. *Done when* no item is unaccounted.

## Return

- Created or modified file paths (absolute).
- Name, invocation mode, blocks and resource layout with reasons; route/tactic inventory or none.
- Assumptions made for gaps in the input.
- Rewrite only: inventory items changed or removed, each with reason.
