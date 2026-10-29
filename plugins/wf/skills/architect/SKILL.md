---
name: architect
description: >-
  Sketch types, signatures, and module structure before code, synthesize competing multi-model design candidates, loop user corrections into the sketch, then hand off to spec. Use for /architect, architect this, design this, or non-trivial work where jumping to code would lock in the wrong shape.
---

# Architect

Sketch types, function signatures, class shapes, and module boundaries with `not implemented` bodies and pseudocode. Synthesize across multiple model perspectives, review the sketch with the user until accepted, then hand off to spec and implementation. Never write production code.

## Bundled files

Resolve every path from this skill's base directory. Read each file fully when its trigger fires.

| File | Load when |
|---|---|
| [references/principles.md](references/principles.md) | any step cites a principle by heading |
| [models.md](models.md) | picking a subagent model for any role |
| [references/subagents.md](references/subagents.md) | spawning any subagent |
| [references/design-red-flags.md](references/design-red-flags.md) | Phase B screening |
| [references/rationale-template.md](references/rationale-template.md) | writing Outputs; give to every runner |
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
| [interrogate/interrogate.md](interrogate/interrogate.md) | Phase C, user picks interrogate |
| [prototype/prototype.md](prototype/prototype.md) | Phase C, user picks prototype |

## Artifact location

Write every artifact — grounding, `how`/`why` outputs, arena candidates, judge verdict, synthesis note, sketch, rationale, interrogate findings, review log — under `<repo-root>/tmp/architect-<slug>/`, where `<repo-root>`. Never write them to the session folder or system `/tmp`. Pass absolute paths under this root to every subagent.

## Repo docs

Read the repo's architecture, relevant ADRs and Concepts, and glossary before grounding; skip absent ones.

- Sketch MUST conform to accepted ADRs and Concepts.
- Use glossary terms for names; no synonyms.
- Place modules per the documented architecture.
- Deviation → record conflict and reason in rationale open questions; raise in Phase C.
- Pass doc paths to every subagent.

## Start

Open a todolist with one entry per phase before starting.

1. Ground
2. Sketch
3. Review
4. Hand off

## Phase A: Ground the problem

Build a real mental model of every system the new code touches, starting from Repo docs. Run the `how/how.md` procedure over the relevant subsystems. Naming a file isn't grounding. Produce the architectural explanation `how/how.md` prescribes. If the design redefines ownership or layering, also run the `why/why.md` procedure on the existing shape so the rationale becomes a constraint, not a guess.

Skip Phase A only when the work is genuinely greenfield with no surrounding system to integrate.

## Phase B: Sketch

Run the `arena/arena.md` procedure with the design-sketch task and the Phase A grounding artifacts. Pass `arena/runner-prompt.md` as each runner's prompt, plus the absolute paths of this `SKILL.md`, `references/rationale-template.md`, and `references/principles.md`.

Take the runners from the `architect runners` role in `models.md`. Alias and rejected entries follow the runner rules in arena Phase A.

Design it twice. Require at least two structurally distinct candidates before synthesis, even when the first looks sufficient. This is the *Exhaust the design space* principle made concrete. Whole-shape alternatives, not point fixes inside one shape.

Screen every candidate against `references/design-red-flags.md` and the Repo docs rules before synthesis. Assume the next contributor is an agent that sees only the files it opened, copies the nearest example, and takes the shortest path that compiles. Prefer the design where a change that looks right from one file is right for the whole repo.

Compare viable candidates on interface depth. Prefer the design that hides more complexity behind a smaller, simpler public surface. A rich interface can keep call chains short by concentrating capability instead of scattering it across layers.

Arena returns one synthesized design package. Its synthesis decision fills the rationale's "Synthesis decision" section.

## Phase C: Review loop

Loop until the user explicitly accepts the sketch. Ask in plain chat; MUST NOT use the VS Code ask/questions tool. Never write production code. Prototype code is disposable evidence kept in a worktree, never part of the sketch.

Each round:

1. Present in chat: usage sketch, module map, key types and signatures, synthesis decision, the rationale's open questions and risks, and absolute paths of the base candidate's sketch, the synthesized design, and the rationale.
2. Offer these replies verbatim, then stop and wait for the user:
   ```
   Reply with one:
   - **corrections**: `Q2 → keep per-tenant tables` (edits sketch, design, rationale; no arena re-run)
   - **interrogate**: `risk 1; intent: ...; target: DynamoDB Local` (adversaries try to prove it)
   - **prototype**: `GSI backfill; target: DynamoDB Local` (throwaway build in a worktree, then interrogated)
   - **ask**: `why does X own Y?` (grounds the answer, then corrections)
   - **accept**: hand off to `/to-spec`
   ```
3. Act on the reply:
   - **Corrections** → apply them directly; never re-run arena, even for shape changes. Rewrite the base candidate's sketch in place, then update the synthesized design and rationale (usage sketch, affected sections, synthesis decision, alternatives, open questions) so all three agree. Screen the rewrite against `references/design-red-flags.md` and the Repo docs rules; surface hits as questions. Append the correction and resulting changes to `review-log.md` in the artifact root. Start the next round.
   - **Interrogate** → run the `interrogate/interrogate.md` procedure on the current sketch. Present findings as proposed corrections; apply only those the user accepts, as above. Start the next round.
   - **Prototype** → run the `prototype/prototype.md` procedure on the question in the reply. Present its output; apply only the proposed corrections the user accepts, as above, citing the evidence in the rationale. Start the next round.
   - **Ask** → answer from Phase A grounding, running `how/how.md` or `why/why.md` when needed; present the answer, then start the next round.
   - **Accept** → go to Phase D.

Ambiguous reply → ask which of the five it is; never treat it as acceptance.

## Phase D: Hand off

Stop. Tell the user the accepted sketch is ready and to run `/to-spec` with the target branch and Initiative ID; that skill turns the synthesized design and base candidate sketch from this conversation into a published spec issue. Do not draft the spec yourself.

After the spec issue is published, offer to run `/implement-spec <spec issue URL>` to implement the spec through its ticket graph into a draft PR. Run it only when the user confirms.

## Outputs

The caller's usage is written first and the type sketch derived from it. One file with new types and signatures for small changes. Module map plus type definitions for larger work. The rationale ships alongside, shaped per `references/rationale-template.md`, including the usage sketch and the synthesis decision. Sketch, synthesized design, and rationale reflect every accepted correction; `review-log.md` records each round.
