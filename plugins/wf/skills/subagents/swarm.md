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

## Attribution

Adapted from [pstack Swarm](https://github.com/cursor/plugins/blob/e73df471cd4bd918367e99f3dd9c51bd53ddf5f0/pstack/skills/swarm/SKILL.md).

```text
MIT License

Copyright (c) 2026 Lauren Tan

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

```
