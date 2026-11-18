# HITL

Run automated review and proof for a PR, then hand the same PR to the user for human-led review.

## Workflow

1. Resolve the PR URL and source checkout. If the PR URL or matching source checkout is missing, ask for the missing input and wait. Done when both are known.
2. Run the shared [Review](../references/review.md) instructions once. If the caller already ran Review for this handoff, use its saved record. Done when the proof summary and any blockers are ready.
3. Run the Human review handoff below. Done when the user ends the session or the HITL route reports a blocker.

## Human review handoff

1. Show the proof summary, including a clickable **Proof report** link for each saved claim report. If no report was produced, show the skip reason or blocker. When the summary has already been shown for this handoff, continue to the next step. Done when the user has the proof outcomes and available links.
2. From the source repository context after proof worktree cleanup, *Load and follow the `review` skill to start human-led review of the same PR, using route `hitl`.* Pass the PR URL. Let the route capture the current revision and discussion and apply its dirty-checkout gate. If the PR revision has advanced, label the proof results with the original revision. The route shows its clickable **Changes brief** link before asking for the first code change or question. If the brief fails, show the reason instead. Done when the first input prompt or setup blocker is visible.
3. Keep the HITL route active across replies. Let the user choose what to inspect and approve the exact text of each drafted comment before posting. When the session ends, return to the caller's next authorized phase, if any. If setup is blocked, report the blocker to the caller.
