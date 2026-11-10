---
name: skill-author
description: >-
  Grill a skill idea into a brief, write, rewrite, or shrink an agent skill, or write a custom coding agent.
disable-model-invocation: true
---

# Skill Author

Own agent-facing authoring end to end: route each request to one selected playbook in `playbooks/`, run it, then run the final check. Writable surface: the target skill folder, the target agent file, or the files given for shrink.

## Routing

Pick the first matching row. Resolve every path from this skill's base directory.

| Mode | Route when | Playbook | Loads | Runs in |
|---|---|---|---|---|
| Grill | Request is a skill idea to define, design, or interview; or a skill request too vague to fill the skill brief | [grill.md](playbooks/grill.md) | none | this session (interactive), then Write |
| Agent | Request is to write or rewrite a custom coding agent definition (`*.agent.md`, an `agents/` file, a planner or decomposer agent) | [agent.md](playbooks/agent.md) | [agent-best-practices.md](references/agent-best-practices.md), [agent-examples.md](references/agent-examples.md), [agent-platforms.md](references/agent-platforms.md), [agent.template.md](templates/agent.template.md); planner only: [planner.template.md](templates/planner.template.md), [planner-output.template.md](templates/planner-output.template.md) | this session |
| Shrink | Request is to shrink, tighten, compress, or condense existing skill, agent, or instructions files | [shrink.md](playbooks/shrink.md) | [wording.md](references/wording.md), [best-practices.md](references/best-practices.md) | fresh subagent |
| Write | Everything else: skill brief, free-text skill request, rewrite of an existing skill | [draft.md](playbooks/draft.md), then [shrink.md](playbooks/shrink.md) | [best-practices.md](references/best-practices.md), [wording.md](references/wording.md), [SKILL.template.md](templates/SKILL.template.md) | fresh subagent per phase |

## Constraints

- **MUST** run the Draft phase and the Shrink phase each in a separate fresh subagent; the parent never drafts or shrinks a skill inline. Rationale: isolated context keeps the shrink pass independent and stops the draft rushing toward later phases. If subagents are unavailable, stop and report the blocker.
- Pass the user input verbatim; restate nothing from the playbooks in prompts.
- Pass absolute paths of the phase playbook and every file in its Loads cell.

## Workflow

1. **Route.** Select the mode per Routing. Take the brief or request verbatim and any target path; shrink mode: collect the file paths. *Done when* mode and inputs are known; ask only when no target can be derived from input or repository layout.
2. **Grill** (grill mode). Read and follow `playbooks/grill.md` in this session. *Done when* the user confirms the brief → run Draft phase with the confirmed brief as input; or the user ends the interview → Report.
3. **Agent** (agent mode). Read and follow `playbooks/agent.md` in this session, reading every file in its Loads cell in full. *Done when* its Output is produced → Final check.
4. **Draft phase** (write mode). Launch a fresh subagent instructed to read and follow `playbooks/draft.md`, given the input verbatim, the target path, and absolute paths of `playbooks/draft.md` and its Loads files. It returns per draft.md Return. *Done when* every returned path exists on disk.
5. **Shrink phase** (write and shrink modes). Launch a new fresh subagent instructed to read and follow `playbooks/shrink.md` on the drafted paths (write mode) or given paths (shrink mode), given absolute paths of `playbooks/shrink.md` and its Loads files. It returns per shrink.md Return. *Done when* the report lists every file with before → after counts.
6. **Final check.** Read the result files. Confirm Completion criteria, plus the playbook's Completion criteria in agent mode; fix a failing item by re-running the owning phase or mode with the defect named. *Done when* all criteria hold or a remaining defect is reported.
7. **Report.** Return mode and paths, then per mode: write → blocks, invocation mode, assumptions, shrink deltas, flagged items; shrink → shrink deltas, flagged items; agent → agent.md Output; grill ended early → the brief. *Done when* the report is shown.

## Completion criteria

- Every target `SKILL.md` has valid frontmatter: `name` matches folder; description passes the forbidden description character table in best-practices.md.
- `SKILL.md` body under 300 lines; no template placeholder or `<!-- @: -->` directive left in a produced skill or agent.
- Every relative link resolves inside its own skill folder.
- Shrink report shows no unflagged lost behavior item.
- New plugin, when created, is registered alongside its siblings.
