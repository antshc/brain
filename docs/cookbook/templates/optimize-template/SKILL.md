---
name: optimize-template
description: Optimizes throughput, latency, and resource use with production-representative baselines, repeatable measurements, and proven regression protection.
---

# Performance Skill Template

## Inputs
- `{{metric|User-visible performance metric and target}}`
- `{{environment|Workload, hardware, data, and version constraints}}`

## Workflow
1. Measure the current bottleneck under a representative workload. *Done when* baseline metrics and limiting factors are recorded.
2. Remove unnecessary work before adding complexity; propose one measurable change. *Done when* the expected gain is falsifiable.
3. Compare baseline and candidate with repeated alternating runs under equivalent conditions. *Done when* variability and resource costs are reported.
4. Keep proven changes, revert unproven ones, and define a regression signal. *Done when* the outcome is measurable and repeatable.

## Guardrails
- MUST NOT fabricate benchmark results or compare non-equivalent environments.
- MUST NOT trade correctness for speed without an explicit contract change.

## Completion criteria
- Measured improvement and its limits are documented, or the unsuccessful optimization is rejected.

## Handoff
- `{{benchmarkReport|Metric, workload, runs, evidence, decision, monitor}}`
