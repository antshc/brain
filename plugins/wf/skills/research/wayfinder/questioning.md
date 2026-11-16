# Questioning

Run interviews directly in the Research Wayfinder session. Research has research and experiment topics only; scope, priorities and evidence criteria are human choices asked here, never Decision topics or Design execution.

## Destination first

Settle subject, outcome, scope, exclusions, exact versions, constraints and sufficient evidence. Ask only what is needed to establish the destination; then get user confirmation. Destination approval is not work item approval.

## Separate breadth-first interview

After destination confirmation, start a separate frontier interview. Cover major in-scope areas before deepening one thread: feasibility, hard limits, performance/scale, reliability, security, operations, ergonomics. Surface precise factual questions, falsifiable hypotheses, dependencies and concerns not yet sharp enough to frame as a topic. Do not exhaust every downstream question before charting.

Maintain the dependency tree and ready frontier. **Ask one question at a time**, with a stable ID, descriptive title and recommended answer. Word it so yes accepts the recommendation; do not hide independent questions inside one item. Wait for the user's answer before asking the next question; silence never accepts an answer.

```text
❓ **Q1** - **<title>**: <one question phrased so yes accepts the recommendation>

➡️ <recommended answer and reason>
```

After each answer, record it, recompute readiness and select one ready question, favoring uncovered main areas before deeper follow-ups where dependencies allow. Hold questions whose prerequisites remain unanswered or whose lookups are running; ask one independent ready question and wait. Finding facts is the agent's job: use the router's Frame, Routing and Spawning agents evidence pipeline rather than asking the user to research them. Name inaccessible/inconclusive evidence as a fact gap; never invent a fact.

## Pause and return

Persist interview phase, stable question IDs, coverage, answers, pending lookups, dependencies, one next question and next action in session state; after worktree setup use the existing ownership record outside disposable worktrees. This is interview state, not another active Markdown research map. Missing durable session storage blocks resumability claims, not independent read-only discussion.

When the current interview phase has sufficient shared understanding, ask the user to confirm that phase is complete. Destination confirmation starts the separate breadth-first frontier interview; only frontier confirmation returns to the small-effort decision. An empty ready frontier with blocked prerequisites is not completion. After frontier confirmation return to Wayfinder's small-effort decision; preserve downstream questions for proposals/fog. On resume restore the phase and pending question rather than restarting. Later human scope or evidence-criteria choices use this same one-question pacing directly in session.
