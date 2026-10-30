# Interrogate

Adversarial review procedure of the `architect` skill. Paths resolve from the skill base directory.

Adversaries try to break a change or a design. A finding survives only when a run proves it. Report the findings. Do not apply fixes.

## Frame

For automatic routing, use the supplied sketch scope, material claim, intent, and runnable target; otherwise keep the defaults below.

The scope is what the user names. Otherwise it is the branch diff from its merge base with the base branch, through the working tree. State the intent per *In your own words* in `references/principles.md`, from the user's message, the commits, and the PR description. Ask the user when the intent is unclear.

## Fan out

Run Phase A steps 3 and 4 and Phase B of `arena/arena.md`, with four changes. Take the runners from the `interrogate reviewers` role in `models.md`. Copy the scope's uncommitted changes into each worktree. Spawn each adversary as `general-purpose`. In place of the arena task and rationale, give each adversary the scope, the intent, and this brief:

> *Run `experiment` skill to test uncertain technical behavior through observation.* Pass the claim, intent, scope, runnable target, success/refutation criteria, prior evidence, and safety limits. Invoke it directly, without the Prototype wrapper or nested Interrogate; reuse valid reproductions and preserve them until coordinator verification. Keep state local or in authorized sandboxes; never use destructive production targets or expand credentials/permissions.

> Break this change. Prove each finding with a run against the real code, such as a failing test, a repro script, or command output that shows the wrong behavior. For a design or plan, run a prototype or probe the current tree. Keep repros in your own worktree. Report each finding with a title, the exact command, the output it printed, and the output the intent requires. Leave out anything you did not run. That covers style, naming, structure, and risks that need a future change to matter. No findings is a valid result.

## Verify

Verify each finding per arena Phase F by rerunning its command. Keep a finding when the output shows the failure and the failure breaks the intent. Drop the rest. Merge findings that share a root cause.

Skip arena Phases C, D, and E. Adversaries find different failures, so the verdict keeps every verified finding, not one adversary's list.

## Output

- **Intent**: the restatement.
- **Findings**: for each verified finding, the command, its output, how it breaks the intent, and the adversaries that found it. Say "no verified findings" when none survive.
- **Dropped**: for each adversary, the count of dropped findings and why.

