### Investigation

**You own the answer. Plan, route, write.** Read-only; produces a cited explanation or recommendation, not a code change.

1. Ground the question. Keep the original request, including how/why framing; identify the known target, context, exact unknown, and evidence needed. Done when the research brief preserves the request and states an answerable question.
2. Research through Non-negotiables. Locate relevant code, trace behavior across deployables and data ownership, inspect dependency APIs, and consult external primary sources as the question requires. Done when claims cite file/line or external sources; unsupported explanations and inferred intent are labeled assumptions or unknowns.
3. Uncertain behavior that reading cannot settle → *run `experiment` skill to answer one technical question by observing actual behavior.*
4. Throughput checkpoint is one line: `throughput checkpoint: n/a, read-only investigation`.
5. Shape the output: Overview, Key concepts, How it works, Where things live, Gotchas. A decision between alternatives → recommendation plus tradeoffs table. *Run `bottom-line` skill to write the decision-oriented key finding and recommended action* when the reader must act.

No PR, no `architect` unless the investigation precedes a code change. If it does, hand back and re-route to the `bug-fix` or `architect` playbook.

**Reply:** the investigation output. For "are we sure?" give real judgment with reasons; push back when the premise is wrong (Autonomy).
