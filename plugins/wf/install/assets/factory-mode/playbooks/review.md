# Review

Prepare a PR for human-led review: triage the change, run only the review axes and blast radius it needs, prove every resulting claim, then hand the PR and its artifacts to the user.

## Workflow

1. Resolve the PR URL and source checkout. If either is missing, ask for it and wait. Set `REVIEW_RUN_DIR` to `RUN_DIR/review` when the caller supplies `RUN_DIR`; otherwise `<repo-root>/tmp/factory-mode-review-<PR-number>`. Done when PR identity, checkout, and `REVIEW_RUN_DIR` are explicit.
2. **Triage.** *Load and follow the `github` skill to read pull requests and review evidence*, using Pull requests, for the title, body, commits, diffstat, and changed paths at the pinned head. Read only enough changed code to classify the change; do not review it. Select from the table below and record a reason for each selected or rejected axis and for the blast-radius mode. Save `REVIEW_RUN_DIR/triage.md` and show the decisions with reasons; do not wait for approval. Done when the axis list and blast-radius mode (`only`, `after`, `decide-after`, or `none`) are saved.

   | Signal in the change | Select |
   |---|---|
   | Changed runtime behavior, branching, data handling, or error paths | `bugs` |
   | Performance, security, reliability, concurrency, observability, or operability surface | `quality-attributes` |
   | Nontrivial new or restructured code | `code-smells` |
   | PR body names an initiative or work item | `initiative` |
   | Mechanical or wide change (rename, move, dependency bump, config, flag, schema, wire format, deletion) where line-level review adds little | blast radius `only`; no code axes |
   | Changed public or shared contract, persisted or wire format, or cross-module boundary, plus line-level logic | blast radius `after` |
   | Other code change | blast radius `decide-after` |
   | Docs-only, test-only, or comment-only change | no code axes; blast radius `none` |

3. If code axes were selected, run [Automated review](../references/automated-review.md) with the PR URL, source checkout, `REVIEW_RUN_DIR` as its destination, and `--axes <selected list>`. If the caller already ran it for this handoff, reuse its saved record. Done when its proof summary and blockers are saved, or no axis was selected.
4. **Decide blast radius after code review.** For `decide-after`, select `after` when a proved or unverified finding names a mechanism that may repeat at other consumers, or when review evidence shows the change reaches a shared contract, persisted or wire format, configuration, or concurrency boundary; otherwise `none`. Append the decision and reason to `triage.md`. Done when the mode is `only`, `after`, or `none`.
5. For `only` or `after`, *Load and follow the `review` skill to assess downstream breakage of the PR, using route `blast-radius`.* Pass the PR URL, pinned head and base, and the proved or unverified code-review findings as known risks. Keep its report local; publish nothing to the PR. Copy or link its final report as `REVIEW_RUN_DIR/blast-radius.md`. Done when the report or a named blocker is saved.
6. **Prove gap sweep.** List every claim from published comments, unposted findings, and the blast-radius report. Map each to its Prove report. For runnable claims without a report, or whose report targets another revision, *Load and follow the `prove` skill to confirm or refute technical claims by executing tests, runnable prototypes, GUI E2E checks, or cloud experiments* once as a batch, from a detached launch worktree at the reviewed head created and removed as in Automated review step 4, with report destinations under `REVIEW_RUN_DIR/proof`. Do not re-prove claims that already have a report for this revision. Record each non-runnable claim with its reason. Done when every claim has a report, a blocker, or a non-runnable reason.
7. **Show artifacts.** Show clickable links to `triage.md`, each **Proof report**, and `blast-radius.md`, then counts of proved, refuted, blocked, and inconclusive claims, plus failed axes, unposted findings, and other blockers. Label results with the reviewed revision. Done when the user has every artifact link or the skip reason for each missing artifact.
8. Run the Human review handoff below. Done when the user ends the session or the human-led review reports a blocker.

## Human review handoff

1. Show the proof summary, including a clickable **Proof report** link for each saved claim report. If no report was produced, show the skip reason or blocker. When the summary has already been shown for this handoff, continue to the next step. Done when the user has the proof outcomes and available links.
2. From the source repository context after proof worktree cleanup, *Load and follow the `review` skill to start human-led review of the same PR, using route `hitl`.* Pass the PR URL. Let the route capture the current revision and discussion and apply its dirty-checkout gate. If the PR revision has advanced, label the proof results with the original revision. The route shows its clickable **Changes brief** link before asking for the first code change or question. If the brief fails, show the reason instead. Done when the first input prompt or setup blocker is visible.
3. Keep the human-led review active across replies. Let the user choose what to inspect and approve the exact text of each drafted comment before posting. When the session ends, return to the caller's next authorized phase, if any. If setup is blocked, report the blocker to the caller.

## Completion criteria

- `triage.md` records the selected axes, final blast-radius mode, and a reason for each choice.
- Every published comment, unposted finding, and blast-radius claim maps to a Prove report, a blocker, or a non-runnable reason.
- Blast-radius results stay local; no review approval or submission was made.
