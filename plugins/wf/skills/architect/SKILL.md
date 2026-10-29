---
name: architect
description: >-
  Sketch types, signatures, and module structure before code, produce one design candidate or synthesize competing multi-model candidates, loop user corrections into the sketch, then hand off to spec or implement against the sketch. Use for /architect, architect this, design this, or non-trivial work where jumping to code would lock in the wrong shape.
---

# Architect

Sketch types, function signatures, class shapes, and module boundaries with `not implemented` bodies and pseudocode. Use one runner by default or synthesize multiple model perspectives, review the sketch with the user until accepted, then hand off to spec or fill in code against the sketch. Write production code only after the user replies **implement**.

## Bundled files

Resolve every path from this skill's base directory. Read each file fully when its trigger fires.

| File | Load when |
|---|---|
| [references/evidence-routing.md](references/evidence-routing.md) | Phase A technical questions and every Phase C round, including greenfield |
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
| [interrogate/interrogate.md](interrogate/interrogate.md) | automatic evidence routing or user picks interrogate |
| [prototype/prototype.md](prototype/prototype.md) | evidence routing selects Experiment or user picks prototype |

## Artifact location

Write every artifact — grounding, `how`/`why` outputs, arena candidates, judge verdict, synthesis note, sketch, rationale, interrogate findings, review log — under `<repo-root>/tmp/architect-<slug>/`, where `<repo-root>`. Never write them to the session folder or system `/tmp`. Pass absolute paths under this root to every subagent. Research specialist reports may retain a stronger location contract per `references/evidence-routing.md`; index their absolute paths under the artifact root. Phase E code goes in the repo's working tree, not the artifact root.

## Repo docs

Read the repo's architecture, relevant ADRs and Concepts, and glossary before grounding; skip absent ones.

- Sketch MUST conform to accepted ADRs and Concepts.
- Use glossary terms for names; no synonyms.
- Place modules per the documented architecture.
- Deviation → record conflict and reason in rationale open questions; raise in Phase C.
- Pass doc paths to every subagent.

## Options

Accept `arena-agents=1|2|3`; default `1`. Reject other values before launching arena runners. Pass the resolved count to Phase B; retain it for arena re-runs unless the user changes it.

## Start

Open a todolist with one entry per phase before starting.

1. Ground
2. Sketch
3. Review
4. Hand off or Implement

Add a Scrap entry when Phase F triggers.

## Phase A: Ground the problem

Build a real mental model of every system the new code touches, starting from Repo docs. Run the `how/how.md` procedure over the relevant subsystems. Naming a file isn't grounding. Produce the architectural explanation `how/how.md` prescribes. If the design redefines ownership or layering, also run the `why/why.md` procedure on the existing shape so the rationale becomes a constraint, not a guess.

Skip subsystem grounding only when the work is genuinely greenfield with no surrounding system to integrate. Before Phase B, resolve technical questions through `references/evidence-routing.md`, including greenfield work.

## Phase B: Sketch

Run the `arena/arena.md` procedure with the design-sketch task and the Phase A grounding artifacts. Pass `arena/runner-prompt.md` as each runner's prompt, plus the absolute paths of this `SKILL.md`, `references/rationale-template.md`, and `references/principles.md`.

Take the runners from the `architect runners` role in `models.md`. Alias and rejected entries follow the runner rules in arena Phase A.

With multiple runners, require structurally distinct candidates before synthesis, per *Exhaust the design space*. Whole-shape alternatives, not point fixes inside one shape.

Screen every candidate against `references/design-red-flags.md` and the Repo docs rules before synthesis. Assume the next contributor is an agent that sees only the files it opened, copies the nearest example, and takes the shortest path that compiles. Prefer the design where a change that looks right from one file is right for the whole repo.

Compare viable candidates on interface depth. Prefer the design that hides more complexity behind a smaller, simpler public surface. A rich interface can keep call chains short by concentrating capability instead of scattering it across layers.

Arena returns one synthesized design package. Its synthesis decision fills the rationale's "Synthesis decision" section.

## Phase C: Review loop

Loop until the user explicitly replies **accept** or **implement**. Ask in plain chat; MUST NOT use the VS Code ask/questions tool. MUST NOT write production code in this phase. Experiment code is disposable evidence kept in a worktree, never part of the sketch.

Before each round, run `references/evidence-routing.md` on open questions and material claims. Reuse valid evidence; propose verified failures as corrections without applying them.

