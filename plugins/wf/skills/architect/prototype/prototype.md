# Prototype

Evidence procedure of the `architect` skill. Paths resolve from the skill base directory.

Build or run a throwaway prototype of the uncertain part of the sketch, run it for real, then prove it with `interrogate/interrogate.md`. The prototype is evidence, not design: it never replaces or enters the sketch. Report the evidence. Do not promote prototype code.

## Frame

State the question, the assumption, the success criteria, and the intent per *In your own words* in `references/principles.md`, from the user's reply and the current sketch. For automatic runs, use the routing handoff in place of the reply. One question per prototype. Ask the user when the question is unclear. Stop and say so when code inspection, docs, or reasoning answer it confidently.

## Build

Set `@runRoot` to a fresh `<artifact-root>/prototype/<question-id>-<revision>-<attempt>/`; pass its absolute path to the builder.

Create one git worktree per arena Phase A step 4 of `arena/arena.md`, copying the uncommitted changes of the repo into it. Spawn one `general-purpose` builder with the role `prototype builder` in `models.md`, pick its reasoning effort per `references/subagents.md`, and give it the worktree path, the Frame, the sketch path, and the grounding paths. Also pass prior evidence, runtime/environment constraints, safety limits, and out-of-scope behavior. Instruct it:

> *Run `experiment` skill to test one uncertain technical question by observing actual behavior.* Let Experiment select the method; CLI-only needs no app or patch. Code changes are allowed in your worktree only; follow the sketch's types and signatures where they apply and stub only irrelevant dependencies. Run it against the real boundary. When code was created, save the diff as `{{runRoot}}/prototype.patch`. Save `{{runRoot}}/report.md` with question, method, observation (actual output), conclusion (confirmed/refuted/inconclusive), evidence paths, architectural implication, cleanup, and the exact command to rerun. Keep state local or in authorized sandboxes; never use destructive production targets or expand credentials/permissions. Preserve code and scratch state until coordinator rerun and Interrogate finish; cleanup follows this round. A failed assumption is a valid result. Do not commit, push, or touch files outside your worktree and the artifact root.

Rerun the report's command in the worktree. Treat an unreproducible observation as no evidence.

## Prove

Run `interrogate/interrogate.md` with the prototype worktree's diff as the scope, the Frame's intent, and the same runnable target. For CLI-only runs, use the report's command, assumption, and observation as scope instead of a diff. Adversaries try to break the prototype. Reuse coverage for the same scope/revision. A verified finding means the sketch's shape fails under that run.

## Output

- **Question**: the Frame.
- **Observation**: the rerun command, its output, and the conclusion.
- **Interrogate**: the verified findings and dropped counts per `interrogate/interrogate.md`.
- **Proposed corrections**: sketch changes the evidence supports, each citing its command. The sketch keeps `not implemented` bodies; prototype code stays out of it.
- **Artifacts**: absolute path of `report.md` and, when code was created, `prototype.patch`.

Remove the worktree after the round and keep the patch and report, unless the user asks to preserve the worktree.

