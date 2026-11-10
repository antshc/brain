# Explorer prompt

Fill the placeholders and pass the resulting brief verbatim to Hunter as `@work` in an Explore request. Set `@target` and the lookup `@shape` and `@depth` as applicable. Pass the Evidence return as the worker's inline `@outputShape` and include any caller-supplied framing. Research passes the evidence to the Explainer.

---

## Original question

> {QUESTION}

## Assigned angle

{EXPLORATION_ANGLE}

- Targets or refs — {TARGETS_OR_REFS}
- Research depth — {DEPTH}
- Applicable lens and proof checks — {LENS_AND_CHECKS}

Resolve the named targets and read contracts first using Hunter's Explore procedure. Focus on the assigned angle. Cite decisive source lines and distinguish executing source from documented intent and runtime observations. Apply only the supplied proof checks for the assigned angle.

Stay read-only under Hunter's rules. Resolve C# dependencies through Hunter's NuGet tactic when needed. Keep search roots bounded to the resolved targets and package cache. Return evidence inline using Evidence return.

If static evidence leaves a material claim open, run a read-only check only with authorized access and a safe target. Record the command or query, environment, and result. If the check needs mutation, unavailable access, or an unsafe target, report the claim, blocker, and exact next check.

## Evidence return

- **Components** — key types or services, their roles, and source references.
- **Flow** — ordered steps, decisions, data, and calls, with citations for each material claim.
- **Boundaries** — inputs, outputs, contracts, and deciding behavior at each handoff or store.
- **Gotchas** — relevant failure paths, edge cases, conflicts, and surprising behavior.
- **Runtime** — checks and observed results, when applicable.
- **Files read** — paths the coordinator can verify.
- **Open questions** — assumptions, unknowns, and evidence gaps with the next exact check.
