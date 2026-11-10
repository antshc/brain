# Explainer prompt

Fill the placeholders after evidence collection. Use [How](how.md) as the report contract.

## Original question

> {QUESTION}

## Scope and depth

{SCOPE_AND_DEPTH}

## Explorer findings

{EXPLORER_FINDINGS}

## System Inspection guidance

{INSPECTION_GUIDANCE}

## Requested report framing

{OUTPUT_SHAPE}

## Synthesize

Draft from the supplied evidence. Lead with the answer and explain the mechanism from trigger to outcome. Combine overlapping findings, cite the decisive evidence in place, and apply the supplied inspection guidance where it affects the answer. Explain any deciding lane behavior, data rule, or provider behavior in the same mechanism. Mark conflicting evidence, assumptions, and unknowns. Separate observed results from what code allows.

Use the applicable lens guidance to choose a diagram or table when it clarifies the mechanism. Build it from verified evidence. When a missing fact could change the answer, identify the claim and exact check for Research to verify.

Return one Markdown draft inline for Research to validate and save.
