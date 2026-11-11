# Design

Full architecture procedure of the `design` skill's `architect` route. Paths resolve from `plugins/wf/skills/design/`. Route options, artifact location, and repo-doc rules are in `SKILL.md`.

## Contents

- Todo list
- Phase A: Ground the problem
- Phase B: Sketch
- Phase C: Review (optional checkpoint)
- Phase D: Hand off
- Phase E: Implement against the sketch
- Phase F: Scrap when the architecture is wrong
- Outputs

## Todo list

Open a todolist with one entry per phase before starting.

1. Ground
2. Sketch
3. Resolve or Review
4. Hand off or Implement

Add a Scrap entry when Phase F triggers.

## Phase A: Ground the problem

Build a mental model of touched subsystems from Repo docs and code. *Run `research` skill to investigate primary sources and save cited findings* using default Research for current behavior. Pass the relevant subsystems, repo docs, repository root as `@outputBase`, `@outputPath=<artifact-root>/grounding-how.md`, and content framing as `@outputShape`. When ownership or layering changes, call **Why** with the existing boundary and `@outputPath=<artifact-root>/grounding-why.md`. Architect owns both destinations; Research supplies no default. Treat supported rationale as a constraint.

Skip subsystem grounding only when the work is genuinely greenfield with no surrounding system to integrate. Before Phase B, resolve technical questions through [Evidence routing](../references/evidence-routing.md), including greenfield work.

## Phase B: Sketch

*Run `subagents` skill to compare independent candidates and synthesize findings* using **Arena**. Pass the design task, Phase A grounding, `architect runners` role, resolved `arena-agents` count, rubric inputs, screening rules below, and artifact layout from `design/SKILL.md`. Use that artifact root for Arena outputs. Pass [Runner prompt](../references/runner-prompt.md), the absolute paths to `design/SKILL.md`, [Sketch](sketch.md), its [shared sketch contract](../references/sketch-contract.md), and [Rationale template](../references/rationale.template.md). Each runner follows Sketch's **Candidate** context; do not create a second sketch implementation. Require each candidate and the synthesized result to contain `rationale.md`, `module-map.md`, and `sketch/`. Arena fills the synthesized rationale's synthesis decision. Verify these against the artifact contract, repo docs, and design criteria.

With multiple runners, require structurally distinct candidates before synthesis, per *run `principles` skill to load indexed engineering principles by name; read its body in full, then load in full the file its Index maps to the `Exhaust the design space` principle*. Whole-shape alternatives, not point fixes inside one shape.

Screen every candidate with [shared design red flags](../references/red-flags.md) and the Repo docs rules before synthesis. Assume the next contributor is an agent that sees only the files it opened, copies the nearest example, and takes the shortest path that compiles. Prefer the design where a change that looks right from one file is right for the whole repo.

Compare viable candidates on interface depth. Prefer the design that hides more complexity behind a smaller, simpler public surface. A rich interface can keep call chains short by concentrating capability instead of scattering it across layers.

Arena returns one synthesized design package. Its synthesis decision fills the rationale's "Synthesis decision" section.

## Phase C: Review (optional checkpoint)

Before continuing, run [Evidence routing](../references/evidence-routing.md) on open questions and material claims. When the caller requests one overall adversarial review, *run `interrogate` skill to find failures with reproduced counterexamples* before checkpoint/handoff, passing current intent/scope, safe target, facts, limits, `adversaries`, `@outputPath=<artifact-root>/interrogate.md` and repository root as `@outputBase`; reuse existing coverage. Resolve contract findings through Deep module in Design. Without checkpoint, apply supported corrections; with checkpoint, present proposals for approval. Record decisions in the sketch, rationale, and `review-log.md`. Never write production code during this phase; proof code remains disposable evidence in a worktree.

**Default: no checkpoint.** Continue to Phase E automatically. When the caller explicitly requests a **design-only handoff** (as Factory Mode does), continue to Phase D instead. Do not wait for an `accept` or `implement` reply.

**Checkpoint requested by the user:** Present the design and wait for approval. Ask in plain chat; MUST NOT use the VS Code ask/questions tool. For each review round:

1. Present in chat: usage sketch, module map, key types and signatures, synthesis decision, the rationale's open questions and risks, evidence conclusions and limitations, proposed corrections, and absolute paths of the synthesized sketch, module map, and rationale.
2. Offer these replies verbatim, then stop and wait for the user:
   ```
   Reply with one:
   - **corrections**: `Q2 → keep per-tenant tables` (edits sketch, design, rationale; add `; arena` to also run a new arena that creates a new candidate)
   - **interrogate**: `risk 1; intent: ...; target: DynamoDB Local` (adversaries try to prove it)
   - **prove**: `GSI backfill; target: DynamoDB Local` (real evidence via the smallest run: command, test, script, or throwaway prototype in a worktree; add `; interrogate` to also have adversaries attack it)
   - **ask**: `why does X own Y?` (grounds the answer, then corrections)
   - **accept**: continue implementation (or the caller's design-only handoff)
   - **implement**: build against the sketch in this working tree (overrides a design-only handoff)
   ```
