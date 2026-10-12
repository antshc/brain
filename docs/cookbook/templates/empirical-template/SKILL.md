---
name: empirical-template
description: Measures uncertain integration behavior or performance improvements using falsifiable hypotheses, controlled experiments, repeatable benchmarks, and evidence-based decisions.
---

<!-- @: Copy into a concrete skill folder; rename folder and frontmatter name, then replace all task placeholders. -->

# Empirical experiment

## Hypothesis
- Test {{hypothesis|Falsifiable claim or candidate design}}.
- Decide using {{threshold|Metric, pass condition, and rejection threshold}}.

## Controlled setup
1. Fix {{environment|Versions, workload, resources, external boundaries}} and record a baseline when comparing changes. *Done when* conditions can be reproduced.
- MUST NOT compare non-equivalent workloads or substitute a mock for the uncertain real boundary.

## Trials
2. Exercise the smallest real scenario needed to distinguish candidates. *Done when* observations are repeatable.
3. When measuring performance, alternate baseline and candidate runs; account for variance and resource cost. *Done when* both have comparable samples.
- {{procedure|Setup, input, repetitions, and capture method}}

## Measurements
- {{results|Raw observations, units, variability, limiting factors}}
- MUST NOT invent numbers or treat anecdotal speed as a benchmark.

## Decision
- {{outcome|Accept, reject, or defer candidate with evidence}}
- {{cleanup|Owned temporary resources cleaned; rejected optimization reverted}}

## Completion criteria
- The hypothesis is supported, rejected, or explicitly unresolved by measurements that another executor can reproduce.
