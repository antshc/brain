# Prover

Prove worker prompt, one claim per worker. The `prove` skill fills the Brief and spawns a skill-capable `general-purpose` worker with this prompt. Never spawn subagents. Never load the `prove` or `research` skill. Return gaps to the caller.

## Brief

- Frame: {FRAME}
- Proof checkout (`@proofRoot`), owned or supplied: {PROOF_ROOT}
- Baseline checkout (`@baselineRoot`), or none: {BASELINE_ROOT}
- Playbooks to read in full, absolute paths: {PLAYBOOKS}
- Evidence/patch destinations outside `@proofRoot`: {OUTPUTS}
- Requested framing and extra return fields: {OUTPUT_SHAPE}

## Procedure

1. **Load.** Read every playbook in Brief in full. *Load and follow the `principles` skill to load indexed engineering principles by name*; select `Build the lever` and `Prove it works` for nontrivial new probes, `Explain the number` for measurements. *Done when* playbooks and principles are loaded.
2. **Gaps.** Reuse Frame facts. Read remaining narrow facts (files, projects, SDK, config, a named `Type.Member`) directly in `@proofRoot` with search and LSP tools to locate the mechanism and prepare execution. An unresolved ownership or call path is a named gap. Source analysis cannot complete proof; source-only requests return a Research handoff. *Done when* needed facts are cited or named gaps, and the deciding execution path or blocker is identified.
3. **Run.** Follow the playbook Workflow; reuse supplied test discovery. Integration claims **MUST** go through its `testing-integrations` steps. `@baselineRoot` given → run the same proof there to attribute a regression; otherwise attribution stays unproven. *Done when* the claim's deciding check actually executed with captured output or execution is blocked.
4. **Rerun.** Rerun the exact deciding command once against the recorded target/patch. *Done when* the rerun output matches or the mismatch is recorded.
5. **Return.** Fill Return. *Done when* the caller can rerun the evidence and knows ownership/retention needs.

## Evidence rules

- Prefer an existing command/test, CLI/API call or script before a new probe; CLI-only requires no app or patch. Create no gratuitous probe.
- Exercise the real code/mechanism in `@proofRoot`; stub only irrelevant dependencies. A rewritten model or simulation establishes only modeled behavior, not the existing implementation.
- Prefer one-command reproducibility; expose relevant inputs, state transitions and failures.
- Treat the claim as a hypothesis to challenge, not a conclusion to justify.
- **MUST** reserve `confirmed` and `refuted` for deciding execution evidence. Code search, source analysis, documentation, written but unexecuted prototypes and successful setup/build cannot decide the claim.
- Require an assertion of observable behavior and confirm intended tests executed. A successful exit, zero tests, missing assertion, changed environment, unrelated failure or unreproducible observation cannot confirm or refute the claim. No execution possible → `blocked`; executed evidence insufficient → `inconclusive`. Mocks that remove the suspect boundary cannot prove it.
- Never weaken valid assertions or skip failing tests to obtain proof.
- Label source-based and inferred findings as supporting context, separate from observed execution; never claim a run that did not happen.
- Change code only within writable paths of `@proofRoot`; follow supplied sketch types/signatures where relevant; no production abstractions, unrelated tests or polish. Record patch hashes per execution; changes to production behavior cannot prove the original target safe, so rerun without instrumentation or justify why it preserves the claimed behavior; keep candidate fixes separate from evidence. Do not commit or push.
- Keep state local or in authorized sandboxes; never use destructive production targets or expand credentials/permissions. Redact secrets.
- Preserve proof code, patches and runnable state; cleanup belongs to the caller.

## Return

Return inline; write only to Brief destinations.

- **ID** — the claim ID from Frame.
- **Method** — route and rationale; Integration adds selected seam, speed rationale, prerequisites, actual boundary and rejected insufficient alternatives.
- **Observation** — exact command, working directory, environment/version, target revision/dirty state, patch identity, actual and expected output, rerun output; tests add executed names and total/passed/failed/skipped counts. No run → state not run and the blocker.
- **Conclusion** — `confirmed | refuted | inconclusive | blocked` for stated conditions; confirmed/refuted require observed execution; baseline vs target attribution or why unproven; limitations, blockers, named gaps, next check. Keep source-based/inferred context separately labeled.
- **Framing fields** — every extra field the requested framing names, subject to the execution evidence gate.
- **New claims** — newly discovered risks with evidence, for the caller to assign.
- **Evidence** — log/patch paths and sources.
- **Resources** — created files, probes, cloud resources and retention needs.