3. Act on the reply:
   - **Corrections** → apply them directly; without `arena`, never re-run arena. Rewrite `synthesis/sketch/` in place under the [shared sketch contract](../references/sketch-contract.md), then update `synthesis/module-map.md` and `synthesis/rationale.md` (usage sketch, affected sections, synthesis decision, alternatives, open questions) so all three agree. Screen the rewrite with [red flags](../references/red-flags.md) and the Repo docs rules; surface hits as questions. Append the correction and resulting changes to `review-log.md` in the artifact root. Start the next round.
   - **Corrections with `arena`** → apply as above, then *run `subagents` skill to compare independent candidates and synthesize findings* using **Arena** with the corrected incumbent, next revision number, same Phase B contract, and corrections folded into the task; the new synthesized design is a new candidate against the corrected current one. Present both with the same round contents; the user picks which stays via **corrections**. Append the run to `review-log.md`. Start the next round.
   - **Interrogate** → *run `interrogate` skill to find failures with reproduced counterexamples* on the current sketch, using the Phase C handoff. Resolve verified contract findings through [Deep module](deep-module.md). Present findings as proposed corrections; apply only those the user accepts, as above. Start the next round.
   - **Prove** → *run `prove` skill to confirm or refute one technical claim with reproducible evidence* on the question, passing sketch/grounding, limits and an exact report destination under `<artifact-root>/prove/`. For `; interrogate`, request retained runnable state, then Design invokes Interrogate with that evidence before releasing owned resources. Present evidence-backed proposed corrections; apply only those the user accepts, citing evidence in the rationale. Start the next round.
   - **Ask** → answer from Phase A grounding, using Phase A’s default Research or **Why** call when needed, with a distinct grounding output for the new question; present the answer, then start the next round.
   - **Accept** → go to Phase D for a design-only handoff; otherwise Phase E.
   - **Implement** → go to Phase E.

Before each subsequent checkpoint review round, rerun [Evidence routing](../references/evidence-routing.md) only for changed questions or claims. Ambiguous reply → ask which of the six it is; never treat it as acceptance or implement.

## Phase D: Hand off

Stop the Architect procedure and return the accepted sketch to the caller for `/design spec`. If standalone, tell the user to run `/design spec` with the target branch and Initiative ID; that skill turns `synthesis/` (rationale, module map, sketch) into a published spec issue. Do not draft the spec yourself.

## Phase E: Implement against the sketch

Work in the current working tree and branch. The synthesized sketch is the contract.

1. Scaffold: write the accepted sketch's types, signatures, and `not implemented` bodies into their target modules; commit as its own commit, per *run `principles` skill to load indexed engineering principles by name; read its body in full, then load in full the file its Index maps to the `Foundational thinking` principle*. Done when the scaffold commit exists.
2. Fill in: replace `not implemented` bodies with code and pseudocode with logic. Planned, scoped breakage during fill-in is fine, per *run `principles` skill to load indexed engineering principles by name; read its body in full, then load in full the file its Index maps to the `Outcome-oriented execution` principle*. Done when no `not implemented` body from the sketch remains and the repo's build and tests pass.
3. Deviations: when code needs something the sketch didn't anticipate (new parameter, type, dependency, module), classify it: sketch wrong, requirement missed, or implementation overreaching. Make evidence-backed corrections, update the sketch, synthesized design, and rationale, and append to `review-log.md`; with checkpoint, surface material changes for approval. Do not silently change user requirements or exceed authorized scope.
4. Watch for Phase F tells throughout; on a pattern, go to Phase F.

## Phase F: Scrap when the architecture is wrong

If implementation keeps producing friction the sketch can't absorb, throw the sketch out. Don't bolt fixes onto a wrong design, per *run `principles` skill to load indexed engineering principles by name; read its body in full, then load in full the files its Index maps to the `Redesign from first principles` and `Fix root causes` principles*.

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
2. Use Phase A’s default Research call over what was built. Save revised grounding beside the original and pass it into the new Phase B.
3. Redesign as if the new constraints had been day-one assumptions, per *run `principles` skill to load indexed engineering principles by name; read its body in full, then load in full the file its Index maps to the `Redesign from first principles` principle*.
4. Subtract before adding, per *run `principles` skill to load indexed engineering principles by name; read its body in full, then load in full the file its Index maps to the `Subtract before you add` principle*. The new sketch is smaller than the old one before it grows.
5. Return to Phase B and re-run arena, then Phase C review.

## Outputs

The caller's usage is written first and the type sketch derived from it. Files follow the artifact contract in `design/SKILL.md`: `synthesis/sketch/` source files (one file for small changes), `synthesis/module-map.md`, and `synthesis/rationale.md` shaped by the [shared template](../references/rationale.template.md), including usage and the synthesis decision. Sketch, synthesized design, and rationale reflect every correction and Phase E deviation; `review-log.md` records each decision. Phase E produces a scaffold commit, then working code filling it in the current branch.

