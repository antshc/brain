# Prove

Evidence procedure of `design prove`. Paths resolve from the `design` skill directory.

Prove or refute one uncertain part of the sketch with real evidence: actual output from a run against the real boundary. Experiment selects the cheapest sufficient method: command, CLI/API call, existing test, script, simulation, or throwaway prototype; a prototype is one method, used only when nothing smaller settles it. Attack the evidence with [Interrogate](interrogate.md) only when the user's prove reply includes `interrogate`. Evidence is not design: it never replaces or enters the sketch. Report the evidence. Do not promote proof code.

Standalone `design prove` may use a user-supplied falsifiable claim without an existing sketch; use the claim and repository facts as the Frame. Do not invent a sketch.

## Frame

State the question, the assumption, the success criteria, and the intent per *run `principles` skill; read its body in full, then load in full the file its Index maps to the `In your own words` principle*, from the user's reply and the current sketch. For automatic runs, use the routing handoff in place of the reply. One question per proof. Ask the user when the question is unclear. Stop and say so when code inspection, docs, or reasoning answer it confidently.

## Build

Set `@runRoot` to a fresh `<artifact-root>/prove/<question-id>-<revision>-<attempt>/`; pass its absolute path to the prover.

*Run `subagents` skill to dispatch independent workers with role-based models and isolated outputs* using **Dispatch**. Request one general-purpose `prover` with its own git worktree and a copy of the repo's uncommitted changes. Pass the Frame, sketch and grounding paths, prior evidence, runtime/environment constraints, safety limits, and out-of-scope behavior. Instruct it:

> Read `experiment` skill's Inputs and Workflow before starting, then *run `experiment` skill to test one uncertain technical question by observing actual behavior*, filling `@question` and `@criteria` from the Frame, `@repoFacts` = sketch path, grounding paths, and prior evidence, `@limits` = runtime/environment constraints, safety limits, out-of-scope behavior, and writable paths (your worktree, `{{runRoot}}`). Let Experiment select the smallest method that proves or refutes the assumption with observed output; build a prototype only when no command, existing test, or script settles it. CLI-only needs no app or patch. Code changes are allowed in your worktree only; follow the sketch's types and signatures where they apply and stub only irrelevant dependencies. Run it against the real boundary. When code was created, save the diff as `{{runRoot}}/proof.patch`. Save `{{runRoot}}/report.md` with question, method and why it was chosen, observation (actual output), conclusion (confirmed/refuted/inconclusive), evidence paths, architectural implication, cleanup, and the exact command to rerun. Keep state local or in authorized sandboxes; never use destructive production targets or expand credentials/permissions. Preserve code and scratch state until coordinator rerun and any requested Interrogate finish; cleanup follows this round. A failed assumption is a valid result. Do not commit, push, or touch files outside your worktree and the artifact root.

Rerun the report's command in the worktree. Treat an unreproducible observation as no evidence.

## Attack

Run only when the user's prove reply includes `interrogate`; otherwise skip to Output. Run [Interrogate](interrogate.md) with the prover worktree's diff as the scope, the Frame's intent, and the same runnable target. For CLI-only runs, use the report's command, assumption, and observation as scope instead of a diff. Adversaries try to break the proof. Reuse coverage for the same scope/revision. A verified finding means the sketch's shape fails under that run.

## Output

- **Question**: the Frame.
- **Method**: what Experiment selected and why.
- **Observation**: the rerun command, its output, and the conclusion.
- **Interrogate**: when Attack ran, the verified findings and dropped counts per [Interrogate](interrogate.md); otherwise "not requested".
- **Proposed corrections**: sketch changes the evidence supports, each citing its command. The sketch keeps `not implemented` bodies; proof code stays out of it.
- **Artifacts**: absolute path of `report.md` and, when code was created, `proof.patch`.

Remove the worktree after the round and keep the patch and report, unless the user asks to preserve the worktree.
