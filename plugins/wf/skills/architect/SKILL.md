---
name: architect
description: >-
  Sketch types, signatures, and module structure before code, produce one design candidate or synthesize competing multi-model candidates, optionally pause at a user-requested checkpoint, then implement or hand off the sketch. Use for /architect, architect this, design this, /architect sketch to write only the sketch without implementing, /architect interrogate to adversarially attack a change without the design phases, or non-trivial work where jumping to code would lock in the wrong shape. Also designs deep module interfaces, finds deepening opportunities, places seams, and compares Design It Twice options.
---

# Architect

Sketch types, function signatures, class shapes, and module boundaries with `not implemented` bodies and pseudocode. Use one runner by default or synthesize multiple model perspectives. Implement against the sketch by default; pause for review only when the user explicitly requests a **checkpoint**. A caller may request a design-only handoff to `/to-spec` instead of direct implementation.

## Options

Accept `arena-agents=1|2|3`; default `1`. Reject other values before launching arena runners. Pass the resolved count to Phase B; retain it for arena re-runs unless the user changes it.

`checkpoint` (or an explicit request to show the design before implementing) is opt-in only when requested by the user; preserve it when forwarded through a calling skill. Do not infer a checkpoint from ordinary design requests.

## Standalone interrogate

Request starts with `interrogate` (`/architect interrogate <request>`) → run only the `interrogate/interrogate.md` procedure; skip the design workflow. Read Repo docs; derive scope, intent, and runnable target from the request; default scope per its Frame. Write findings to `interrogate.md` in the artifact root. Verified contract findings → run Deep-module design and add each recommended interface to `interrogate.md` as a proposed fix. Present its Output and the findings path, then stop. Write no sketch or production code; apply nothing.

## Deep-module design

Route here when:

- **User request**: design or deepen a module interface, find deepening opportunities, decide seam placement, or make code more testable or AI-navigable. Run standalone; user also asks to sketch → Sketch only; to implement → Design workflow.
- **Contract finding**: Interrogate (standalone, automatic, or checkpoint reply) returns a verified finding on a contract: interface, invariant, ordering, error mode, required configuration, seam placement, or adapter. Resolve it here before proposing or applying its correction.

Interrogate itself never runs this route; it only reports findings.

1. Read `principles/deep-modules.md`. Done when its vocabulary names the module, interface, seam, and dependency categories.
2. Run the `principles/design-it-twice.md` procedure on the target module. Done when `comparison.md` holds a recommendation.
3. Hand back per its Hand back section.

## Sketch only

Route here when the user asks only for a sketch (`/architect sketch <request>`, "write the sketch", "sketch it, don't implement"), or asks to sketch a Deep-module design recommendation. Run the `sketch/sketch.md` procedure; never run the design workflow. Done when its Completion criteria hold.

## Design workflow

Every other request → run the `design/design.md` procedure (Phases A–F). Done when it reaches Phase D hand-off or Phase E working code.

## Bundled files

Resolve every path from this skill's base directory. Read each file fully when its trigger fires.

