---
applyTo: "**/SKILL.md,**/*.agent.md,**/*.prompt.md,**/*.instructions.md,**/AGENTS.md"
---
# AI authoring conventions

- Read the target and a representative sibling before editing; follow established folder and naming conventions.
- Use lowercase hyphenated skill names matching the folder. State the trigger in a third-person frontmatter description. Use `disable-model-invocation: true` only for skills humans must invoke directly.
- Keep `SKILL.md` under 500 lines and disclose large occasional material through linked `references/`. Put executable automation in `scripts/`, scaffolds in `templates/`, unchanged output resources in `assets/`.
- Give each skill one purpose; reach shared procedures by invoking their owner rather than duplicating their steps.
- Use concrete, checkable instructions and canonical terms. Remove filler, repeated rationale, and examples that only restate a rule.
- Follow existing verb-prefix families for new skills and update the marketplace manifest when adding a plugin. Use `python3` for portable scripted commands.
- Add a concise `## Gotchas` rule when an external platform quirk causes an observed failure; avoid speculative gotchas.
- Check that every invoked skill, path, and linked reference exists; keep affected paragraphs and list items on one physical line when the repository does so.
- Keep credentials out of generated instructions, skills, and prompts.
