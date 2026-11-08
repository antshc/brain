---
name: design
description: >-
  Stress-test a plan or design through a decision interview, or write and publish a spec or PRD from resolved context. On explicit request, break a spec into implementation tickets, chart or resume a Wayfinder decision map, or review a technical design for gaps and readiness.
---

# Design

| Mode | Select for | Playbook |
| --- | --- | --- |
| `grill` | Challenge a plan, interview for domain decisions, or resolve a Wayfinder grilling ticket. | [Grill](playbooks/grill.md) |
| `spec` | Synthesize a spec or PRD from the conversation, resolved decisions, or an accepted sketch. | [Spec](playbooks/spec.md) |
| `tickets` | An explicit user request to break a spec into implementation tickets. | [Tickets](playbooks/tickets.md) |
| `wayfinder` | An explicit request to chart or resume a Wayfinder decision map. | [Wayfinder](playbooks/wayfinder.md) |
| `review` | An explicit request to review a technical design for gaps, risks, or implementation readiness. | [Review](playbooks/review.md) |

1. Honor an explicit mode from the user or caller. For a reply to a pending question, review, or confirmation, continue the active route unless the user requests a different mode. Otherwise infer the mode from clear intent. If the request is ambiguous, ask which outcome the user wants and wait.
2. Select `tickets`, `wayfinder`, or `review` only on an explicit user request, including clear natural language or a caller relaying that request. Tickets publication requires separate approval of the current breakdown. Wayfinder automatic runs require their own confirmation.
3. Read only the selected playbook and the references it calls for. Wayfinder loads Grill when its playbook calls for an interview, then resumes the map. Continue from Grill to Spec only for a requested handoff after the closing sweep.

Use `draft-artifact` in `design` mode for authoritative feature-design documents, `architect` for code sketches, and `factory-mode` in `stories` mode for User story breakdown.
