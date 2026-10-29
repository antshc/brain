# Models

Model per subagent role. Value format: `<model> <effort>`; pass the model as `model` and the effort as `reasoning_effort`. A value of `inherit-parent` or `auto` runs the role on the parent chat model (omit `model` and `reasoning_effort`); alias entries in a panel list still count toward its fan-out. Use **Fallback** when **Value** is empty or rejected. Edit **Value** to retune.

| Role | Value | Fallback |
|---|---|---|
| architect runners | claude-opus-5.5 high, gpt-6.1-sol high, grok-4.7 high | claude-opus-5 high, gpt-6-sol high, grok-4.6 high |
| arena cross-judge pool | gpt-6.1-sol xhigh, claude-opus-5.5 xhigh, grok-4.7 xhigh | claude-opus-5.5 xhigh, grok-4.7 xhigh |
| interrogate reviewers | claude-sonnet-5.5 high, gpt-6-luna medium, grok-4.7 low | claude-opus-5 high, gpt-6-sol high, grok-4.6 high |
| prototype builder | claude-opus-5.5 high | claude-opus-5 high |
| how explorer | claude-haiku-5.5 high | gemini-3.8-flash high |
| how explainer | claude-opus-5.5 high | claude-opus-5 high |
| why investigators | claude-sonnet-5.5 medium | claude-sonnet-5 medium |
| why synthesizer | claude-opus-5.5 medium | claude-opus-5 medium |
