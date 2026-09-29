---
name: run-cloud-scenario
description: Execute a cloud test scenario phase by phase against real resources, logging PASS/FAIL and findings to a new `<TICKET>-test-execution-log-runN.md`, and feeding confirmed scenario-doc bugs back into the scenario itself. Use when the user asks to run, execute, or validate a cloud test scenario, or to continue/resume one already in progress.
disable-model-invocation: true
---

# Run Cloud Test Scenario

A scenario doc is not a one-shot script — it accumulates fixes across runs. Every run either confirms the doc is correct or makes it more correct; never end a run with a known scenario-doc bug left unfixed.

## Setup

1. Read the target scenario doc in full: its phases, the "Target environment" variable block, and its "Run history" bullets (skip if absent — first run).
2. List `docs/escalations/<TICKET>-test-execution-log-run*.md`; the new log is `run<N>` where `N` is one past the highest existing run. Create it with a title, a one-line pointer back to the scenario doc, the variable block, and a "Pre-check:" line recording the subscription/resource-group verification.
3. Resolve the **phase gate**: default is stop after each phase for the user to validate before continuing. If the user has authorized running to completion unattended, record that authorization verbatim in the log's opening paragraph and skip the gate for every phase, including destructive ones — a blanket continue-authorization also satisfies query-azure's Delete Gate for this run.

## Per phase

Repeat for each phase in the scenario doc, in order:

1. If the phase gate applies, stop after the previous phase's log section is written and wait for the user before starting this one.
2. Run the phase's commands (use the `query-azure` skill for the actual `az` calls). Check each command's actual result against the phase's stated expectation, not just its exit code.
3. Append a `## Phase N — <name>: PASSED|FAILED` section to the log: one bullet per command with its real result, in the order run. Call out anything that deviated from the scenario doc — an error, a quirk, a new capability confirmed, a prior open question resolved — as a **`Finding (...)`:** paragraph explaining what happened and why it matters, not just what the error said.
4. Classify each finding:
   - **Reproducible scenario-doc bug or gap** (wrong command order, missing step, stale assumption) — fix the scenario doc itself in the same turn, and note the fix in the log's finding.
   - **Environment quirk or one-off flake** — record it in the log only.
5. End the section with a `**Status:**` line stating what happens next (proceeding to the next phase, or stopped for validation).
6. If this phase deletes or destroys resources, re-confirm it's covered by the Setup step 3 gate before running — never infer destructive authorization from anything other than an explicit blanket continue instruction.

## Completion

1. After the last phase, append `## Overall result: PASSED|FAILED — <one-line summary>` with a numbered list of this run's new findings (resolved open questions, new confirmations, scenario-doc bugs fixed).
2. Add one new bullet to the scenario doc's "Run history" section summarizing this run and linking the log — this is what makes the next run start from the current ground truth instead of repeating this run's discoveries.
3. Report the log file path and every scenario-doc edit made, so the user can review the diff.
