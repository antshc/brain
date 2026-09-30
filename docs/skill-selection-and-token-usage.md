# Skill selection and token usage

## Goal

Keep the skill catalog large enough to cover real tasks while making selection predictable and reducing context used by irrelevant or oversized instructions. Optimize observed task quality, token usage, and latency rather than aiming for an arbitrary skill count.

## How loading works

Copilot discovers skills by their frontmatter names and descriptions. When a skill is selected, it loads the `SKILL.md` body; additional referenced files are read as needed. Having 80 installed skills therefore does not mean loading 80 full bodies for every task. However, a broad catalog increases routing ambiguity, and descriptions and selected bodies have a context cost. Measure the actual cost in the host you use.

Treat the three loads separately:

| Load | What to optimize |
|---|---|
| Discovery | Enabled skills and concise, distinct descriptions |
| Invocation | The selected `SKILL.md` body |
| Follow-up reading | Referenced files, search results, tool output, and repeated instructions |

## Choose the right exposure

| Need | Form |
|---|---|
| The agent must select the skill from a natural-language request | Model-invocable skill with a precise description |
| You always invoke the workflow by name | Skill with `disable-model-invocation: true` |
| A rule applies to code in a given file scope | Scoped Copilot instruction file |
| Another workflow uses reference material on one branch | Linked reference file inside that skill |
| A capability needs a distinct agent role or tool set | Custom agent |
| An operation must occur deterministically on a lifecycle event | Hook or script |

