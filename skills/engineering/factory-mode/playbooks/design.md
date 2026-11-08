### Design

**You own the destination. Resolve unknowns, then synthesize.** Produces a spec and an authoritative feature design, not code.

1. Research the current state through Non-negotiables: how the affected flow works, where it lives, and relevant architecture documentation and domain terminology. Done when the current state is cited.
2. Resolve unknowns; pick by size.
   - Fits one session → *run `grill-design` skill to stress-test the design through a relentless interview, resolving decisions and recording glossary terms, assumptions, and ADRs.*
   - Larger than one session → `wayfinder` is human-only: ask the user to run `/wayfinder` with the loose idea to chart decision tickets and resolve them one at a time.
   - Empirical fork inside either → run the `prototype` playbook and let the result decide.
   Done when no open unknowns remain.
3. Optional: sketch it. Run when the user asks for a sketch or the code shape (types, signatures, module boundaries) is still contested; otherwise skip. *Run `code-sketch` skill to draft a usage-first code sketch with types, signatures, module map, and rationale* from the resolved decisions. Then loop:
   1. Present the usage, module map, key signatures, open questions, and absolute artifact paths; ask the user to **approve** or give corrections.
   2. Corrections → apply them to the sketch and rationale so both agree, then repeat from 3.1. Never write production code.
   3. Approve → exit the loop and suggest the `to-spec` handoff with the approved sketch and rationale paths.
   Done when the user approves the sketch or the step is skipped.
4. Spec it. *Run `to-spec` skill to synthesize the resolved decisions into a published spec* with the target branch, Initiative ID, and the approved sketch and rationale paths when step 3 ran. Done when the spec issue URL or offline Markdown path exists.
5. Design it. Ask the user to run `/draft-artifact design` with the spec, Wayfinder map or grill-design context, and any existing design to create or extend the authoritative feature design. Done when the design file exists and holds every resolved decision.
6. Check the design against the decisions from step 2; surface any decision lost, contradicted, or still open.

**Reply:** decisions resolved and how (grill, ticket, prototype), approved sketch paths when sketched, spec and design links, open decisions, recommended next step.
