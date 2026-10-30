---
name: architect
description: >-
  Sketch types, signatures, and module structure before code, produce one design candidate or synthesize competing multi-model candidates, optionally pause at a user-requested checkpoint, then implement or hand off the sketch. Use for /architect, architect this, design this, /architect interrogate to adversarially attack a change without the design phases, or non-trivial work where jumping to code would lock in the wrong shape.
---

# Architect

Sketch types, function signatures, class shapes, and module boundaries with `not implemented` bodies and pseudocode. Use one runner by default or synthesize multiple model perspectives. Implement against the sketch by default; pause for review only when the user explicitly requests a **checkpoint**. A caller may request a design-only handoff to `/to-spec` instead of direct implementation.

## Options

Accept `arena-agents=1|2|3`; default `1`. Reject other values before launching arena runners. Pass the resolved count to Phase B; retain it for arena re-runs unless the user changes it.

`checkpoint` (or an explicit request to show the design before implementing) is opt-in only when requested by the user; preserve it when forwarded through a calling skill. Do not infer a checkpoint from ordinary design requests.

## Standalone interrogate

Request starts with `interrogate` (`/architect interrogate <request>`) → run only the `interrogate/interrogate.md` procedure; skip the design workflow. Read Repo docs; derive scope, intent, and runnable target from the request; default scope per its Frame. Write findings to `interrogate.md` in the artifact root. Present its Output and the findings path, then stop. Write no sketch or production code; apply nothing.

## Design workflow

Every other request → run the `design/design.md` procedure (Phases A–F). Done when it reaches Phase D hand-off or Phase E working code.

## Bundled files

Resolve every path from this skill's base directory. Read each file fully when its trigger fires.

| File | Load when |
|---|---|
| [design/design.md](design/design.md) | design workflow (any request except standalone interrogate) |
| [design/evidence-routing.md](design/evidence-routing.md) | Phase A technical questions and every Phase C round, including greenfield |
| [references/principles.md](references/principles.md) | any step cites a principle by heading |
| [models.md](models.md) | picking a subagent model for any role |
| [references/subagents.md](references/subagents.md) | spawning any subagent |
| [design/design-red-flags.md](design/design-red-flags.md) | Phase B screening |
| [design/rationale-template.md](design/rationale-template.md) | writing Outputs; give to every runner |
| [how/how.md](how/how.md) | Phase A grounding |
| [how/explorer-prompt.md](how/explorer-prompt.md) | `how/how.md` spawns explorers |
| [how/explainer-prompt.md](how/explainer-prompt.md) | `how/how.md` spawns the explainer |
| [why/why.md](why/why.md) | Phase A, design redefines ownership or layering |
| [why/epistemics.md](why/epistemics.md) | `why/why.md` operating posture and synthesis |
| [why/investigator-prompt.md](why/investigator-prompt.md) | `why/why.md` spawns investigators |
| [why/synthesizer-prompt.md](why/synthesizer-prompt.md) | `why/why.md` spawns the synthesizer |
| [why/source-playbook.md](why/source-playbook.md) | mapping an MCP to its category playbook |
| [why/sources/code-archaeology.md](why/sources/code-archaeology.md) | source control investigator |
| [why/sources/linear.md](why/sources/linear.md) | issue tracker investigator |
| [why/sources/notion.md](why/sources/notion.md) | long-form documents investigator |
| [why/sources/slack.md](why/sources/slack.md) | team chat investigator |
| [why/sources/datadog.md](why/sources/datadog.md) | infrastructure observability investigator |
| [why/sources/sentry.md](why/sources/sentry.md) | error tracking investigator |
| [why/sources/databricks.md](why/sources/databricks.md) | product analytics investigator |
| [why/sources/incident-postmortem.md](why/sources/incident-postmortem.md) | target code looks defensive |
| [arena/arena.md](arena/arena.md) | Phase B |
| [arena/runner-prompt.md](arena/runner-prompt.md) | Phase B runner brief |
| [interrogate/interrogate.md](interrogate/interrogate.md) | standalone interrogate, automatic evidence routing, user picks interrogate, or prototype requests `interrogate` |
| [prototype/prototype.md](prototype/prototype.md) | evidence routing selects Experiment or user picks prototype |

## Artifact location

Write every artifact — grounding, `how`/`why` outputs, arena candidates, judge verdict, synthesis note, sketch, rationale, interrogate findings, review log — under `<repo-root>/tmp/architect-<slug>/`, where `<repo-root>`. Never write them to the session folder or system `/tmp`. Pass absolute paths under this root to every subagent. Research specialist reports may retain a stronger location contract per `design/evidence-routing.md`; index their absolute paths under the artifact root. Phase E code goes in the repo's working tree, not the artifact root.

## Repo docs

Read the repo's architecture, relevant ADRs and Concepts, and glossary before grounding; skip absent ones.

- Sketch MUST conform to accepted ADRs and Concepts.
- Use glossary terms for names; no synonyms.
- Place modules per the documented architecture.
- Deviation → record conflict and reason in rationale open questions; raise in Phase C.
- Pass doc paths to every subagent.
