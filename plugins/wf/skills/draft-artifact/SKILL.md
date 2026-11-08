---
name: draft-artifact
description: >-
  Draft a single User story, reproducible bug report, or feature Transfer of Information (TOI). Use for 'write a User story', 'draft a bug report', 'write a TOI', or feature handover.
argument-hint: "story | bug | toi"
---

# Draft an Artifact

Honor an explicit artifact type. Otherwise select by the requested result. Ask which type when intent is ambiguous. Read only the selected tactic and its listed template in full. Return the tactic's output and apply its own completion checks.

| Tactic | Select when | Procedure | Template |
| --- | --- | --- | --- |
| Story | Draft one atomic, testable User story | [Story](tactics/story.md) | Output Format in the procedure |
| Bug report | Draft one reproducible report from observed behavior | [Bug report](tactics/bug.md) | Output Format in the procedure |
| TOI | Draft a feature handover for technical teams | [TOI](tactics/toi.md) | [TOI template](templates/toi-template.md) |
