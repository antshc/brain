# Statechart review

## Inputs

- Code scope: paths or a description of a stateful behavior, with its expected rules when known.
- PR scope: PR URL and an available local checkout. Do not clone as a fallback.

Use this route to check finite state-transition behavior with TLA+ and TLC. It produces a model report and Mermaid statechart; it does not post PR comments. Use `code` for a complete PR review or posting findings.

## Workflow

1. **Resolve scope.** For a PR, *Load and follow the `github` skill to read the PR title, body, diff, and changed files for this statechart review.* Inspect the affected implementation, callers, tests, and explicit behavior contracts. If no target or stateful behavior is clear, ask which to model. Do not invent expected behavior.
2. **Choose rules.** Model only rules stated by the user, PR context, or applicable contracts and tests. Write each as an `INVARIANT`; add a variable when the rule needs state the implementation does not expose directly. Never weaken a rule to make it hold. If there are no defensible rules, report the gap instead of presenting a pass.
3. **Write a finite model.** Work in a scratch directory outside the repository. Define `Init`, `Next`, state variables, and named actions. Define `Next` as a disjunction of those actions so TLC names each transition. Keep constants small or add a `CONSTRAINT`. A correct terminal state still fails `NoDeadlock`; add an end-only stuttering action such as `Done == phase \in {"paid", "failed"} /\ UNCHANGED vars`. If an invariant or property is already named `NoDeadlock`, use `CHECK_DEADLOCK`.
4. **Describe the chart.** Write a view module and pass it with `--view`. `state(vars)` returns a user-facing string for a flat chart, an array for parent states, or an object for parallel regions. Keep variable names out of labels. `step(action, from, to)` returns the transition label in the reader's words, not code or TLA+ names. Add a condition in brackets only when it is not shown by another region. When an unlabelled variable determines the destination, name the result. Optional `group(vars)`, `colors`, and `title` set phases and title. Keep all view functions deterministic and dependent only on their arguments.
5. **Keep the chart legible.** Aim for 20 arrows or fewer. Coarsen labels first, but preserve every state on a bug path and every distinct rule-breaking mark. Do not merge states that break different rules. Split a label when a model step that stays in that chart state matters to the reader. If needed, return `null` from `step()` to hide unneeded transitions. Keep every chart state reachable, retain an outgoing arrow for each nonterminal state with model steps, and hide all equivalent steps for an arrow or none. Report hidden steps.
6. **Run the model checker.** From this skill's base directory, run:

   ```sh
   scripts/statechart/statechart SPEC.tla --config FILE --view FILE --out NEW_DIR
   ```

   Exit 0 means all checked rules hold, exit 1 means a rule breaks, and exit 2 means TLC or the command failed. The command requires Node 22.18+ (or supported Bun/Deno), and installs pinned TLC and Java with `mise` on first use; that run needs network access. Set `TLA2TOOLS` and optionally `JAVA` to use an existing installation. `NEW_DIR` must be new or empty. Read `report.md`, `chart.mmd`, and `tlc.out`; inspect `tlc-RULE.out` when a broken rule has no chart path.
7. **Replay every counterexample.** Follow each reported action against the actual code, one action at a time, as a test or live repro. Treat a model-only counterexample as unverified, not a code finding. For a PR, anchor each confirmed finding to a changed line and retain code/test evidence. Do not post from this route.
8. **Report limits and result.** Show `chart.mmd` in a `mermaid` fence. A `breaks` mark means every model state represented by that chart state breaks the rule; `mayBreak` means only some do. In parallel regions, explain a broken combination when the mark is not on a single region state. Match each mark to its rule, including when several rules share one mark. TLC continues past invariant violations. A `CONSTRAINT` checks rules at a boundary state but does not explore it or check it for deadlock; an `ACTION_CONSTRAINT` still checks rules in states reached by excluded steps, even when reached another way. A `VIEW` or `SYMMETRY` can merge model states into one representative chart state. After the first broken rule, TLC caps subsequent checks at 100,000 distinct states; rules listed as not checked are unknown, not passing. State model omissions, hidden steps, state bounds, and unchecked rules. The chart shows the full graph only up to 500 states; above that it draws bug paths only, and writes no chart when no rule breaks.

## Output

Return the Mermaid chart, a concise model-checking summary, confirmed code-replayed findings, and explicit model limitations. Say `No confirmed state-machine finding` only when every modeled rule was checked, every relevant state was explored, and each counterexample was replayed. Otherwise report `incomplete` or keep unverified counterexamples separate from confirmed findings.

## Chart rendering

The generated state machine uses the doc-diagram dark base palette and the stable ID `statechart-model`. Read [Statechart rendering](../references/statechart-render.md) when the user asks for an SVG or another rendered image.
