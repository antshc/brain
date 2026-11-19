### Bug fix

**You own this task. Plan, review, verify.** Delegate investigation and the fix to subagents; stay in the lead.

Be scientific. Every shipped line traces to runtime evidence. "Might help" is a hypothesis, not a fix; it does not ship. When evidence refutes a hypothesis, revert what it motivated.

1. Reproduce it yourself on the matching surface. *Load and follow the `testing-integrations` skill to pick the minimal seam and reproduce strategy (component test, functional slice, real cloud, local app via REST or GUI).* Cloud-only symptom → *Load and follow the `prototype-cloud-scenario` skill to reproduce the bug as a throwaway cloud scenario on isolated test resources.* Ask the user only with a specific reason the surface is unreachable, after driving it as far as it goes. Done when the symptom fires on demand.
2. Binary-search the cause. List candidate hypotheses; each pass take the split that cuts the most remaining space, get runtime evidence, eliminate. Use [Evidence](../references/evidence.md) to research the affected subsystem and trace regression history with `git log -p` or `git blame`. Unclear state → add logging or instrumentation and read it as the code runs. Confirm the surviving *mechanism* with runtime evidence before step 3 (**Fix root causes**, **Attack the premise**).
3. Before editing, run [Prepare a direct branch](../references/shipping.md#prepare-a-direct-branch). Plan the fix. Crosses a function boundary → *Load and follow the `design` skill to design architecture and resolve decisions*, selecting `architect` first. Delegate implementation with a specific scope: files, data shape, the repro to turn green.
4. Verify on the same surface. The original repro now passes. "Inconclusive" or wrong-surface is not a pass; flag it. Unit tests show branch behavior, not bug absence (**Prove it works**).
5. *Load and follow the `git` skill to run verified Git mechanics using **Draft commit***. Follow [Commit](../references/shipping.md#commit) to write the commits. Put the failing repro before the fix (**Sequence verifiable units**). Skip the separate failing-test commit when that test would be expensive or integration-heavy; say so.
6. Not fixing now, or the user wants a report → *Load and follow the `write` skill to write and update bug reports from observed behavior, using route `bug`.*
7. When shipping a fix, run [Opening a PR](../references/shipping.md#opening-a-pr). Done when the draft PR is verified or the blocker is recorded.

**Reply:** what was broken, root cause, fix, how you verified. Paste failing-then-passing repro output verbatim.
