# Draft phase

Write or rewrite one skill from a brief or request. Apply every rule in [best-practices.md](best-practices.md) and [wording.md](wording.md); fill [SKILL.template.md](../templates/SKILL.template.md). Ground every fact in the input or the environment; record each gap as an assumption instead of guessing.

## Inputs

- **Input** — skill brief or free-text request, verbatim.
- **Target** — skill folder path; derive from the brief, or from repository layout (`plugins/<plugin>/skills/<name>/`, `skills/<area>/<name>/`, or `.github/skills/<name>/`).
- [**Existing skill**] — when rewriting, the current files.

## Steps

1. **Load rules.** Read best-practices.md, wording.md, and the template in full, plus repository agent-skill instructions (e.g. `.github/instructions/*skill*.instructions.md`) when present; repository rules win on conflict. *Done when* all are read.
2. **Resolve identity.** Set name (verb-prefix family, matches folder), target path, plugin, invocation mode, callers. Check the environment for name collisions and neighbouring skills to compose with instead of duplicating. *Done when* name and path are unique and invocation mode is justified by callers.
3. **Inventory (rewrite only).** List every rule, step, constraint, failure behavior, pointer, and completion criterion of the existing skill. *Done when* every sentence maps to an item.
4. **Select variant.** Apply Variant selection from the template: workflow, probes, or free-form. *Done when* one variant is chosen with a one-line reason.
5. **Write description.** Front-load the leading word; one trigger per branch; 3–6 keywords; check every forbidden description character. *Done when* it states when, responsibility, result and passes the character table.
6. **Fill body.** Fill every placeholder; delete unused sections and all `<!-- @: -->` directives of the template. Apply instruction precision: constraint pattern for critical rules, a failure policy per critical step, degrees of freedom matched to task risk, output contract with no-result and incomplete outcomes. *Done when* no placeholder or template directive remains and each step has a checkable completion condition.
7. **Disclose and place resources.** Push branch-specific or bulky reference behind conditionally worded pointers into `references/`; scaffolds into `templates/`; fragile repeated operations into `scripts/`. Copy any needed resource into this skill's folder. *Done when* every link resolves inside the skill folder and `SKILL.md` body is under 300 lines.
8. **Register.** For a new plugin, create its manifest and register it in the repository marketplace and README following existing entries. *Done when* the plugin is discoverable the same way as its siblings, or no new plugin was created.
9. **Self-check.** Walk every section of best-practices.md and every Before finishing item; mark each applied or not applicable. For rewrites, confirm every inventory item is preserved or deliberately changed per the input. *Done when* no item is unaccounted.

## Return

- Created or modified file paths (absolute).
- Name, invocation mode, variant with reason.
- Assumptions made for gaps in the input.
- Rewrite only: inventory items changed or removed, each with reason.
