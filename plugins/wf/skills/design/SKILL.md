---
name: design
description: >-
  Stress-test a plan through a decision interview, or publish a spec or PRD. Use for 'grill this', 'write a spec'; on request, break a spec into tickets, chart a Wayfinder map, or review a design. Not for code shape → `architect`; stories, bugs, TOIs, feature designs → `draft-artifact`.
---

# Design

| Mode | Select for | Playbook |
| --- | --- | --- |
| `grill` | Challenge a plan, interview for domain decisions, or resolve a Wayfinder grilling ticket. | [Grill](playbooks/grill.md) |
| `sketch` | Draft one usage-first code sketch: types, signatures with `not implemented` bodies, module map, rationale. Select only on explicit `sketch`; `architect` owns code shape otherwise. | [Sketch](playbooks/sketch.md) |
| `spec` | Synthesize a spec or PRD from the conversation, resolved decisions, or an accepted sketch. | [Spec](playbooks/spec.md) |
| `tickets` | An explicit user request to break a spec into implementation tickets. | [Tickets](playbooks/tickets.md) |
| `wayfinder` | An explicit request to chart or resume a Wayfinder decision map. | [Wayfinder](playbooks/wayfinder.md) |
| `review` | An explicit request to review a technical design for gaps, risks, or implementation readiness. | [Review](playbooks/review.md) |

1. Honor an explicit mode from the user or caller. For a reply to a pending question, review, or confirmation, continue the active route unless the user requests a different mode. Otherwise infer the mode from clear intent. If the request is ambiguous, ask which outcome the user wants and wait.
2. Select `tickets`, `wayfinder`, or `review` only on an explicit user request, including clear natural language or a caller relaying that request. Tickets publication requires separate approval of the current breakdown. Wayfinder automatic runs require their own confirmation.
3. Read only the selected playbook and the references it calls for. Wayfinder loads Grill when its playbook calls for an interview, then resumes the map. Continue from Grill to Spec only for a requested handoff after the closing sweep.

Use `draft-artifact` in `design` mode for authoritative feature-design documents, `architect` for multi-phase or competing-candidate code designs, and `factory-mode` in `stories` mode for User story breakdown.
