---
name: subagents
description: >-
  Dispatch independent workers with role-based models and isolated outputs. Use Arena to compare independent candidates and synthesize findings, or Swarm to partition work or race workers.
---

# Subagents

## Actions

| Action | Inputs | Return |
| --- | --- | --- |
| **Dispatch** | Worker briefs with scope, tools, constraints, evidence and expected output. Optional role or ordered role pool, explicit model, worktree requirements, and model fallback. | Reports or blockers per brief, model choices and worktree paths. |
| **Arena** | Same task for all runners, output root, artifact contract, grounding, runner role/count, rubric inputs, screening and verification rules, and optional incumbent and correction context. | Synthesis path, candidate paths, judge or skip reason, and verified findings or blockers. |
| **Swarm** | Task, worker count, partition/race/mixed shape, done condition and required evidence. | One report covering results, issues and gaps. |

- **Dispatch** → apply Dispatch and Model selection below.
- **Arena** → read [arena.md](arena.md) in full. Use its dispatch rules within the same run.
- **Swarm** or `/subagents swarm <task>` → read [swarm.md](swarm.md) in full.
- A named role or model pool → read [models.md](models.md) in full before selection. Explicit caller models take precedence. With neither a role nor an explicit model, use harness defaults.

## Dispatch

1. **Brief.** Pass file pointers, task, scope, tools, constraints and expected output. Default to a full-capability worker; honor caller requirements such as read-only or MCP access. Send Explore requests verbatim to `hunter`. If Hunter is unavailable, report the blocked evidence request and continue independent work. Other briefs that name a skill **MUST** go to a skill-capable agent, such as `general-purpose` with edits forbidden when read-only. The built-in `explore` agent can handle plain grep or LSP checks outside the Explore request contract. Give writers separate output paths. When isolation is requested, *run `git` Worktrees tactic to create an isolated worktree* per worker unless the caller supplies a verified checkout. Retain each ownership record outside the worktrees and apply only explicitly scoped uncommitted changes. Report a blocker if required isolation is unavailable; use a shared read-only checkout only when the caller permits it.
2. **Launch.** Run independent workers together in background, including when steering a running worker. Serialize shared writes. Use prose to specify what each worker does. Preserve caller-specific fallback and retry rules.
3. **Return.** Drain the workers and return terminal results or blockers with their artifact/worktree paths and actual models. Pass worktree ownership records to the caller for verification and cleanup. The caller verifies results, reviews any diffs, and writes its own summary. For a second opinion, give a different model the same prompt.

## Model selection

Before spawning a named role, start with its configured value or fallback and adjust reasoning effort to the job. Raise one step for the hardest work, lower one for judgment and two or more for routine work. Keep the model family and use its nearest supported effort. For `auto` or `inherit-parent`, omit model and effort.

If the adjusted model or effort is rejected, retry the role's original value if still valid and report the change. If rejected again, follow the calling action's fallback. Skip models already rejected as invalid. Without a specified fallback, use the closest valid model of that family from the tool's error or omit model and effort for the parent defaults. Report fallback use and any remaining blocker.

For an ordered panel, choose the first N pool entries. Use the fallback pool when the value is absent. Fill missing seats with the last entry or parent defaults when the pool is empty, and report it. On rejection, try the role fallback for that model family, then the closest valid model of the same family from the tool error. Drop and report the seat if none is available. Families use the `claude-*`, `grok-*`, `gpt-*`, and `gemini-*` prefixes. Keep fallbacks within the requested seats.

## Fresh subagents by default

Give new work, fixes, follow-ups and retries to a fresh worker with the original brief, later directives, and the prior report and branch. Reuse a worker only when the work needs costly state it alone holds, such as an uncommitted checkout or a running process. Stopping or holding a worker is allowed without reuse.