1. Present in chat: usage sketch, module map, key types and signatures, synthesis decision, the rationale's unresolved questions and risks, evidence conclusions and limitations, proposed corrections, and absolute paths of the base candidate's sketch, the synthesized design, and the rationale.
2. Offer these replies verbatim, then stop and wait for the user:
   ```
   Reply with one:
   - **corrections**: `Q2 → keep per-tenant tables` (edits sketch, design, rationale; add `; arena` to also run a new arena that creates a new candidate)
   - **interrogate**: `risk 1; intent: ...; target: DynamoDB Local` (adversaries try to prove it)
   - **prototype**: `GSI backfill; target: DynamoDB Local` (throwaway build in a worktree, then interrogated)
   - **ask**: `why does X own Y?` (grounds the answer, then corrections)
   - **accept**: hand off to `/to-spec`
   - **implement**: build against the sketch in this working tree (skips `/to-spec`)
   ```
3. Act on the reply:
   - **Corrections** → apply them directly; without `arena`, never re-run arena. Rewrite the base candidate's sketch in place, then update the synthesized design and rationale (usage sketch, affected sections, synthesis decision, alternatives, open questions) so all three agree. Screen the rewrite against `references/design-red-flags.md` and the Repo docs rules; surface hits as questions. Append the correction and resulting changes to `review-log.md` in the artifact root. Start the next round.
   - **Corrections with `arena`** → apply as above, then run the `arena/arena.md` *Re-run for corrections* procedure with the corrections folded into the task; the new synthesized design is a new candidate against the corrected current one. Present both with the same round contents; the user picks which stays via **corrections**. Append the run to `review-log.md`. Start the next round.
   - **Interrogate** → run the `interrogate/interrogate.md` procedure on the current sketch. Present findings as proposed corrections; apply only those the user accepts, as above. Start the next round.
   - **Prototype** → run the `prototype/prototype.md` procedure on the question in the reply. Present its output; apply only the proposed corrections the user accepts, as above, citing the evidence in the rationale. Start the next round.
   - **Ask** → answer from Phase A grounding, running `how/how.md` or `why/why.md` when needed; present the answer, then start the next round.
   - **Accept** → go to Phase D.
   - **Implement** → go to Phase E.

Ambiguous reply → ask which of the six it is; never treat it as acceptance or implement.

## Phase D: Hand off

Stop. Tell the user the accepted sketch is ready and to run `/to-spec` with the target branch and Initiative ID; that skill turns the synthesized design and base candidate sketch from this conversation into a published spec issue. Do not draft the spec yourself.

## Phase E: Implement against the sketch

Work in the current working tree and branch. The synthesized sketch is the contract.

1. Scaffold: write the accepted sketch's types, signatures, and `not implemented` bodies into their target modules; commit as its own commit, per *Foundational thinking*. Done when the scaffold commit exists.
2. Fill in: replace `not implemented` bodies with code and pseudocode with logic. Planned, scoped breakage during fill-in is fine, per *Outcome-oriented execution*. Done when no `not implemented` body from the sketch remains and the repo's build and tests pass.
3. Deviations: when code needs something the sketch didn't anticipate (new parameter, type, dependency, module), stop and classify it: sketch wrong, requirement missed, or implementation overreaching. Surface it to the user in chat; never absorb it silently. Apply the agreed change to the sketch, synthesized design, and rationale, and append it to `review-log.md`.
4. Watch for Phase F tells throughout; on a pattern, go to Phase F.

## Phase F: Scrap when the architecture is wrong

If implementation keeps producing friction the sketch can't absorb, throw the sketch out. Don't bolt fixes onto a wrong design, per *Redesign from first principles* and *Fix root causes*.

The signal is a pattern, not single instances. Tells:

- Same shape of workaround repeating across unrelated code.
- Multiple unrelated edge cases each needing special-case branches.
- Types needing escape hatches (`any`, casts, optional fields always set in practice) to compile.
- The "we need a lock" reflex when the sketch said the state wasn't shared.
- Callers needing the abstraction's internal rules to use it.
- Two or more independent Phase E deviations of the same shape.

Use judgment. A few edge cases don't condemn an architecture. Complexity in the data is not complexity in the design.

When you scrap:

1. Tell the user which tells fired, with file evidence; append to `review-log.md`.
2. Run the `how/how.md` procedure over what's been built.
3. Redesign as if the new constraints had been day-one assumptions, per *Redesign from first principles*.
4. Subtract before adding, per *Subtract before you add*. The new sketch is smaller than the old one before it grows.
5. Return to Phase B and re-run arena, then Phase C review.

## Outputs

The caller's usage is written first and the type sketch derived from it. One file with new types and signatures for small changes. Module map plus type definitions for larger work. The rationale ships alongside, shaped per `references/rationale-template.md`, including the usage sketch and the synthesis decision. Sketch, synthesized design, and rationale reflect every accepted correction and Phase E deviation; `review-log.md` records each round. After **implement**: a scaffold commit, then working code filling it in the current branch.

