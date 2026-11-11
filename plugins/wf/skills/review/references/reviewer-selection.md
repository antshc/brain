# Reviewer selection

Independently per eligible axis, choose GPT Sol or Claude Opus with equal probability and `reasoning_effort: high`. Use the latest runtime-advertised version supporting High; without discovery, try `gpt-6.1-sol` or `claude-opus-5.5`. On rejection, try the other family; if neither works, report a blocker. If model selection is unsupported, inherit and disclose that limitation. Record each axis's requested model, actual model when exposed, and fallbacks.
