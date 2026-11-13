---
name: draft-artifact
description: >-
  Draft a User story, bug report, or feature Transfer of Information (TOI) from a template. Use for 'write a User story', 'draft a bug report', 'write a TOI'. Not for HLDs, feature designs, specs or PRDs → `design`; settled ADRs, Concepts, terms → `doc-architecture`.
argument-hint: "story | bug | toi"
---

# Draft an Artifact

Honor an explicit artifact type. Otherwise select by the requested result. Ask which type when intent is ambiguous. Read only the selected tactic and its listed resources in full. Return the tactic's output and apply its own completion checks.

| Tactic | Select when | Procedure | Resources |
| --- | --- | --- | --- |
| Story | Draft one atomic, testable User story | [Story](tactics/story.md) | Output Format in the procedure |
| Bug report | Draft one reproducible report from observed behavior | [Bug report](tactics/bug.md) | Output Format in the procedure |
| TOI | Draft a feature handover for technical teams | [TOI](tactics/toi.md) | [TOI template](templates/toi-template.md) |
