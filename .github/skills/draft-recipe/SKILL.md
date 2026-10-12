---
name: draft-recipe
description: Draft a cookbook recipe for an AI agent practice. Use when documenting agent reliability, prompt instructions, repeatable AI workflows, or lessons learned as one concise Problem with context, Examples, Best Practices, Related Recipes, and source references entry.
---

# Draft AI Practice Recipe

Write one standalone recipe about a reusable **AI agent practice**, not about how to use a skill or tool.

## Workflow

1. Identify the observed AI agent problem and its context: when it occurs and what makes it relevant. For repository-based requests, inspect current evidence; ignore `_backup/` and `_in-progress/`. *Done when* the Problem describes both the failure and its context.
2. Inspect relevant real skills from the **Example sources** below. Prefer source examples and instruction excerpts over invented examples. Read the source file and record its commit SHA and exact line range. If a skill points to a supporting file, read and cite that file too. *Done when* each selected source passage supports the recipe's practice.
3. Select **one or two** practical tasks based on those passages. Describe each **Task** in **1–3 sentences**. Write terse, concise **AI Instructions** as direct imperative commands for each task. Use specific actions, not generic placeholders. Remove explanations and filler. *Done when* each example is ready to copy into an agent prompt.
4. Render the recipe with the **Template** below. Populate all sections; write **exactly three** Best Practices bullets and **one or two** Examples. Repeat the Example section for a second task; number the Example headings when there are two. Add **References** as the last section. Map every Example to the real skill and exact source lines used. Link only confirmed related recipes; if none exist, write `None yet.` *Done when* the rendered recipe matches the template with no empty placeholders.

## Example sources

- **[Lauren Tan (poteto) — pstack](https://github.com/cursor/plugins/tree/main/pstack):** Inspect `pstack/skills/` for relevant skills and their supporting files.
- **[Addy Osmani — Agent Skills](https://github.com/addyosmani/agent-skills):** Inspect real `SKILL.md` files and their supporting files.
- **[Matt Pocock — Skills](https://github.com/mattpocock/skills):** Inspect `skills/engineering/` and `skills/productivity/` for relevant skills and their supporting files.

Use the sources that match the practice. Do not require an example from every repository.

## Writing rules

- Apply ASD-STE100 principles: short sentences, common words, active voice, and one command per instruction.
- Focus on AI agent behavior and reusable instructions. Do not describe skill invocation.
- Make each Example operational: include a **Task** of 1–3 sentences and ready-to-copy **AI Instructions**.
- Preserve the source practice when adapting an example. Mark adaptations in References; do not present adapted text as a verbatim excerpt.
- Cite each Example with the author, skill name, source file, and exact lines. Use a verified GitHub permalink: `https://github.com/{{owner}}/{{repo}}/blob/{{commitSha}}/{{path}}#L{{start}}-L{{end}}`.
- Cite the lines that contain the example or instructions used, not just the repository homepage or skill heading.
- If the passage is in a supporting file, include both the real skill link and the supporting file's line permalink.
- Never invent source content, paths, commit SHAs, or line ranges. If no relevant passage is available, state the gap and label any original example as original.
- Put detailed commands only in **AI Instructions**. Do not add a Solution section.
- Do not add a Verification section.

## Template

```md
# Recipe: {{name|AI agent practice}}

## Problem
{{problem|Describe the AI agent problem and the context in which it occurs.}}

## Example

**Task:** {{task|Describe one practical use case in 1–3 sentences.}}

**AI Instructions:**
> {{instructions|Write terse, concise, task-specific commands ready to copy into an AI agent prompt.}}

## Best Practices
- {{recommendedApproach|Recommended approach.}}
- {{pitfall|Common mistake to avoid.}}
- {{constraint|Important constraint.}}

## Related Recipes
- {{relatedRecipe|Verified relative link or URL; write "None yet." if no related recipe exists.}}

## References
- **{{author}} — [{{skillName}}]({{skillUrl}}):** Example {{exampleNumber}}, {{adapted from|excerpt from}} [{{sourcePath}}, lines {{start}}–{{end}}]({{sourceLinePermalink}}).
```
