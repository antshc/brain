# Blast-radius worker prompt

Coordinator: fill placeholders and pass the complete brief verbatim through `subagents` Dispatch. Workers return evidence; the coordinator owns aggregation and delivery.

## Assignment

- Original question — {QUESTION}
- Assigned claim IDs, hypotheses, behaviors, boundaries, and scope stops — {ASSIGNMENT}
- Baseline/head SHAs or recorded local-state identity — {TARGET_IDENTITY}
- Original launch/harness root, source checkout, assigned proof checkout — {ROOTS_AND_CHECKOUT}
- Research grounding and central safety assumptions — {GROUNDING}
- Discovered suites, cited commands, prerequisites, and proposed seams — {TEST_DISCOVERY}
- Constraints, permitted edits, resource ownership, and serialization requirements — {EXECUTION_CONSTRAINTS}
- Absolute path to the blast-radius playbook's How sure are you contract — {PROOF_CONTRACT}
- Exact evidence/patch artifact destinations, or inline-only — {OUTPUT_DESTINATIONS}

## Investigate and prove

Read the supplied proof contract and applicable repository instructions. Treat assigned risks as hypotheses to challenge, not conclusions to justify. Cover only this group; return newly discovered risks with evidence for coordinator assignment. Do not start other proof/review workers, start Arena, or write the final report. Skill-owned evidence delegation is allowed within this assignment; return its blockers and evidence with your result.

Use the supplied `testing-integrations` discovery, preserving the original launch root and explicit code checkout. *Run `testing-integrations` skill to pick the minimal test seam and prove claims with evidence* for the chosen seam and execution; rediscover only missing or stale facts. Inspect fixtures and assertions: mocks that remove the suspect boundary cannot prove it. Use documented commands and the narrowest filter; *run `prove` skill to confirm or refute one technical claim with reproducible evidence* using Execute for uncertain questions, passing existing suite discovery, the assigned checkout, exact evidence destinations and coordinator-owned cleanup. Integration selection goes through Testing Integrations; do not start a second proof worker. Record unavailable suites, prerequisites, and skipped tests.

Add or adapt tests and temporary production instrumentation only within the assigned owned proof worktree and permitted scope. Never weaken valid assertions or skip failing tests to obtain proof. Record patch hashes per execution. Changes to production behavior cannot prove the original target safe; rerun without instrumentation or justify why it preserves the claimed behavior. Keep candidate fixes separate from verification.

Attempt executable proof for every assigned claim. Require an assertion of observable behavior and confirm intended tests actually executed; a successful exit or zero collected tests proves nothing. To attribute a defect to this change, compare the same proof against the pinned baseline and target; otherwise mark regression attribution unproven with the reason.

Follow the supplied constraints: do not modify the user's checkout, post comments, commit, push, deploy, or reset/clean that checkout. Do not choose artifact paths, remove worktrees, or clean shared resources; return ownership and leftovers to the coordinator. Redact private data.

## Evidence return

Return inline, one record per assigned claim, including failed or blocked attempts:

- **Identity:** claim ID, assigned behavior, inspected scope, baseline/head or local-state identity, environment, and applied patch hashes.
- **Finding:** failure mechanism, source `file:line`, likelihood, impact, verdict (`confirmed | cleared | unresolved`), highest supported ladder level, and scope of the conclusion.
- **Proof:** method, cited command source, exact command/working directory/filter, executed test names, total/passed/failed/skipped counts, observed output, and authorized artifact paths. For runtime checks, return the observation instead of test counts.
- **Unproven:** without executable proof, write `unproven`, reason, consequence, and exact next check. Preserve supported source conclusions; distinguish regression attribution from defect existence.
- **Coverage:** behaviors checked/excluded, stopping reasons, assumptions, conflicting evidence, newly discovered risks, and blockers.
- **Handoff:** reusable regression patches, instrumentation diffs, evidence artifacts, worktree ownership record, external resources, and retention/cleanup needs. Report missing artifacts explicitly.
