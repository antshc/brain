# Interrogate

Adversarial review procedure of the `architect` skill. Paths resolve from the skill base directory.

Adversaries try to break a change or a design. A finding survives only when a run proves it. Report the findings. Do not apply fixes.

## Frame

Automatic routing → use supplied sketch scope, material claim, intent, and runnable target. Otherwise use the user-named scope, defaulting to the branch diff from its merge base with the base branch through the working tree. State the intent per *In your own words* in `references/principles.md`, from the user's message, the commits, and the PR description. Ask the user when the intent is unclear.

## Fan out

Run Phase A steps 3 and 4 and Phase B of `arena/arena.md`, with four changes. Take the runners from the `interrogate reviewers` role in `models.md`. Copy the scope's uncommitted changes into each worktree. Spawn each adversary as `general-purpose`. In place of the arena task and rationale, give each adversary the scope, the intent, and this brief:

> Break this change. *Run `experiment` skill to test uncertain technical behavior through observation.* Pass the claim, intent, scope, runnable target, success/refutation criteria, prior evidence, and safety limits. Invoke Experiment directly, without the Prototype wrapper or nested Interrogate. Let Experiment select probes; reuse valid reproductions. Preserve repros until coordinator verification. Keep repros in your own worktree and state in local or authorized sandboxes; never use destructive production targets or expand credentials/permissions. Report each finding with title, exact command, actual output, intent-required output, and relevance to intent. Leave out anything you did not run. That covers style, naming, structure, and risks that need a future change to matter. No findings is a valid result.

## Verify

Verify each finding per arena Phase F by rerunning its command. Keep a finding when the output shows the failure and the failure breaks the intent. Drop the rest. Merge findings that share a root cause.

Skip arena Phases C, D, and E. Adversaries find different failures, so the verdict keeps every verified finding, not one adversary's list.

## Output

- **Intent**: the restatement.
- **Findings**: for each verified finding, the command, its output, how it breaks the intent, and the adversaries that found it. Say "no verified findings" when none survive.
- **Dropped**: for each adversary, the count of dropped findings and why.

