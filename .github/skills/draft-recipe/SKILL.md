---
name: draft-recipe
description: Draft a cookbook recipe for an AI agent practice. Use when documenting agent reliability, prompt instructions, repeatable AI workflows, or lessons learned as one concise Problem, Solution, Example, Best Practices, and Related Recipes entry.
---

# Draft AI Practice Recipe

Write one standalone recipe about a reusable **AI agent practice**, not about how to use a skill or tool.

## Workflow

1. Identify the observed AI agent problem and the repeatable instruction that prevents it. For repository-based requests, inspect current evidence; ignore `_backup/` and `_in-progress/`. *Done when* the problem and prevention are specific.
2. State the Solution in **one or two sentences**. Describe **what to instruct the AI agent to do** and **when**. Do not assign the procedure to the human reader. *Done when* both the instruction and its trigger are clear.
3. Select **one** practical task. Write terse, concise **AI Instructions** as direct imperative commands for that task. Use specific actions, not generic placeholders. Remove explanations and filler. *Done when* the reader can copy the instructions into an agent prompt without modification.
4. Render the recipe with [templates/recipe.md](templates/recipe.md). Populate all sections; write **exactly three** Best Practices bullets and only **one** Example. Link only confirmed related recipes; if none exist, write `None yet.` *Done when* the rendered recipe matches the template with no empty placeholders.

## Writing rules

- Apply ASD-STE100 principles: short sentences, common words, active voice, and one command per instruction.
- Focus on AI agent behavior and reusable instructions. Do not describe skill invocation.
- Make the Example operational: include both **Task** and ready-to-copy **AI Instructions**.
- Keep the Solution brief. Put detailed commands in **AI Instructions**, not in the Solution.
- Do not add a Verification section.
