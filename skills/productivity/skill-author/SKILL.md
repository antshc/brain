---
name: skill-author
description: >-
  Author agent-facing documents and custom coding agents. Use for 'define a skill', 'write a skill', 'review agent instructions', or 'shrink agent docs'.
---

# Skill Author

Apply guidance to the current task or execute one authoring playbook, then check results. Writable surface: requested agent-facing documents, target skill folder, or target agent file.

## Routing

Honor an explicit mode; otherwise pick the first matching row. Resume the active mode for replies to its prompts. Unknown mode → report it and available modes. Resolve every path from this skill's base directory. For combined requests, apply Guidance first, then authoring modes in dependency order; complete each before selecting the next.

| Mode | Route when | Playbook | Loads | Runs in |
|---|---|---|---|---|
| `guidance` | Caller requests authoring rules for an ongoing writing, editing or review task, including a repository instruction invoking this skill | Inline Guidance | [best-practices.md](references/best-practices.md), [wording.md](references/wording.md) | this session |
| Grill | Request is a skill idea to define, design, or interview; or a skill request too vague to fill the skill brief | [grill.md](playbooks/grill.md) | none | this session (interactive), then Write |
| Agent | Request is to write or rewrite a custom coding agent definition (`*.agent.md`, an `agents/` file, a planner or decomposer agent) | [agent.md](playbooks/agent.md) | [best-practices.md](references/best-practices.md), [wording.md](references/wording.md), [agent-best-practices.md](references/agent-best-practices.md), [agent-examples.md](references/agent-examples.md), [agent-platforms.md](references/agent-platforms.md), [agent.template.md](templates/agent.template.md); planner only: [planner.template.md](templates/planner.template.md), [planner-output.template.md](templates/planner-output.template.md) | this session |
| Shrink | Request is to shrink, tighten, compress, or condense existing skill, agent, or instructions files | [shrink.md](playbooks/shrink.md) | [wording.md](references/wording.md), [best-practices.md](references/best-practices.md) | fresh subagent |
| Write | Everything else: skill brief, free-text skill request, rewrite of an existing skill | [draft.md](playbooks/draft.md), then [shrink.md](playbooks/shrink.md) | [best-practices.md](references/best-practices.md), [wording.md](references/wording.md), [SKILL.template.md](templates/SKILL.template.md) | fresh subagent per phase |

## Guidance

Read best-practices.md and wording.md in full; apply their rules within the caller's current task, scope and output contract. Return the requested documents or review findings when they meet applicable rules, or report a named blocker. Do not start Draft, Shrink or an interview merely to load rules; return to the caller.

## Repository overrides

Read applicable repository instructions and apply independent overrides. A stub invoking this same skill is already satisfied by this invocation; never invoke this skill recursively to follow the stub. Pass this rule and the applicable overrides to phase workers.

## Composition resources

For skill composition, read Route composition in [best-practices.md](references/best-practices.md). Pass Draft absolute paths of [playbook.template.md](templates/playbook.template.md) and [tactic.template.md](templates/tactic.template.md); read and fill only for extracted procedures or techniques, respectively.

## Constraints

- **MUST** run Draft and Shrink in separate fresh subagents; never inline. Isolation keeps Shrink independent and Draft focused. If subagents are unavailable, stop and report the blocker.
- Pass the user input verbatim; restate nothing from the playbooks in prompts.
- Pass absolute paths of the phase playbook and every file in its Loads cell.

## Workflow

1. **Route.** Select per Routing; collect verbatim input and target paths. Ask only if input and repository layout cannot supply a target. Guidance → execute Guidance and return to the caller; other modes continue below. *Done when* mode and inputs are known.
2. **Grill** (grill mode). Follow the selected playbook interactively. User confirms brief → Draft phase with that brief; user ends interview → Report.
3. **Agent** (agent mode). Follow the selected playbook here; read every Loads file fully. Its Output produced → Final check.
4. **Draft phase** (write mode). Delegate reading and following `playbooks/draft.md` with input and paths per Constraints; require its Return. *Done when* every returned path exists.
5. **Shrink phase** (write and shrink modes). Delegate reading and following `playbooks/shrink.md` on drafted or given paths, per Constraints; require its Return. *Done when* every file has before → after counts.
6. **Final check.** Read results against Completion criteria and, for Agent, its playbook criteria. Re-run the owning phase or mode with named defects. *Done when* criteria pass or remaining defects are reported.
7. **Report.** Return mode and paths, then per mode: write → blocks, invocation mode, assumptions, shrink deltas, flagged items; shrink → shrink deltas, flagged items; agent → agent.md Output; grill ended early → the brief. *Done when* the report is shown.

## Completion criteria

- Every target `SKILL.md` has valid frontmatter: `name` matches folder; description passes the forbidden description character table in best-practices.md.
- Executable calls follow Skill invocation syntax in best-practices.md: standalone or compact under a named-dependency loading contract available to the executing agent; optional rationale carries no mandatory behavior.
- `SKILL.md` body under 300 lines; no template placeholder or `<!-- @: -->` directive left in a produced skill or agent.
- Every relative link resolves inside its own skill folder; every conditional playbook, tactic, and reference has a direct body link and loading condition, without loading chains.
- Every route has an unambiguous trigger, procedure (inline or playbook), output contract, and selection/ambiguity/continuation/combined-request policy; every tactic has a trigger, consumer, and result. Simple skills retain only justified blocks/files.
- Shrink report shows no unflagged lost behavior item.
- New plugin, when created, is registered alongside its siblings.
