# Diagnostic Log: {{bugTitle}}

**Rules** — apply while filling this scaffold, then delete this block and every `**Rules:**` line from the result.

- Update the log at the end of every phase, before starting the next one; a phase not yet reached keeps its placeholders.
- Every command, output, and artifact is redacted per **Redact** in the skill — `<REDACTED>` in place of each secret.
- Quote only the output lines that carry the signal; never paste a full dump.
- Record dead ends as they happen — a rejected loop, a falsified hypothesis, a probe that proved nothing is the log's most reusable content.

- Reported symptom: {{the user's description, verbatim}}
- Captured symptom: {{exact error message, wrong output, or timing — filled in Phase 2}}
- Environment: {{branch/commit, runtime, config, or dataset the bug reproduces against}}
- Status: building-loop | reproducing | hypothesising | instrumenting | fixing | done | blocked
- Correct hypothesis: {{H-number and one-line statement, or — until confirmed}}

## Phase 1 — Feedback loop

**Rules:** one row per loop attempted, in the order tried; `Outcome` says why it was kept or rejected (not red-capable, flaky, slow, needs a human).

| # | Approach | Command | Outcome |
|---|---|---|---|
| 1 | {{failing test, curl, CLI, harness, ...}} | `{{command}}` | {{kept, or rejected because ...}} |

Loop: `{{the one red-capable command}}`

```text
{{redacted output of its first run}}
```

- [ ] Red-capable
- [ ] Deterministic {{or pinned reproduction rate}}
- [ ] Fast {{runtime}}
- [ ] Agent-runnable

## Phase 2 — Reproduce + minimise

- Runs: {{red count}}/{{total runs}}
- Matches reported symptom: {{yes, or how it differs}}

**Rules:** one row per cut, in the order tried; `Load-bearing` is yes when the cut turned the loop green and was restored.

| Cut | Verdict after cut | Load-bearing |
|---|---|---|
| {{input, caller, config, data, or step removed}} | red \| green | yes \| no |

Minimal repro: {{what remains, and where it lives}}

## Phase 3 — Hypotheses

**Rules:** rank before testing; `Status` moves from open to falsified or confirmed as Phase 4 evidence lands, and `Evidence` names the probe row that decided it.

| # | Hypothesis | Prediction | Status | Evidence |
|---|---|---|---|---|
| H1 | {{if X is the cause}} | {{changing Y makes the bug disappear / Z makes it worse}} | open \| falsified \| confirmed | {{P-number}} |

User input on ranking: {{re-ranks, ruled-out hypotheses, or — when AFK}}

## Phase 4 — Instrumentation

- Debug tag: `[DEBUG-{{tag}}]`

**Rules:** one row per probe; each probe tests one prediction and changes one variable.

| # | Tests | Probe | Observation | Verdict |
|---|---|---|---|---|
| P1 | {{H-number}} | {{breakpoint, targeted log, measurement}} | {{redacted signal}} | {{supports / refutes H-number}} |

## Phase 5 — Fix + regression test

- Root cause: {{mechanism, with file reference}}
- Fix: {{change summary, with file reference}}
- Regression test: {{test name and seam, or the missing-seam finding}}
- Test failed before fix: {{yes / n/a}}
- Test passes after fix: {{yes / n/a}}
- Original loop after fix: {{green, with redacted output line}}

## Phase 6 — Cleanup + post-mortem

- [ ] Original repro no longer reproduces
- [ ] Regression test passes, or absence of seam is documented
- [ ] All `[DEBUG-{{tag}}]` instrumentation removed
- [ ] Throwaway prototypes deleted or moved
- [ ] Correct hypothesis stated in the commit / PR message

Prevention: {{what would have prevented this bug, and any architectural hand-off}}
