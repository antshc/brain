---
name: grill-skill
description: Interview the user to define a new agent skill and produce a confirmed skill brief for /write-skill.
disable-model-invocation: true
---

# Grill Skill

Own the interview and the **skill brief**. Writing belongs to `/write-skill`, which the user runs. Writable surface: none until handoff.

## Interview

Walk the question tree in order; skip a question once the user's input or the environment answers it. Look up facts before asking: existing plugins and skills, naming families, name collisions, neighbouring skills to invoke instead of duplicating, repository agent-skill instructions.

Ask one question at a time, phrased so "yes" accepts the recommendation:

```markdown
❓ **Q<n>** - **<title>**: <question>

- **A** (Recommended) <option>
- **B** <option>

➡️ <recommended answer and reason>
```

Record each answer into the brief; rebuild later questions when an answer changes earlier ones. Unanswered questions stay open, never implicitly accepted.

## Question tree

| # | Topic | Resolve | Recommend by |
|---|---|---|---|
| 1 | **Purpose** | One-phrase responsibility | More than one phrase → propose a split |
| 2 | **Callers** | User, agent, other skills | Who must reach it unprompted |
| 3 | **Invocation** | Model-invoked or user-invoked | Model-invoked if agent or another skill must reach it; else user-invoked (zero context load) |
| 4 | **Triggers** | Distinct branches, 3–6 keywords users type | One trigger per branch; collapse synonyms |
| 5 | **Inputs** | Each input, source, required or optional, resolution when missing | Derive from environment over asking at runtime |
| 6 | **Output contract** | Artifacts, format, location, no-result and incomplete outcomes | Explicit outcome for each edge case |
| 7 | **Variant** | workflow, probes, or free-form | See Variant |
| 8 | **Steps or probes** | Outline with a checkable completion condition each | Demanding, exhaustive criteria where it matters |
| 9 | **Degrees of freedom** | What must stay true vs agent's choice | Exploration high; migration and destructive ops low |
| 10 | **Hard constraints** | MUST/MUST NOT rules, mechanism, failure policy each | Fail closed for mandatory mechanisms; fallback or degradation otherwise |
| 11 | **Gotchas** | External tools, APIs, platform quirks | Only knowledge not findable by looking |
| 12 | **Resources** | scripts, references, templates, assets | Scripts for fragile repeated operations; disclose branch-only reference |
| 13 | **Completion** | Result conditions; completeness sweep needed? | Sweep only for multi-part work |
| 14 | **Placement** | Plugin or folder, name in verb-prefix family | Existing plugin and family first |

## Variant

- **workflow** — steps must run in a fixed order.
- **probes** — agent picks among known techniques by situation.
- **free-form** — creative task, or structure follows the output itself.

## Skill brief

```markdown
# Skill brief: {{name}}

- Purpose: {{one phrase}}
- Target: {{folder path}}; new plugin: {{yes|no}}
- Invocation: {{model|user}}; callers: {{callers}}
- Triggers: {{branches and keywords}}
- Inputs: {{name, source, required|optional, missing handling}}
- Output: {{artifacts, format, location}}; no result: {{outcome}}; incomplete: {{outcome}}
- Variant: {{workflow|probes|free-form}}; reason: {{reason}}
- Steps or probes: {{outline with completion conditions}}
- Degrees of freedom: {{fixed vs free}}
- Constraints: {{MUST/MUST NOT, mechanism, failure policy}}
- Gotchas: {{items or none}}
- Resources: {{scripts, references, templates, assets or none}}
- Completion criteria: {{conditions}}; completeness sweep: {{yes|no}}
- Assumptions and open items: {{items or none}}
```

## Handoff

1. Print the filled brief. *Done when* every field holds a value, `none`, or a listed assumption.
2. Ask the user to confirm or edit. Only the user ends the interview. *Done when* the user confirms.
3. Save the confirmed brief to the session workspace (or print it when no workspace exists) and tell the user to run `/write-skill` with that brief. `write-skill` is user-invoked, so the agent cannot invoke it. *Done when* the brief path or full brief and the `/write-skill` instruction are shown.

## Completion criteria

- Confirmed brief saved or printed in full, with the `/write-skill` handoff instruction, or the user ended the interview with the brief printed.
