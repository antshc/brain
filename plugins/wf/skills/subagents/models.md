# Models

Model per subagent role. Value format: `<model> <effort>`; pass the model as `model` and the effort as `reasoning_effort`. A value of `inherit-parent` or `auto` runs the role on the parent chat model (omit `model` and `reasoning_effort`); alias entries in a panel list still count toward its fan-out. Use **Fallback** when **Value** is empty or rejected. Edit **Value** to retune.

For `architect runners`, the ordered list is a model pool; Arena selects seats per its Frame procedure. Other roles keep their existing fan-out. `hunty`, `explainy`, `whyy`, `composy`, `cloudy`, and `weby` are research route agents; only the `research` skill spawns them. `prover` is the prove worker; only the `prove` skill spawns it.

| Role | Value | Fallback |
|---|---|---|
| architect runners | claude-opus-5.5 high, gpt-6.1-sol high, grok-4.7 high | claude-opus-5 high, gpt-6-sol high, grok-4.7 high |
| arena cross-judge pool | gpt-6.1-sol xhigh, claude-opus-5.5 xhigh, grok-4.7 xhigh | claude-opus-5.5 xhigh, grok-4.7 xhigh |
| challenge-this reviewers | claude-opus-5.5 high, gpt-6-sol high, grok-4.7 high | claude-opus-5 medium, gpt-6-sol medium, grok-4.7 medium |
| prover | claude-opus-5.5 medium | gpt-6-sol medium |
| hunty | gpt-6-luna low | claude-haiku-5.5 high |
| explainy | claude-opus-5.5 medium | claude-opus-5 medium |
| whyy | claude-sonnet-5.5 high | claude-sonnet-5 high |
| composy | claude-opus-5.5 medium | claude-opus-5 medium |
| cloudy | gpt-6-luna low | claude-haiku-5.5 high |
| weby | gpt-6-luna low | claude-haiku-5.5 high |
