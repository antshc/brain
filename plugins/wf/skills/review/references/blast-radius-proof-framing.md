# Blast-radius proof framing

Coordinator: fill placeholders and pass the sections below verbatim as the `prove` request fields. Prove runs the claims; the coordinator owns risk judgment, aggregation and delivery.

## Claims

One Claim per risk or safety claim from the behavior inventory:

- ID — the claim ID.
- Question — the hypothesis to challenge, including the central safety fact: {CLAIM}
- Criteria — the observable behavior that confirms the defect vs. clears it for the exercised conditions: {CRITERIA}
- Baseline — the pinned baseline SHA, so attribution compares the same proof against baseline and target: {BASELINE}
- Group — shared mutable resources that require sequential runs: {GROUP}

## Facts

- Original question — {QUESTION}
- Target identity: head SHA or recorded local-state identity — {TARGET_IDENTITY}
- Original launch/harness root and source checkout — {ROOTS}
- Research grounding paths and central safety assumptions — {GROUNDING}
- Suite commands and prerequisites already cited in grounding, or none; provers select seams themselves — {KNOWN_SUITES}

## Limits

Permitted edits: tests and temporary production instrumentation only inside Prove-owned worktrees. Do not modify the user's checkout, post comments, commit, push, deploy, or reset/clean that checkout. Redact secrets, credentials and customer data. {EXECUTION_CONSTRAINTS}

## Framing

Apply the How sure are you ladder at {PROOF_CONTRACT}. Return per claim, in addition to Prove's fields:

- **Finding:** failure mechanism, source `file:line`, likelihood, impact, verdict (`confirmed | cleared | unresolved`), highest supported ladder level, and scope of the conclusion.
- **Unproven:** without executable proof, write `unproven`, reason, consequence, and exact next check. Keep supported source findings as grounding only; they cannot confirm or clear a claim. Distinguish regression attribution from defect existence.
- **Coverage:** behaviors checked/excluded, stopping reasons, assumptions, conflicting evidence, newly discovered risks.

## Destination

Report folder under the absolute run directory: {OUTPUT_FOLDER}. Retention: keep worktrees only when a requested follow-up needs runnable state.
