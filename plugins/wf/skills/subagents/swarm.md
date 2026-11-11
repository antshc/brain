# Swarm

Copy the checklist before dispatch.

```markdown
- [ ] Frame
- [ ] Fan out
- [ ] Aggregate
- [ ] Report
```

## Frame

1. State the done condition, required evidence and report or artifact. Retain caller output contracts, validation and retry rules.
2. Partition into named slices, race workers on identical briefs, or mix both. Slices may share the complete input and differ by responsibility or evaluation dimension. A supplied slice list fixes coverage and worker count. Before a race, choose **first pass**, **rank all**, or **best-of** and state its selection criteria.
3. Use the `swarm workers` role by default. For a model race, name each arm's model. Apply Subagents Model selection through the current harness. Use local execution when a worker needs local state. If using remote execution, select the requested branch and commit. Report a blocker if the harness cannot provide the required checkout.
4. Give each writer an isolated output. Verification and measurement briefs name the exact SHAs. Measurement also names the method, sample count, unit and order.

## Fan out

Use Dispatch to launch independent workers together in background; queue within harness limits without dropping required slices. Each brief stands alone: goal, shared inputs, scope, slice or arm, constraints, verification and expected report. Honor the caller's output contract; otherwise workers report `PASS`, `ISSUES` or `BLOCKED` with evidence and any required SHA and measurement method. An `ISSUES` report includes every supported finding. Record dropouts and continue with the other workers.

## Aggregate

Drain all workers and check terminal reports against the declared output and evidence contract, including required SHAs and methods. Unless the caller supplies retry rules, retry malformed or incomplete reports once through Dispatch. Preserve original reports and corrections; record unresolved failures and missing results as gaps. Every required slice needs a valid result. Apply the declared race rule to the race arms. A gap cannot count as a pass. Return domain judgments to the caller for validation; a summary never replaces the underlying results.

## Report

Return one consolidated result table with issue summaries, gaps and dropouts, and the race rule when used. Include each slice's original result or artifact path and execution outcome. Record requested model, effort, rejections and fallbacks; record actual model only when observable. Disclose unsupported model selection. Keep execution metadata separate from caller-defined worker payloads.
