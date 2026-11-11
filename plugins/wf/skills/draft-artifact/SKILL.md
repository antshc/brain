---
name: draft-artifact
description: >-
  Draft a User story, bug report, feature Transfer of Information (TOI), or feature design document from a template. Use for 'write a User story', 'draft a bug report', 'write a TOI', 'write a feature design'. Not for specs or PRDs → `design`; settled ADRs, Concepts, terms → `doc-architecture`.
argument-hint: "story | bug | toi | design"
---

# Draft an Artifact

Honor an explicit artifact type. Otherwise select by the requested result. Ask which type when intent is ambiguous. Use Feature design only when the user explicitly requests a new or updated feature design, including `/draft-artifact design`. A spec or design provided as input is insufficient by itself. Read only the selected tactic and its listed resources in full. Return the tactic's output and apply its own completion checks.

| Tactic | Select when | Procedure | Resources |
| --- | --- | --- | --- |
| Story | Draft one atomic, testable User story | [Story](tactics/story.md) | Output Format in the procedure |
| Bug report | Draft one reproducible report from observed behavior | [Bug report](tactics/bug.md) | Output Format in the procedure |
| TOI | Draft a feature handover for technical teams | [TOI](tactics/toi.md) | [TOI template](templates/toi-template.md) |
| Feature design (`design`) | Create or extend the authoritative feature design from specs and resolved decisions | [Feature design](tactics/feature-design.md) | [Design template](templates/design-template.md), [decision bullets](references/decision-bullet.md) |
