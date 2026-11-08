# Reviewer selection

Resolve before spawning. Use a fresh, general-purpose read-only review subagent for each eligible axis. Do not install or invent an agent. Fresh context per axis; the axis contract remains authoritative.

## Model routing

Take the review level (`low`, `medium`, `high`) from the user's invocation or caller configuration; default `medium`. An unrecognized level fails before delegation; ask the user instead of guessing.

Look up the level's model pool in the *Model selection* table. For each eligible axis, pick one pool entry uniformly at random, independently per axis. If the runtime rejects the picked entry, pick randomly among the remaining entries of the same pool; when the pool is exhausted, inherit the current model and disclose the limitation. Do not invent IDs absent from the table or caller configuration. If model selection is unsupported, inherit and record `model selection unsupported`. Model choice never reduces coverage/evidence requirements.

Before delegation, record: reviewed SHA, review level, and per axis the requested model and effort plus any rejection/fallback. Record actual model when exposed; never claim an unobservable selection took effect.
