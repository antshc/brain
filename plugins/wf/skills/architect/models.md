# Models

Model per subagent role. Value format: `<model> <effort>`; pass the model as `model` and the effort as `reasoning_effort`. A value of `inherit-parent` or `auto` runs the role on the parent chat model (omit `model` and `reasoning_effort`); alias entries in a panel list still count toward its fan-out. Use **Fallback** when **Value** is empty or rejected. Edit **Value** to retune.

For `architect runners`, the ordered list is a model pool; arena selects seats per its Frame procedure. Other roles keep their existing fan-out.

| Role | Value | Fallback |
|---|---|---|
| architect runners | claude-opus-5.5 high, gpt-6.1-sol high, mai-code-1.1-flash high | claude-opus-5 high, gpt-6-sol high, mai-code-1.1-flash high |
| arena cross-judge pool | gpt-6.1-sol xhigh, claude-opus-5.5 xhigh, mai-code-1.1-flash xhigh | claude-opus-5.5 xhigh, mai-code-1.1-flash xhigh |
| interrogate reviewers | claude-sonnet-5.5 high, gpt-6-luna medium, mai-code-1.1-flash medium | claude-opus-5 medium, gpt-6-sol medium, mai-code-1.1-flash medium |
| prototype builder | claude-sonnet-5.5 high | gpt-6-luna medium |
| how explorer | claude-haiku-5.5 high | gemini-3.8-flash high |
| how explainer | claude-opus-5.5 medium | claude-opus-5 medium |
| why investigators | claude-sonnet-5.5 high  | claude-sonnet-5 high  |
| why synthesizer | claude-opus-5.5 medium | claude-opus-5 medium |
