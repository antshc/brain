# Cookbook Principle Index

Tracks reusable AI-agent practices found in this repository. A concept, ADR, or skill is evidence of a principle, **not** evidence that a cookbook recipe exists.

- `[x]` — principle has a cookbook recipe; link the recipe.
- `[ ]` — principle found in the repository but has no cookbook recipe; link its source.

## Delivery and learning

- [x] **Verification** — [recipe](verification-exit-criteria-completeness-sweep.md)
- [x] **Exit criteria (completeness verification)** — [recipe](verification-exit-criteria-completeness-sweep.md)
- [x] **Completeness sweep** — [recipe](verification-exit-criteria-completeness-sweep.md)
- [x] **Gotchas** — [recipe](gotchas-and-persistent-memory.md)
- [x] **Persistent memory** — [recipe](gotchas-and-persistent-memory.md)
- [ ] **Checklist-driven workflow** — [source](../concepts/structure-checklist-workflow.md)
- [ ] **Improvement flywheel (classify and fix observed failures)** — [source](../concepts/ops-improvement-flywheel.md)
- [ ] **Canary rule verification** — [source](../concepts/ops-canary-rule-verification.md)
- [ ] **Focused functional-slice testing** — [source](../adr/crew-is-agnostic.md)
- [ ] **Behavior-preserving agent review** — [source](../../plugins/crew/agents/chorey.agent.md)

## Instructions and drafting

- [ ] **Instruction robustness** — [source](../concepts/ops-instruction-robustness.md)
- [ ] **Constraint-first reasoning** — [source](../concepts/structure-constraint-first-reasoning.md)
- [ ] **Agent design and bounded responsibility** — [source](../concepts/structure-agents-style.md)
- [ ] **Open-question markers** — [source](../concepts/str-open-question-marker.md)
- [ ] **Repository instruction loading** — [source](../adr/crew-agents-uses-instructions.md)
- [ ] **Skill discovery and trigger descriptions** — [source](../../.github/instructions/agent-skills.instructions.md)
- [ ] **Progressive disclosure of agent guidance** — [source](../../skills/engineering/writing-great-skills/GLOSSARY.md)
- [ ] **Template ownership of rendering** — [source](../../.github/instructions/agent-skills.instructions.md)

## Composition and state

- [ ] **Skill composition and single ownership** — [source](../concepts/structure-skill-composition.md)
- [ ] **Cross-scope specialist discovery** — [source](../concepts/structure-cross-scope-skill-family.md)
- [ ] **Delegation engine isolation** — [source](../adr/explore-codebase-is-skill-agnostic.md)
- [ ] **Agent-agnostic handoff contracts** — [source](../adr/ralph-is-agent-agnostic.md)
- [ ] **Session ledger** — [source](../concepts/structure-ledger.md)
- [ ] **Trigger indexing** — [source](../concepts/structure-trigger-indexer.md)
- [ ] **Per-repository configuration resolution** — [source](../concepts/ops-per-repo-config-resolution.md)
- [ ] **Repository adapter skills** — [source](../concepts/structure-repository-adapter-skill.md)
- [ ] **Resource access skills** — [source](../concepts/structure-resource-access-skill.md)
- [ ] **Skill-owned code** — [source](../concepts/structure-skill-owned-code.md)
- [ ] **CLI JSON handoff** — [source](../concepts/str-cli-json-handoff.md)

## Scan and update

1. Scan current `ARCHITECTURE.md`, `docs/concepts/`, `docs/adr/`, `.github/instructions/`, and active agents and skills in `plugins/` and `skills/`. Ignore `_backup/` and `_in-progress/`.
2. Extract reusable **AI-agent behavior principles** supported by an explicit source rule. Merge synonyms and duplicate occurrences into one checklist entry.
3. Compare each principle with the recipes in `docs/cookbook/` (excluding this index). Check the box **only** when a recipe actually covers the principle with actionable AI instructions, and link that recipe. Otherwise leave it unchecked and link the source.
4. Add newly found principles; recheck existing entries and links. Do not mark a principle covered merely because its source document exists.
