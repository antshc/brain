### Design

**You own the destination. Resolve unknowns, then synthesize.** Produces a spec and an authoritative feature design, not code.

1. Research the current state through Non-negotiables: how the affected flow works, where it lives, and matching `ARCHITECTURE.md` and `GLOSSARY.md` rows. Done when the current state is cited.
2. Resolve unknowns; pick by size.
   - Fits one session → *run `grill-design` skill to stress-test the design through a relentless interview, resolving decisions and recording glossary terms, assumptions, and ADRs.*
   - Larger than one session → `wayfinder` is human-only: ask the user to run `/wayfinder` with the loose idea to chart decision tickets and resolve them one at a time.
   - Empirical fork inside either → run the `prototype` playbook and let the result decide.
   Done when no open unknowns remain.
3. Spec it. *Run `to-spec` skill to synthesize the resolved decisions into a published spec* with the target branch and Initiative ID. Done when the spec issue URL or offline Markdown path exists.
4. Design it. `to-zdesign` is human-only: ask the user to run `/to-zdesign` with the spec, Wayfinder map or grill-design context, and any existing design to create or extend the authoritative feature design. Done when the design file exists and holds every resolved decision.
5. Check the design against the decisions from step 2; surface any decision lost, contradicted, or still open.

Next: the `architect` playbook per story or slice.

**Reply:** decisions resolved and how (grill, ticket, prototype), spec and design links, open decisions, recommended next step.
