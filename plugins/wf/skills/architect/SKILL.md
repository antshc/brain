---
name: architect
description: >-
  Sketch types, signatures, and module structure before code, synthesize competing multi-model design candidates, then implement against the chosen sketch. Use for /architect, architect this, design this, or non-trivial work where jumping to code would lock in the wrong shape.
---

# Architect

Sketch types, function signatures, class shapes, and module boundaries with `not implemented` bodies and pseudocode. Synthesize across multiple model perspectives, then fill in code against the chosen sketch.

## Bundled files

Resolve every path from this skill's base directory. Read each file fully when its trigger fires.

| File | Load when |
|---|---|
| [references/principles.md](references/principles.md) | any step cites a principle by heading |
| [models.md](models.md) | picking a subagent model for any role |
| [references/subagents.md](references/subagents.md) | spawning any subagent |
| [references/design-red-flags.md](references/design-red-flags.md) | Phase B screening |
| [references/rationale-template.md](references/rationale-template.md) | writing Outputs; give to every runner |
| [how/how.md](how/how.md) | Phase A grounding; scrap step 1 |
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
| [arena/arena.md](arena/arena.md) | Phase B; scrap step 4 |
| [arena/runner-prompt.md](arena/runner-prompt.md) | Phase B runner brief |
| [interrogate/interrogate.md](interrogate/interrogate.md) | Phase C adversarial pressure |

## Start

Open a todolist with one entry per phase before starting.

1. Ground
2. Sketch
3. Agree
4. Implement
5. Scrap

## Phase A: Ground the problem

Build a real mental model of every system the new code touches. Run the `how/how.md` procedure over the relevant subsystems. Naming a file isn't grounding. Produce the architectural explanation `how/how.md` prescribes. If the design redefines ownership or layering, also run the `why/why.md` procedure on the existing shape so the rationale becomes a constraint, not a guess.

Skip Phase A only when the work is genuinely greenfield with no surrounding system to integrate.

## Phase B: Sketch

Run the `arena/arena.md` procedure with the design-sketch task and the Phase A grounding artifacts. Pass `arena/runner-prompt.md` as each runner's prompt, plus the absolute paths of this `SKILL.md`, `references/rationale-template.md`, and `references/principles.md`.

Take the runners from the `architect runners` role in `models.md`. Alias and rejected entries follow the runner rules in arena Phase A.

Design it twice. Require at least two structurally distinct candidates before synthesis, even when the first looks sufficient. This is the *Exhaust the design space* principle made concrete. Whole-shape alternatives, not point fixes inside one shape.

Screen every candidate against `references/design-red-flags.md` before synthesis. Assume the next contributor is an agent that sees only the files it opened, copies the nearest example, and takes the shortest path that compiles. Prefer the design where a change that looks right from one file is right for the whole repo.

Compare viable candidates on interface depth. Prefer the design that hides more complexity behind a smaller, simpler public surface. A rich interface can keep call chains short by concentrating capability instead of scattering it across layers.

Arena returns one synthesized design package. Its synthesis decision fills the rationale's "Synthesis decision" section.

## Phase C: Agree (opt-in)

Default: proceed directly to implementation with the synthesized design. No human checkpoint.

Opt in to a checkpoint when the invoker explicitly asks: "/architect with checkpoint," "stop and show me before implementing," or similar. Then surface the synthesized design and pause for sign-off.

The synthesis can ship as its own commit either way, as the "scaffold first" mode of the *Foundational thinking* principle. Planned and scoped breakage during fill-in is fine, per the *Outcome-oriented execution* principle. For adversarial pressure on the design before implementing, run the `interrogate/interrogate.md` procedure on the synthesized sketch.

If the human pushes back on the shape (in a checkpoint or after the fact), treat that as Phase A evidence. Re-ground and re-run Phase B before writing more code.

## Phase D: Implement against the sketch

Replace `not implemented` bodies with code, pseudocode with logic. The synthesized sketch is the contract. Deviations from it are signal to surface, not friction to absorb silently. If a function needs a parameter the sketch didn't anticipate, ask whether the sketch was wrong, the requirement was missed, or the implementation is overreaching.

## Phase E: Scrap when the architecture is wrong

If implementation keeps producing friction the sketch can't absorb, throw the sketch out. Don't bolt fixes onto a wrong design, per the *Redesign from first principles* and *Fix root causes* principles.

The signal is a *pattern*, not single instances. Tells:

- The same shape of workaround appearing repeatedly across unrelated code.
- Multiple unrelated edge cases that all need special-case branches.
- Types that need escape hatches (`any`, casts, optional fields always set in practice) to compile.
- The "we need a lock" reflex when the sketch said the state wasn't shared.
- Callers having to know the abstraction's internal rules to use it.
- Two or more independent Phase D deviations of the same shape across the implementation.

Use judgment. A few edge cases don't condemn an architecture. Some problems are legitimately complex. Complexity in the data is not complexity in the design.

When you scrap:

1. Re-run the `how/how.md` procedure over what's been built.
2. Redesign as if the new constraints had been day-one assumptions, per *Redesign from first principles*.
3. Subtract before adding, per the *Subtract before you add* principle. The new sketch should be smaller than the old one before it grows.
4. Return to Phase B and re-run arena.

## Outputs

The caller's usage is written first and the type sketch derived from it. One file with new types and signatures for small changes. Module map plus type definitions for larger work. The rationale ships alongside, shaped per `references/rationale-template.md`, including the usage sketch and the synthesis decision.
