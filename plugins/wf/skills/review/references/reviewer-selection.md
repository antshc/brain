# Reviewer selection

Resolve before spawning. Use a fresh, general-purpose read-only review subagent for each eligible axis. Do not install or invent an agent. Fresh context per axis; the axis contract remains authoritative.

## Model routing

For each eligible axis, choose uniformly at random between GPT Sol and Claude Opus, independently per axis; use `reasoning_effort: high`. Resolve each family to its latest version explicitly advertised by the runtime that supports High. Known IDs: `gpt-6.1-sol`, `claude-opus-5.5`; prefer newer supported versions when advertised. Use exact runtime IDs; never infer version names or substitute another family.

If model discovery is unavailable, try the known IDs. If the selected model rejects High or is unavailable, try the latest advertised version in that family supporting High, then the other eligible family. Skip rejected entries. If neither family supports High, report a delegation blocker. If model selection is unsupported, inherit the current model and disclose `model selection unsupported`; do not claim the requested model or effort took effect. Model choice never reduces coverage/evidence requirements.

Before delegation, record the reviewed SHA and per-axis requested model and effort, including rejections/fallbacks. Record actual model when exposed; never claim an unobservable selection took effect.
