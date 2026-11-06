# Verification strategies

1. Read repository test commands and configuration. Select required checks from affected behavior, critical risks, existing test coverage, and repository requirements. Record why each check matters before treating it as required; do not drop a failed check to obtain a pass.
2. Run relevant existing and new unit/component/integration tests. Expand to broader suites proportionate to risk and repository requirements. Record exact command, working directory, target/baseline revision, result/exit status, and relevant redacted output. Skipped or unrun tests are not passes.
3. Choose additional methods only for an observed need:

   | Trigger | Method and evidence |
   |---|---|
   | Public interface, serialized/wire/storage format, mixed-version consumers | Contract tests at the real boundary; prove producer/consumer compatibility |
   | Legacy behavior with weak specifications | Characterization of intended unchanged behavior; exclude known bugs |
   | Large input space or invariants | Property-based tests; record seeds and minimized counterexamples |
   | Assertions may miss meaningful wrong behavior | Mutation testing in disposable test fixtures/harnesses only; never mutate production code. If the tool requires source mutation, report the limitation and select another method |
   | Outputs must remain unchanged | Differential testing on the same inputs against isolated baseline and fixed versions; allow only intended differences |
   | Races, ordering, shared state | Stress/concurrency tests with recorded schedule/seeds, repetitions, failure rate, and bounded runtime |
   | Material hot path, throughput, latency, allocation, query changes | Comparable performance baselines using the same workload/environment |

**Perf branch.** For performance regressions, logs are usually wrong. Instead: establish a baseline measurement (timing harness, `performance.now()`, profiler, query plan), then compare isolated pre-fix and fixed versions. Measure first, judge the fix second.

4. Classify each failing outcome separately: introduced failure, relevant pre-existing failure, flaky outcome, or environment blocker. Re-run against the isolated baseline when needed to distinguish them. A baseline failure does not excuse a required-check failure; report its relevance and limits. Do not call a flaky or blocked run a pass.
5. Re-run the original un-minimized scenario; inspect the final diff/status to confirm only permitted test changes remain. Clean up only run-owned probes/worktrees and report preserved paths or cleanup failures. Return evidence to Report; do not fix production defects.
