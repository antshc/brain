---
name: draft-recipe
description: Draft a cookbook recipe for an AI agent practice. Use when documenting agent reliability, prompt instructions, repeatable AI workflows, or lessons learned as one concise Problem with context, Examples, Best Practices, and Related Recipes entry.
---

# Draft AI Practice Recipe

Write one standalone recipe about a reusable **AI agent practice**, not about how to use a skill or tool.

## Workflow

1. Identify the observed AI agent problem and its context: when it occurs and what makes it relevant. For repository-based requests, inspect current evidence; ignore `_backup/` and `_in-progress/`. *Done when* the Problem describes both the failure and its context.
2. Select **one or two** practical tasks. Describe each **Task** in **1–3 sentences**. Write terse, concise **AI Instructions** as direct imperative commands for each task. Use specific actions, not generic placeholders. Remove explanations and filler. *Done when* each example is ready to copy into an agent prompt.
3. Render the recipe with the **Template** below. Populate all sections; write **exactly three** Best Practices bullets and **one or two** Examples. Repeat the Example section for a second task; number the Example headings when there are two. Link only confirmed related recipes; if none exist, write `None yet.` *Done when* the rendered recipe matches the template with no empty placeholders.

## Writing rules

- Apply ASD-STE100 principles: short sentences, common words, active voice, and one command per instruction.
- Focus on AI agent behavior and reusable instructions. Do not describe skill invocation.
- Make each Example operational: include a **Task** of 1–3 sentences and ready-to-copy **AI Instructions**.
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
```