| File | Load when |
|---|---|
| [design/design.md](design/design.md) | Design workflow, or Sketch only resume |
| [sketch/sketch.md](sketch/sketch.md) | Sketch only route |
| [design/evidence-routing.md](design/evidence-routing.md) | Phase A technical questions and every Phase C round, including greenfield |
| [principles/boundary-discipline.md](principles/boundary-discipline.md) | a step cites *Boundary discipline* |
| [principles/encode-lessons-in-structure.md](principles/encode-lessons-in-structure.md) | a step cites *Encode lessons in structure* |
| [principles/exhaust-the-design-space.md](principles/exhaust-the-design-space.md) | a step cites *Exhaust the design space* |
| [principles/fix-root-causes.md](principles/fix-root-causes.md) | a step cites *Fix root causes* |
| [principles/foundational-thinking.md](principles/foundational-thinking.md) | a step cites *Foundational thinking* |
| [principles/in-your-own-words.md](principles/in-your-own-words.md) | a step cites *In your own words* |
| [principles/laziness-protocol.md](principles/laziness-protocol.md) | a step cites *Laziness protocol* |
| [principles/make-operations-idempotent.md](principles/make-operations-idempotent.md) | a step cites *Make operations idempotent* |
| [principles/minimize-reader-load.md](principles/minimize-reader-load.md) | a step cites *Minimize reader load* |
| [principles/outcome-oriented-execution.md](principles/outcome-oriented-execution.md) | a step cites *Outcome-oriented execution* |
| [principles/prove-it-works.md](principles/prove-it-works.md) | a step cites *Prove it works* |
| [principles/redesign-from-first-principles.md](principles/redesign-from-first-principles.md) | a step cites *Redesign from first principles* |
| [principles/separate-before-serializing-shared-state.md](principles/separate-before-serializing-shared-state.md) | a step cites *Separate before serializing shared state* |
| [principles/subtract-before-you-add.md](principles/subtract-before-you-add.md) | a step cites *Subtract before you add* |
| [principles/deep-modules.md](principles/deep-modules.md) | Deep-module design route, or a step cites *Deep modules* |
| [principles/design-it-twice.md](principles/design-it-twice.md) | Deep-module design route |
| [models.md](models.md) | picking a subagent model for any role |
| [arena/subagents.md](arena/subagents.md) | spawning any subagent |
| [design/design-red-flags.md](design/design-red-flags.md) | Phase B screening, or `sketch/sketch.md` step 5 |
| [design/rationale-template.md](design/rationale-template.md) | writing Outputs; give to every runner; `sketch/sketch.md` step 6 |
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
| [arena/runner-prompt.md](arena/runner-prompt.md) | Phase B runner brief, or `sketch/sketch.md` step 4 discipline |
| [interrogate/interrogate.md](interrogate/interrogate.md) | standalone interrogate, automatic evidence routing, user picks interrogate, or prove requests `interrogate` |
| [prove/prove.md](prove/prove.md) | evidence routing selects Experiment or user picks prove |

## Artifact location

Write every artifact — grounding, `how`/`why` outputs, arena candidates, judge verdict, synthesis note, sketch, rationale, interrogate findings, deep-module options, review log — under `<repo-root>/tmp/architect-<slug>/`, where `<repo-root>`. Never write them to the session folder or system `/tmp`. Pass absolute paths under this root to every subagent. Research specialist reports may retain a stronger location contract per `design/evidence-routing.md`; index their absolute paths under the artifact root. Phase E code goes in the repo's working tree, not the artifact root.

### Artifact layout

```
<artifact-root>/
  task.md                      arena task, requirements, human decisions
  grounding-*.md               Phase A outputs (grounding-how.md, ...)
  candidate-<n>/               one per runner
    rationale.md
    module-map.md
    sketch/                    source files, never one markdown holding code
  synthesis/                   same shape as a candidate, plus synthesis-note.md
  arena-r<k>/                  correction re-runs: candidate-<n>/, synthesis/
  deep-modules/                Deep-module design: problem.md, option-<n>.md, comparison.md
  review-log.md
```

- `sketch/` holds real source files in the repo's primary language (e.g. `.cs`), grouped per module or concern; hook-point edits to existing files are diff-like snippets in source files. Prose and code never share a file; `rationale.md` and `module-map.md` link to sketch files.
- `module-map.md` lists each new, modified, or deleted file by real repo-relative path, with its sketch file.
- Interrogate and prove artifacts stay under the artifact root per their procedures.

## Repo docs

Read the repo's architecture, relevant ADRs and Concepts, and glossary before grounding; skip absent ones.

- Sketch MUST conform to accepted ADRs and Concepts.
- Use glossary terms for names; no synonyms.
- Place modules per the documented architecture.
- Deviation → record conflict and reason in rationale open questions; raise in Phase C.
- Pass doc paths to every subagent.
