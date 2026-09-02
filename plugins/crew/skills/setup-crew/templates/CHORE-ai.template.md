# CHORE — AI Authoring

<!-- Read in full by crew-review during Chorey's REVIEW step. Hazard rules below are AI-authoring-general and ship with this template — kept even when repository practice differs; a conflict is recorded in the shared GOTCHAS.md instead of edited here. Review rules/Never describe this repo's own behavior-preserving cleanup rules — never invent or copy example values from another repo. When this file exists it replaces crew-review's inline default for this Stack's files. -->

## Hazard rules (AI authoring)
- Never fold two skills' distinct triggers into one shared description just to remove duplication — a description that now fires on unrelated tasks is a correctness regression, not a cleanup.

## Review rules
<!--
List the behavior-preserving refactor patterns Chorey should look for and apply to this repo's skills/agents/templates, and anything it must never touch. Default checklist (replace or extend with real, repo-specific rules):
-->
- **Duplication** → extract shared procedure into the skill that owns it, invoked by name
- **Long/branching steps** → break into decision criteria or sub-steps
- **Shallow skills** → combine or deepen
- **Stale reference** → update or disclose to a sibling file
- **Existing content** the new content reveals as problematic

## Never
<!-- List anything Chorey must never change in this repo's skills/agents/templates (e.g. published frontmatter names, marketplace registration, another skill's owned procedure). -->
