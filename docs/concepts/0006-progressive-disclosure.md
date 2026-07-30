# Progressive Disclosure

**Status:** Accepted

## Purpose

A `SKILL.md` that inlines every detail an agent might ever need — edge cases, extended reference tables, rarely-used templates — grows past what the agent must read on every invocation, wasting context and burying the core instructions. Progressive Disclosure keeps `SKILL.md` limited to the core instructions the agent needs on every run, and moves detailed reference material the agent only needs sometimes into separate files (e.g. `references/`) that are read on demand.

## Design Guidance

- Keep `SKILL.md` under ~500 lines and ~5,000 tokens — just the instructions needed on every run.
- When a skill legitimately needs more content (extended formats, large tables, rarely-used edge cases), move it to separate files in `references/` or similarly named directories alongside the skill.
- `SKILL.md` should link to or name the reference file and state when to consult it, rather than inlining its content.
- Applies to every skill authored in this repo, not just large ones — apply the split as soon as a skill's instructions grow beyond core, every-run guidance.
- Distinct from a skill's format templates (e.g. `CONCEPT-FORMAT.md`, `ADR-FORMAT.md`): those are already separate files by convention; Progressive Disclosure is the general rule that motivates keeping them separate, and extends the same treatment to any other bulky, occasionally-needed material.
