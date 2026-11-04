# Subagents

Rules for every subagent this skill spawns. A procedure that prescribes its own agent type (`how`, `why`, `arena`, `interrogate`) keeps it.

## Defaults

`mode: "background"` (also for a steer of a running agent, because a foreground call holds your turn while other reports wait), a full-capability agent type (`explore` is read-only and has no MCP), file pointers not inlined context, explicit model per role from `models.md`.

## Match the model to the job

Before each spawn, start from the role's value and pick the reasoning level the job needs. Raise it one step, up to max, for the hardest or subtlest work. Lower it one step for judgment and two or more steps for routine work. Change only the effort level, and keep the model family the role names, so a diverse panel stays diverse. If the model does not offer that effort, use its nearest supported effort. A role on `auto` or `inherit-parent` stays on the parent model.

If the subagent tool rejects the adjusted model or effort, do not try another adjusted value. Use the role's value and say so. If the tool rejects that too, continue with the calling procedure's fallback. A value counts as rejected once a tool error says the model is not valid, or leaves it out of its list of valid values. Never pass a rejected model, and skip any fallback whose model is already rejected. When the calling procedure has no fallback, use the closest valid model of the role's family from the error's list, or omit `model` so the subagent runs on the parent model when the list has none. When the fallback runs out of models without saying what to do next, omit `model` too. Say so in both cases.

## Ownership

You own every subagent's work. Review the diff and write your own summary; don't pass through what it said. A second opinion is the same prompt against a different model. Agreement is high-signal.

## Fresh subagents by default

Give new work to a fresh subagent with consolidated scope: the original brief, every later directive, and the prior agent's report and branch. This holds for a fix round, a follow-up, a retry, and the next queue item. Resume or message an existing subagent only when the new work strictly needs state that lives in that agent and is costly to move: its local checkout, its uncommitted changes, or a process it still runs. A stop or hold order to a running agent is not reuse. Interrupt-chained resumes silently drop directives, so fire a fresh subagent with consolidated scope rather than trusting a "done" summary.
