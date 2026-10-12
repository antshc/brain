# Existing Agent-Skills Cookbooks on GitHub

Reference repositories for designing an AI engineering cookbook: authoring `SKILL.md` files, agent instructions, reusable practices, recipes, and indexes.

Checked: 2026-10-11. These are external references, **not** imported or verified cookbook principles. Capture a specific practice as a separate recipe only after reviewing its source.

## Closest references

| Repository | Focus | What to study |
| --- | --- | --- |
| [agentskillexchange/agent-skills-resources](https://github.com/agentskillexchange/agent-skills-resources) | Agent-skills handbook with a cookbook, checklists, examples, anti-patterns, evaluation, and generated indexes | [Cookbook](https://github.com/agentskillexchange/agent-skills-resources/tree/main/cookbook), [navigation index](https://github.com/agentskillexchange/agent-skills-resources/blob/main/generated/nav-index.md), [anti-patterns](https://github.com/agentskillexchange/agent-skills-resources/blob/main/cookbook/common-anti-patterns.md) |
| [b-mendoza/agent-skills](https://github.com/b-mendoza/agent-skills) | Skill-authoring guidance, architecture, examples, and evaluations | [Best practices](https://github.com/b-mendoza/agent-skills/tree/main/docs/best-practices), [architecture](https://github.com/b-mendoza/agent-skills/blob/main/docs/architecture.md) |
| [latestaiagents/agent-skills](https://github.com/latestaiagents/agent-skills) | Reusable skills and plugins, including skill-authoring workflows | [Skills](https://github.com/latestaiagents/agent-skills/tree/main/skills), [plugins](https://github.com/latestaiagents/agent-skills/tree/main/plugins) |
| [layerzlabs/cookbook](https://github.com/layerzlabs/cookbook) | Problem-oriented recipes, reusable prompts, and skill implementations | [Recipe template](https://github.com/layerzlabs/cookbook/blob/main/TEMPLATE.md), [recipes](https://github.com/layerzlabs/cookbook/tree/main/recipes) |
| [OpenDataBox/OpenCook](https://github.com/OpenDataBox/OpenCook) | Agent-based coding workflow with skill support, prompts, memory, and tools | [Code agent](https://github.com/OpenDataBox/OpenCook/tree/main/code_agent), [skills](https://github.com/OpenDataBox/OpenCook/tree/main/code_agent/skills) |

## Adjacent cookbook and catalog designs

| Repository | Focus | What to study |
| --- | --- | --- |
| [DenisSergeevitch/agents-best-practices](https://github.com/DenisSergeevitch/agents-best-practices) | Agent engineering practices and a reusable `SKILL.md` | [Skill](https://github.com/DenisSergeevitch/agents-best-practices/blob/main/SKILL.md), [references](https://github.com/DenisSergeevitch/agents-best-practices/tree/main/references) |
| [gorgias/mcp-cookbook](https://github.com/gorgias/mcp-cookbook) | Task-specific MCP recipes with a consistent template | [Recipes](https://github.com/gorgias/mcp-cookbook/tree/main/recipes), [template](https://github.com/gorgias/mcp-cookbook/tree/main/recipes/_template) |
| [SAP/custom-agentic-cookbook](https://github.com/SAP/custom-agentic-cookbook) | Sequential core recipes and optional agentic integrations | [Recipes](https://github.com/SAP/custom-agentic-cookbook/tree/main/recipes), [optional recipes](https://github.com/SAP/custom-agentic-cookbook/tree/main/recipes/optional) |
| [harbor-framework/harbor-cookbook](https://github.com/harbor-framework/harbor-cookbook) | Executable agent-task examples and evaluation infrastructure | [Repository](https://github.com/harbor-framework/harbor-cookbook), [source](https://github.com/harbor-framework/harbor-cookbook/tree/main/harbor_cookbook) |
| [agentskillexchange/skills](https://github.com/agentskillexchange/skills) | Large, machine-readable skill catalog organized by categories | [Catalog](https://github.com/agentskillexchange/skills/blob/main/CATALOG.md), [skills.json](https://github.com/agentskillexchange/skills/blob/main/skills.json), [categories](https://github.com/agentskillexchange/skills/tree/main/categories) |

## Design ideas for this cookbook

| Problem to solve | Reference pattern | Candidate application |
| --- | --- | --- |
| Engineers cannot find practices for their problem | Layerz uses problem-oriented recipes; Agent Skills Resources has topical cookbook pages | Use **problem statements** as human navigation categories; task types (debugging, reviewing, planning) as filters |
| Agents cannot locate the right recipe efficiently | Agent Skills Resources publishes a generated navigation index; Agent Skill Exchange publishes structured catalogs | Maintain an agent-readable index with title, problem, tags, and recipe path |
| Recipes have inconsistent structure | Layerz provides a recipe template; Gorgias has a shared recipe template | Keep a small, consistent recipe format: problem/context, instruction, best practices, related recipes |
| Guidance becomes stale or duplicates other guidance | Agent Skills Resources covers maintenance, source-backed skills, and anti-patterns | Record source links; audit examples and references before promoting a practice |
| Static documentation lacks proof it works | b-mendoza includes evaluations; Harbor provides executable agent-task examples | Associate repeatable verification or evaluation with recipes where applicable |

**Recommended combination:** Layerz for problem-oriented recipes; b-mendoza for skill-authoring guidance; Agent Skills Resources for anti-patterns and navigation; Agent Skill Exchange for machine-readable discovery.

Related local material: [Cookbook principle index](index.md) and [skill template categories](skill-template-categories.md).
