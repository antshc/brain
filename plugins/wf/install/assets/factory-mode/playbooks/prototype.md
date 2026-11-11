### Prototype

**You own the decision, not production code. The prototype is a throwaway instrument; finish with evidence and a recommendation.**

Laziness and the verification bar invert here: speed over polish, no planning. Rigor is in picking the right design cheaply. Propose variations the user did not ask for; throw an approach away and try another.

1. Scope the decision: which layout, interaction, behavior, timing, or approach. No decision → no prototype; report the missing decision.
2. Open design space → gather prior art and summarize directions; let the user pick before building. Skip when direction is set.
3. Build throwaway in an isolated scratch dir outside production source (session workspace or `tmp/`). Behavioral, API, SDK, cloud, or runtime question → *run `prove` skill to confirm or refute one technical claim with reproducible evidence*, filling `@question` and `@criteria` from the scoped decision, `@repoFacts` = prior art gathered, `@limits` = the scratch dir. Reuse repository test infrastructure when Prove selects it; keep the wrapper disposable. Cloud bug scenario → `prototype-cloud-scenario`. Visual → lightest stack that renders the idea. No production abstractions.
4. Comparing alternatives → build them behind one switch (flag, argument, or keypress), each variant labeled (**Exhaust the design space**).
5. Observe on the matching surface. Visual → screenshot each variant and drive the interaction. Behavioral or timing → log the timing, print the output. The observation is the test.
6. Present alternatives, tradeoffs, and a recommendation. Stop; do not start implementation.

**Reply:** variants explored, evidence (screenshots or observed output/timing), tradeoffs, recommendation, scratch path. State plainly that the prototype is throwaway.
