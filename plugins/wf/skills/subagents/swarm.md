# Swarm

Copy the checklist before dispatch.

```markdown
- [ ] Frame
- [ ] Fan out
- [ ] Aggregate
- [ ] Report
```

## Frame

1. State the done condition and the required report or artifact.
2. Partition into slices, race workers on identical briefs, or mix both. Before a race, choose **first pass**, **rank all**, or **best-of** and state its selection criteria.
3. Use the `swarm workers` role by default. For a model race, name each arm's model. Apply Subagents Model selection through the current harness. Use local execution when a worker needs local state. If using remote execution, select the requested branch and commit. Report a blocker if the harness cannot provide the required checkout.
4. Give each writer an isolated output. Verification and measurement briefs name the exact SHAs. Measurement also names the method, sample count, unit and order.

## Fan out

Use Dispatch to launch all workers together in background. Each brief stands alone: goal, scope, slice or arm, verification and expected report. Workers report `PASS`, `ISSUES` or `BLOCKED` with evidence and any required SHA and measurement method. An `ISSUES` report includes every supported finding. Record dropouts and continue with the other workers.

## Aggregate

Read terminal reports. Retry a worker once if its report omits a required SHA or method. Record a gap if the retry still misses evidence. Every required slice needs a valid result. Apply the declared race rule to the race arms. A gap cannot count as a pass.

## Report

Return one consolidated result table with issue summaries, gaps and dropouts, and the race rule when used.
