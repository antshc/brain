---
description: Use whenever creating, editing, reviewing, or shrinking agent-facing skills (SKILL.md), agents (*.agent.md), instructions, conventions, templates, or supporting reference files — enforces terse style, frontmatter, skill invocation, and resource layout rules.
applyTo: "**/skills/**/*.md,**/agents/*.agent.md,.github/instructions/*.instructions.md"
---

# Writing agent-facing documents

Write-time guidance for `SKILL.md`, bundled references/templates, `*.agent.md`, and `.crew/` convention files. Design-time composition guidance lives in [ARCHITECTURE.md](../../ARCHITECTURE.md).

## Style

**Skill content:** write the actual rule or action first. Be extremely concise, terse, agent-optimized, and use no fillers. Sacrifice grammar for concision. Add the reason only when it changes interpretation or application. Omit explanation that does not change agent behavior.

**Section references:** use section titles without `#` markers.

**Line wrapping:** one physical line per paragraph, bullet, or table cell.

**Leading words:** prefer compact concepts the model already knows; repeat the token, not the explanation.

**Prompt positive behavior:** state the desired behavior. Use prohibitions only for hard guardrails; pair them with the desired behavior.

**Normative wording:** use **MUST** / **MUST NOT** for mandatory rules only. Use plain imperative wording for guidance or preference.

## Frontmatter and discovery

| Key | Required | Rule |
|---|---|---|
| `name` | yes | Lowercase, hyphenated, matches folder name. |
| `description` | yes | Third person; target 100–300 chars; state **when → responsibility → result**; include 3–6 distinctive trigger keywords. |
| `disable-model-invocation` | no | `true` = human-only; omit when model or other skills must discover it. |

Name skills by existing verb-prefix family. Start a new family only when needed.

Register every new plugin in [marketplace.json](../plugin/marketplace.json) in the same change.

## Skill invocation

Reference the exact plain `skill-name` without a leading `/`, immediately followed by the word `skill` (e.g. `` `fetch-page` skill ``). Wording may use run, follow, use, load, or equivalent prose; do not enforce one verb.

Every skill invocation **MUST** include 3–6 distinctive keywords from the invoked skill's description to strengthen triggering. Do not copy the full description.

Wrap the whole invocation phrase in *italics* to mark it visibly. Example: *Run `fetch-page` skill to fetch the Confluence page as Markdown.*

## Subagents

Run subagents through prose instructions describing the task, scope, inputs, constraints, and expected output. Do not instruct agents to call `runSubagent` directly.

## Content and resources

Order content by need: **steps → inline reference → disclosed reference**. Inline always-needed material; disclose conditional or bulky material.

Keep `SKILL.md` body under 300 lines.

| Folder | Holds |
|---|---|
| `scripts/` | executable automation |
| `references/` | decision/reference material |
| `assets/` | files used unchanged |
| `templates/` | scaffolds to fill or modify |

Keep up to two category files at skill root; otherwise use the matching resource folder.

**Bundled paths:** resolve `scripts/`, `references/`, `assets/`, and `templates/` from the skill base directory, never the caller CWD. Example: **Run `./scripts/run.py` from this skill's base directory**.

Prefer Python over shell-specific scripts for cross-platform automation. Use the repository-supported Python command.

## Template ownership

- **Template owns rendering; skill owns orchestration.** Template: structure, format, conditions, rendering, local constraints. `SKILL.md`: selection, workflow, inputs/outputs, shared rules.
- `{{value|hint}}` — preferred field-local guidance.
- `<!-- @: instruction -->` — hidden structural/rendering directive; **MUST** be one terse line.
- Templates MAY define local **Rules** and **Gotchas**.
- Keep template-specific guidance in the template; move only shared/cross-template guidance to `SKILL.md` or `references/`.

## Syntax legend

| Syntax | Meaning | Example |
|---|---|---|
| **bold** | Required rule, label, warning | **Required:** Run tests. |
| *italic* | Skill invocation phrase | *Run `fetch-page` skill to fetch the Confluence page as Markdown.* |
| `camelCase` | Agent-resolved conceptual value | Resolve `camelCase` from Git. |
| `camelCase := instruction` | Runtime assignment | `NAME := generate unique kebab-case name` |
| `{{camelCase}}` | Replaced placeholder | `reports/{{camelCase}}.md` |
| `{{camelCase\\|hint}}` | Preferred field-local guidance | `{{priority\\|MVP or Should have}}` |
| `<!-- @: instruction -->` | Hidden structural/rendering directive; **MUST** be one terse line | `<!-- @: repeat per component -->` |
| `[optional]` | Optional input | `[target-path]` |
| `value1 \\| value2` | Allowed values | `completed \\| failed` |
| ``literal`` | Fixed command/path/value | `dotnet test` |
| `$VARIABLE` | Shell variable | `$REPOSITORY_ROOT` |
| `${VARIABLE}` | Braced shell variable | `${REPOSITORY_ROOT}/src` |

## Procedures

Every procedural step needs a checkable completion condition. Use numbered steps only when order matters; otherwise state decision criteria.

## Gotchas

When a skill depends on an external tool, API, or platform quirk, add `## Gotchas`. State the constraint first; add why only when it changes interpretation or handling.

## Completion criteria

Add `## Completion criteria` when a skill's result is not self-evident. List observable, checkable conditions on the produced result (files, output, state) the agent confirms before reporting done.

**Why:** without them the agent stops at "steps ran" and claims success on a wrong or empty result. They define done by outcome, not by effort.

- Name the section **Completion criteria** (the condition that tells the agent the work is done). Do not use `Verification`, `Validation`, `Testing`, or `Acceptance criteria` (reserved for stories).
- State the result to observe, not how to run tests. A skill's own test suite is repository tooling: **MUST NOT** appear in a skill — no test commands, test paths, or test-only dependencies.
- Omit the section when the steps' completion conditions already prove the result.

## Completeness sweep

Completion criteria check whether the defined result meets its contract; a completeness sweep checks whether any required scope was omitted.

- Add a **closing completeness sweep** for multi-part work with independently missable obligations: features, cross-file refactors, migrations, or broad research.
- When used, the sweep **MUST** run last, after other checks. Re-read the request, reconstruct explicit and implied obligations, and map each to evidence across affected code, tests, docs, configuration, and relevant failure/compatibility paths.
- Resolve uncovered obligations by implementing them, asking for clarification, or reporting explicit deferral. **MUST NOT** declare completion with an unaccounted obligation.
- Omit the sweep for small, bounded work when procedural checks or completion criteria already prove full coverage (e.g. a method rename or single defined diagram). **MUST NOT** duplicate the same checks under both sections.

See [Completeness Sweep](../../docs/concepts/ops-completeness-sweep.md) for the closing procedure and [comparison research](../../docs/research/skill-result-check-section-naming.md) for selection examples.

## Pruning

- **One meaning, one place.** Invoke shared procedure; do not duplicate it.
- **Record only non-obvious knowledge.** Prefer source-of-truth files/config over copied facts.
- **Delete no-ops and stale rules.** Keep only text that changes agent behavior.

## Before finishing

- Valid frontmatter; trigger-rich description.
- `SKILL.md` body under 300 lines.
- Shared procedure not duplicated.
- No test commands or test-only dependencies; result checks live under `## Completion criteria`.
- No credentials, tokens, or secrets.