`user-invocable: false` hides a skill from the slash menu **but leaves automatic invocation enabled**. It is useful for background skills the agent should still discover. With both `user-invocable: false` and `disable-model-invocation: true`, a skill has neither normal route; use a reference file instead if another workflow must read it. See the [VS Code skill options](https://code.visualstudio.com/docs/agent-customization/agent-skills).

`init-crew` already uses the explicit-only setting. Keep that pattern for workflows that only run after a named command. Keep `testing-*` skills discoverable where coding agents must find the applicable test types, commands, setup, and seams.

## Write descriptions for selection

Each model-invocable description should answer:

1. **When:** the observable request or artifact that triggers the skill.
2. **What:** its single responsibility.
3. **Result:** the output or decision it produces.

Start with the distinguishing verb or object. Use one clause per genuinely different trigger. Remove generic phrases such as “use for software work” and duplicated synonyms. State the boundary with a neighboring skill where the same request might match both.

Example shape:

```yaml
description: "Inspect as-built behavior in one deployable and write a cited report. Use when asked how an existing code path works or where its decision is made."
```

Test descriptions against realistic prompts, including negative cases. Do not rely on a long body to repair an incorrect initial match: the body is loaded after selection.


### Do quotes or bold markers improve selection?

There is no documented selection boost for wrapping words in `'single quotes'` or `**Markdown bold**`. Copilot uses the parsed description to judge relevance; the Agent Skills specification calls for a clear task and trigger with specific terms. The `description` is a YAML string, not the Markdown body, so `**` has no specified emphasis effect. A model might react differently to any changed text, but punctuation alone is not a reliable routing strategy.

Distinguish **YAML delimiters** from characters *inside* the value:

```yaml
description: 'Inspect as-built behavior in one deployable.'
```

Or:

```yaml
description: "Inspect as-built behavior in one deployable."
```

These yield the same description text. Choose outer single or double quotes when needed to parse the value safely (for example, when it contains `: `); they do not make selection more likely. Quotes *inside* the value remain text and can clarify a literal command, label, or phrase, but only when that distinction matters. Likewise, `**as-built behavior**` adds literal asterisks to the value and has no guaranteed benefit over `as-built behavior`.

Spend the characters on discriminating task words and boundaries instead. If punctuation appears to help in one run, compare both versions on the same should-trigger and near-miss prompts before retaining it.

## Cross-skill invocation

Use the exact child skill name with a few distinctive keywords from its description. The name identifies the dependency; the keywords state why the child applies.

### Reusable template

> When <trigger keywords from child description> applies, load and follow <exact-skill-name> from <plugin>. Use it for <child responsibility and output keywords>. Pass <required inputs and parent constraints>. Confirm it was loaded before continuing.

### Example

> When documenting software behavior—interactions, decisions, or responsibility handoffs—load and follow `doc-behavior-diagram` from the `wf` plugin. Use it to create sequence, flowchart, or swimlane diagrams. Pass the required diagram type, scope, participants, evidence, and requested output location. Confirm it was loaded before drafting.

Use 3–6 distinctive keywords from the child description. Do not copy the complete description or add unrelated terms. A child skill's description supports independent discovery; the parent instruction defines the required dependency.

## Keep the loaded body focused

Put common steps, branch selection, and checkable completion criteria in `SKILL.md`. Put material needed only for one branch in a linked file, with a pointer that says exactly when to open it. Keep hard safety and correctness gates on the path that needs them.

The current `plugins/wf/skills/inspect-system/SKILL.md` has Behavior, Flow, and Data branches and already links axis-specific references. A first experiment is to move each branch's detailed diagram, evidence, and formatting guidance behind its axis pointer while keeping the short axis routing rules and shared evidence rules in the body. Check that no branch loses a required completion criterion. This is a candidate for measurement, not a blanket instruction to split the skill into three discoverable entries.

Split a skill only when the new entry has an independently useful trigger, output, or invocation path. If a helper has no independent task, keep it as a reference or script. Avoid copying the same rules into a router, a child skill, and an agent.

## Audit the installed catalog

1. Export the active CLI catalog with `copilot skill list --json`; record `name`, `source`, `path`, `enabled`, and `description`. Check plugin, project, and personal sources for duplicate purposes.
2. Group descriptions by request type and output. Flag overlapping triggers, generic “research/review/document” wording, unused explicit workflows exposed to automatic invocation, and helpers with no independent entry point.
3. Inspect the bodies of frequently invoked skills for duplicated instructions, unconditional reference dumps, and references that are read on every branch.
4. Disable an unused skill for a trial before removing it. In CLI, `copilot skill disable <name>` and `copilot skill enable <name>` support this. Plugin-provided files remain managed by their plugin.

Do not merge skills simply to make the catalog smaller: a large merged body can cost more on each invocation and blur routing.

## Verify with representative tasks

Build a small prompt set from actual work:

| Prompt type | Expected route |
|---|---|
| “How does this endpoint behave today?” | `inspect-system`, Behavior |
| “Trace the message across services” | `inspect-system`, Flow |
| “What owns this stored item and its retention?” | `inspect-system`, Data |
| “Does this SDK operation work against the real service?” | `experiment` |
| “Implement this repository change and verify it” | Coding agent; discover applicable `testing-*` guidance |
| “Initialize Crew here” | Explicit `init-crew` |

For each prompt, record selected skills, unnecessary loads, answer quality, input tokens, tool calls, and duration. Include near misses that should **not** load a skill. Change one factor at a time: descriptions first, then explicit-only settings, then body/reference boundaries.

In VS Code, use **Agent Debug Logs** for discovery and token metrics, and **Chat Debug** to inspect the request context. In Copilot CLI, use `/context` for context usage, `/skills info <name>` to confirm a skill's source, and `copilot skill list --json` for the catalog. Re-run the same prompts after each change; keep a reduction only if behavior still meets the task's quality bar.

## Suggested first pass in this repository

1. Audit the `wf` descriptions around `inspect-*`, `research-*`, `doc-*`, `review-*`, and `experiment` for overlapping triggers.
2. Preserve explicit-only setup commands such as `init-crew`; evaluate other commands with the same invocation pattern.
3. Measure a smaller `inspect-system` body against the three axis prompts above.
4. Verify that coding agents still discover the applicable `testing-*` skills and run the smallest relevant checks.

## References

- [VS Code: Agent Skills](https://code.visualstudio.com/docs/agent-customization/agent-skills)
- [Agent Skills: description specification](https://agentskills.io/specification#description-field)
- [Agent Skills: optimizing descriptions](https://agentskills.io/skill-creation/optimizing-descriptions)
- [YAML: scalar styles and values](https://yaml.org/spec/1.2.2/ext/glossary/)
- [GitHub Copilot CLI: manage skills](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-command-reference#managing-skills-non-interactively)
- [VS Code: Debug chat interactions](https://code.visualstudio.com/docs/agents/agent-troubleshooting/chat-debug-view)
- [GitHub Copilot CLI: Manage context](https://docs.github.com/en/copilot/concepts/agents/copilot-cli/context-management)
- [Repository guidance: writing great skills](../skills/engineering/writing-great-skills/SKILL.md)
