---
name: 'suggest'
description: 'Analyzes provided information and proposes improvements, options, or ideas, each with supporting reasoning. Use when asked to suggest, improve, brainstorm, list options or alternatives, or propose ideas.'
---
Analyze the provided information, then propose what fits the request:

- **Improvements:** actionable changes to existing content, each with reasoning.
- **Options:** distinct alternatives for a decision; per option state trade-offs (pros, cons) and when it fits. Mark the recommended one.
- **Ideas:** new directions or additions beyond the current content, each with expected value.

Default to improvements; add options or ideas when the request is open-ended, mentions alternatives, or the input is a plan/decision rather than finished content.

You MUST NOT apply any suggestions or update files without user approval.