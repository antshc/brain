---
name: write-agent
description: Writes or rewrites a custom coding agent definition, including planner agents that decompose features into parallel task graphs, from a brief using bundled best practices, with a routing description, least-privilege tools, bounded scope, and an evidence-based output contract.
disable-model-invocation: true
---

# Write Agent

Own one custom coding agent definition file: create or rewrite it. Writable surface: the target agent file only.

## Inputs

- **Input** — agent brief or free-text request, verbatim. Required.
- [**Target**] — agent file path. When missing, derive from repository layout: existing `plugins/<plugin>/agents/`, `.github/agents/`, `.claude/agents/`, `.codex/agents/`, `.gemini/agents/`, or `.grok/agents/`; prefer the folder holding sibling agents. Ask only when neither input nor layout names a location.
- [**Existing agent**] — current file when rewriting.

## Constraints

- **MUST** ground every fact (paths, commands, tool names, skills, models) in the input or the environment. Record each gap as an assumption in the output; leave the field out of the file rather than inventing it.
- **MUST** configure tools with least privilege through the platform's frontmatter or config, not only through body text. Rationale: instructions are probabilistic, not a security boundary. If the platform cannot restrict a needed boundary (e.g. Codex inherits parent permissions), keep the body rule and list the required runtime control (permission, hook, sandbox, branch protection, CI gate) in the output.
- **MUST** reference an existing skill for procedural work instead of copying its procedure into the body. If no skill owns the procedure, keep a short workflow and report the gap.
- **MUST** keep the agent to one responsibility. If the input describes several, stop and return a split per Output.

## Workflow

1. **Load rules.** Read `references/agent-best-practices.md` and `templates/agent.template.md` in full, plus repository instructions covering `*.agent.md` or agent files (e.g. `.github/instructions/*.instructions.md` whose `applyTo` matches the target) when present; repository rules win on conflict. *Done when* all are read.
2. **Resolve platform, identity, kind.** Set `@agentKind` to `planner` when the agent decomposes a spec, feature, or plan into tasks for other agents; else `standard`. For `planner`, also read `templates/planner.template.md` and `templates/planner-output.template.md` in full; use them in place of `templates/agent.template.md`. Set platform from the target path or sibling agents; read that platform's section of `references/platforms.md` for location, format, and metadata fields. Set name (lowercase, hyphenated unless `references/platforms.md` gives the platform's convention, matches file name, role noun such as `reviewer` or `debugger`). Read every sibling agent's description. *Done when* platform, path, and name are set and the name is unique.
3. **Check fit.** Apply Layer test in `references/agent-best-practices.md`. **Belongs to another layer?** → stop; return per Output. **New agent?** → step 5. **Existing agent?** → step 4. *Done when* the Layer test places the work in the agent layer.
4. **Inventory (rewrite only).** List every rule, step, constraint, tool, failure behavior, skill reference, and output field of the existing agent. *Done when* every sentence maps to an item.
5. **Write description.** Follow Description in `references/agent-best-practices.md`. *Done when* it meets those rules and no sibling description would be selected for the same request.
6. **Set tools and metadata.** Grant only tools the workflow uses. Add model, effort, turn, or timeout fields only when the input names them. *Done when* every granted tool maps to a workflow step and every edit, execute, or external tool is justified.
7. **Fill body.** Fill the template per its directives; write constraints per Constraint language and checks per Verification in `references/agent-best-practices.md`; for agents that edit code, also apply Coding agents there; for `planner`, apply Planner agents there and inline the output template's field table, example, and failure shape into Output, reusing an established ticket schema when the repository has one. Read `references/examples.md` when choosing section depth or wording. *Done when* no placeholder or `<!-- @: -->` directive remains and each workflow step has an observable result.
8. **Self-check.** Walk Checklist in `references/agent-best-practices.md`; mark each item applied or not applicable. Rewrite: confirm every inventory item is preserved or deliberately changed per the input. *Done when* no item is unaccounted.

## Output

- Created or modified agent file path (absolute).
- Name, platform, granted tools with the step needing each, skills referenced.
- Runtime controls the user must configure outside the file.
- Assumptions made for gaps in the input.
- Rewrite only: inventory items changed or removed, each with reason.
- No agent warranted: recommended layer and reason; no file written.
- Split needed: proposed agents with one description each; no file written.

## Gotchas

- Metadata, model aliases, and tool names differ per client and change; validate against the installed client rather than copying examples or `references/platforms.md`.

## Completion criteria

- Agent file exists at the target path; frontmatter or TOML parses; `name` matches the file name.
- Body covers every template section, merged only per the template's very-small-agent directive.
- Planner: no edit tools granted; Output defines every task-graph field, a compact example, and the failure shape.
