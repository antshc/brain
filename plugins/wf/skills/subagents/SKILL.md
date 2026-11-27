---
name: subagents
description: >-
  Select the model and reasoning effort for a named subagent role or ordered model panel, or run an Arena comparison of independent candidates. Use for 'which model for this role', 'pick the panel models', 'compare independent designs'.
---

# Subagents

| Action | Use | Load |
|---|---|---|
| **Model selection** | Model, effort, and optional context tier for a named role or ordered panel; the caller spawns the worker | [models.md](models.md) |
| **Arena** | Same task to independent runners, cross-judge, pick a base, graft, verify | [arena.md](arena.md), [models.md](models.md) |

Read the listed files in full before acting. [models.md](models.md) is the user's persistent model configuration: pass its resolved model and effort as `model` and `reasoning_effort`, and its context tier as `context_tier` when set. Explicit caller values take precedence. Unknown role and no explicit model → omit model and effort for harness defaults. Only Arena launches workers.

## Load and follow skills

For every call to the `principles` skill, load and follow its skill content in full, then read each selected principle file through EOF before applying it. Reuse complete content already loaded for the same revision.

## Model selection

Before spawning a named role, start with its configured value or fallback and adjust reasoning effort to the job. Raise one step for the hardest work, lower one for judgment and two or more for routine work. Keep the model family and use its nearest supported effort. Pass the configured context tier unchanged. For `auto` or `inherit-parent`, omit model and effort.

If the adjusted model or effort is rejected, retry the role's original value if still valid and report the change. If rejected again, follow the caller's fallback. Skip models already rejected as invalid. Without a specified fallback, use the closest valid model of that family from the tool's error or omit model and effort for the parent defaults. Report fallback use and any remaining blocker.

## Ordered panels

For an ordered panel, choose the first N pool entries. Use the fallback pool when the value is absent. Fill missing seats with the last entry or parent defaults when the pool is empty, and report it. On rejection, try the role fallback for that model family, then the closest valid model of the same family from the tool error. Drop and report the seat if none is available. Families use the `claude-*`, `grok-*`, `gpt-*`, and `gemini-*` prefixes. Keep fallbacks within the requested seats.
