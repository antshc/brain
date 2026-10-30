### Investigation

**You own the answer. Plan, route, write.** Read-only; produces a cited explanation or recommendation, not a code change.

1. Locate the code. *Run `explore-codebase` skill in a subagent to find where a symbol lives, what calls it, how a flow works.* Done when every claim has a file and line.
2. Pick depth. Behavior inside one deployable, a cross-deployable flow, or data ownership → *run `research-system` skill to inspect the system as-built with cited file references.* External docs, packages, cloud, or web facts → *run `research` skill to investigate against primary sources and save cited findings.* Unknown external C# type → *run `inspect-nuget-source` skill to resolve the owning NuGet package and verify its real API.*
3. Uncertain behavior that reading cannot settle → *run `experiment` skill to answer one technical question by observing actual behavior.*
4. Throughput checkpoint is one line: `throughput checkpoint: n/a, read-only investigation`.
5. Shape the output: Overview, Key concepts, How it works, Where things live, Gotchas. A decision between alternatives → recommendation plus tradeoffs table. *Run `bottom-line` skill to write the decision-oriented key finding and recommended action* when the reader must act.

No PR, no `architect` unless the investigation precedes a code change. If it does, hand back and re-route to the `bug-fix` or `architect` playbook.

**Reply:** the investigation output. For "are we sure?" give real judgment with reasons; push back when the premise is wrong (Autonomy).
