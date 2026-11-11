# Interrogate

Adversarial review procedure of `design interrogate`. Paths resolve from the `design` skill directory.

Adversaries try to break a change or a design. A finding survives only when a run proves it. Report the findings. Do not apply fixes.

Standalone `design interrogate` reads the repository's architecture, relevant ADRs/Concepts and glossary, then derives intent, scope, and a safe runnable target. Write verified findings to `<artifact-root>/interrogate.md`; for verified contract findings, run [Deep module](deep-module.md) and append recommended interfaces as **proposed** corrections. Present the report and stop. Apply nothing. When Architect calls this route, return findings and proposals to the caller instead.

## Frame

For automatic routing, use the supplied sketch scope, material claim, intent, and runnable target; otherwise keep the defaults below.

The scope is what the user names. Otherwise it is the branch diff from its merge base with the base branch, through the working tree. State the intent per *run `principles` skill to load indexed engineering principles by name; read its body in full, then load in full the file its Index maps to the `In your own words` principle*, from the user's message, the commits, and the PR description. Ask the user when the intent is unclear.

## Fan out

*Run `subagents` skill to dispatch independent workers with role-based models and isolated outputs* using **Dispatch**. Use the ordered `interrogate reviewers` pool and the caller's `adversaries` count (1–3, default 1, independent of `arena-agents`). Give each general-purpose reviewer an isolated worktree with the scope's uncommitted changes, the scope and intent, and this brief:

> Read `experiment` skill's Inputs and Workflow before starting, then *run `experiment` skill to answer an uncertain technical question by observing actual behavior*, filling `@question` = the claim, `@criteria` = success/refutation criteria, `@repoFacts` = intent, scope, runnable target, and prior evidence, `@limits` = safety limits and your worktree. Invoke it directly, without the Prove wrapper or nested Interrogate; reuse valid reproductions and preserve them until coordinator verification. Keep state local or in authorized sandboxes; never use destructive production targets or expand credentials/permissions.

> Break this change. Prove each finding with a run against the real code, such as a failing test, a repro script, or command output that shows the wrong behavior. For a design or plan, run a prototype or probe the current tree. Keep repros in your own worktree. Report each finding with a title, the exact command, the output it printed, and the output the intent requires. Leave out anything you did not run. That covers style, naming, structure, and risks that need a future change to matter. No findings is a valid result.

## Verify

Verify each finding by rerunning its command in the reviewer's worktree. Keep a finding when the output shows the failure and the failure breaks the intent. Drop the rest. Merge findings that share a root cause.

Keep every verified finding across reviewers.

## Output

- **Intent**: the restatement.
- **Findings**: for each verified finding, the command, its output, how it breaks the intent, and the adversaries that found it. Say "no verified findings" when none survive.
- **Dropped**: for each adversary, the count of dropped findings and why.

