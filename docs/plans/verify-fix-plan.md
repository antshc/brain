# Plan: Consolidate `blast-radius` into self-contained `verify-fix`

Status: **Planning only — do not implement this plan while reading it.**

Repository: `antshc/brain`  
Target plugin: `plugins/review`  
Primary new skill: `plugins/review/skills/verify-fix/SKILL.md`

## Goal and rationale

Create one self-contained skill that reviews an implemented bug fix and gathers executable evidence that the fix corrects the reported defect without breaking relevant existing behavior. It must also support two explicitly requested **standalone subflows**: impact analysis (the former `blast-radius` behavior) and test assessment. Users should not have to run the complete verification workflow to ask either focused question.

The previous proposal delegated impact analysis to the separate `blast-radius` skill and reused references from other skills. **That design is superseded.** A fresh agent session must be able to execute any mode by reading only `verify-fix/SKILL.md` and its own `references/`. Copy and adapt the necessary procedural guidance; do not rely on invoking `blast-radius`, `code-review`, `diagnosing-bugs`, `how`, `why`, `writing-style`, or another skill.

Why: a generic “review the fix” prompt encourages optimistic, diff-only conclusions. The new skill must force a risk-oriented investigation, meaningful tests, execution, and an evidence-backed verdict, while keeping lightweight focused requests fast.

## Source-of-truth material to inspect before implementation

Read the current files from the target branch, since they may have changed since this plan was written:

1. `plugins/review/skills/blast-radius/SKILL.md` — **primary source** for impact-analysis behavior. Preserve its distinguishing ideas: inspect indirect effects missed by symbol search; find and prove the one or two critical safety facts; inspect external library source, pinned versions, timing, wire/storage formats, consumers, and downstream effects; distinguish confirmed risks from cleared risks; show actual executed proof and its confidence level. Its evidence ladder is: assertion → cited source → traced impossibility → executed test/script → running-app reproduction. Adapt, do not mechanically copy references to the `how`, `why`, `writing-style`, or `arena` capabilities.
2. `plugins/review/skills/code-review/references/bug-review-guidance.md` — incorporate its concise correctness, reliability, compatibility, security, and performance inspection dimensions and evidence discipline. **Do not copy** the PR inline-comment schema, reviewer axis contract, or read-only limits that conflict with test writing.
3. `plugins/wf/skills/diagnosing-bugs/SKILL.md` — incorporate the minimized reproduction, correct test seam, red-on-pre-fix/green-on-fixed verification, original-scenario rerun, and deterministic feedback-loop principles. **Do not copy** the entire diagnosis/hypothesis process: this skill starts with an existing fix, not a new investigation.
4. `plugins/review/skills/code-review/SKILL.md`, `plugins/review/plugin.json`, and repository conventions — inspect integration and auto-discovery. Do not turn `verify-fix` into a PR-comment posting skill.
5. Search the **whole repository** for references to `blast-radius` as a skill name or path before removing it. Update genuine invocations/documentation; ordinary prose such as “blast radius of this change” need not be renamed.

## Public interface and mode routing

One skill: `name: verify-fix`. The `description` must explicitly trigger on bug-fix verification, regression-safety review, “blast radius / what could this change break,” and “assess tests / test coverage gaps.” Preserve familiar user phrasing after retiring the old skill.

| User intent / example | Mode | Scope and expected result |
|---|---|---|
| “Verify this fix”, “review fix regressions” | `full` (default) | Complete review, impact analysis, test assessment, missing tests, test execution, evidence verdict |
| “Blast radius of this change”, “what else could break?” | `impact` | Only change-impact investigation and proof of critical assumptions; no broad test campaign |
| “Assess tests for this fix”, “which regression tests are missing?” | `assess-tests` | Only discover/map existing tests and identify gaps; report recommended test cases, without editing by default |

Do **not** force the user to supply a mode flag if intent is clear. Optional explicit form: `verify-fix <mode> <diff|commit|branch|local change|PR checkout>`. Resolve the target and its comparison baseline; ask when ambiguous. Never silently expand `impact` or `assess-tests` into full verification. Standalone mode may perform narrow, safe proof checks where its definition requires them.

## Full-mode workflow and gates

1. **Establish scope and baseline.** Identify change, pre-fix baseline, original bug/reproduction (if available), affected repository, and tests. Inspect repository instructions and preserve dirty worktrees. If original defect evidence is unavailable, say so; do not invent it.
2. **Review correctness.** Trace how the fix addresses the root cause. Assess input/state validity, failure paths, cancellation/concurrency/idempotency, interfaces, compatibility, security, and material performance effects. Report a concrete triggering path for a proposed defect, not speculation.
3. **Change Impact Analysis.** Execute the fully embedded former blast-radius method. Follow callers, transitive consumers, shared state, data formats, external dependencies, and activation/configuration paths. Identify critical safety facts and test or reproduce them with real code. Separate confirmed risks, cleared risks, and unverified risks; report likelihood/impact when evidence permits. This step is the entirety of `impact` mode.
4. **Assess existing tests.** Locate tests for the bug and affected behavior. Build a concise risk → existing test → gap mapping. Check the *seam* (whether a test exercises the actual failure mechanism) and assertion strength; code coverage alone is not proof. This step is the entirety of `assess-tests` mode, with scope/context discovery from step 1.
5. **Add necessary safeguards (full mode only).** Write focused tests for the original defect and important behavior-preservation gaps; prefer observable contracts, invariants, boundary cases, integration seams, and failure paths. When practical, prove the bug reproduction test fails on pre-fix code and passes on fixed code using isolated, non-destructive checkout/worktree techniques. Do not let the test merely echo the current implementation. If a correct test seam does not exist, record the limitation instead of writing a misleading test.
6. **Execute verification.** Run relevant existing and new unit/component/integration tests, expand to broader suites proportionate to risk. Apply *conditional*, not universal, methods: contract testing for interfaces; characterization for legacy behavior; property-based testing for input spaces/invariants; mutation testing for weak assertions; differential testing for expected unchanged outputs; stress/concurrency testing for races; performance baselines for hot paths. Record exact commands and results, distinguish pre-existing from new failures, and do not substitute skipped tests for passes.
7. **Evaluate evidence.** Return `VERIFIED` only if required checks passed and no critical unverified risk remains; `FAILED` when a relevant defect/regression or required-check failure is found; `INCONCLUSIVE` when essential evidence is missing or execution blocked. Report what changed in tests, executed evidence, cleared concerns, defects, and residual limitations. Never guarantee absence of every possible regression.

## Focused mode contract

- `impact`: review change + indirect effects + critical executable proof + risk/cleared/unproven report. It may use temporary read-only probes or safe disposable test harnesses but MUST NOT persist new test changes unless explicitly requested. Existing skill's “prove the one fact” discipline is non-negotiable; if proof is impossible, state `unproven` rather than inventing certainty.
- `assess-tests`: identify relevant existing tests, assess coverage and assertion quality, and propose prioritized missing cases with appropriate test level. Default is **read-only**: do not add tests or run the entire suite. A narrowly run diagnostic test may be useful when necessary to evaluate a claimed assertion; disclose it. The report is an assessment, not a `VERIFIED` verdict.
- `full`: may add/update tests; MUST NOT silently change the production fix. New source defects are reported back to the implementer. Must not create PR comments, push commits, or invoke deployments merely to produce evidence.

## Guardrails and evidence contract

- MUST inspect relevant code beyond the changed lines. MUST use real `file:line` evidence for nontrivial claims. Absence of a search match alone is not proof of safety.
- MUST distinguish intended behavior changes from regressions. MUST protect pre-existing correct behavior, not freeze known incorrect behavior.
- MUST run relevant tests in `full` when safely possible; MUST NOT claim execution if blocked. No unsafe writes or production-impacting test commands without authorization.
- MUST preserve unrelated worktree changes. Use isolated temporary worktrees for baseline comparisons; do not reset/clean the user's checkout.
- MUST NOT alter production code in any mode. Test-file changes are allowed only in `full` or upon explicit request.
- MUST classify pre-existing failures, introduced failures, flaky outcomes, and environment blockers separately.
- MUST redact secrets, credentials, and customer data from captured evidence.
- MUST keep outputs concise, but include enough evidence to audit the conclusion.

Suggested output contract:

| Field | Full | Impact | Assess-tests |
|---|---|---|---|
| Scope and baseline | Yes | Yes | Yes |
| Root-cause/fix correctness | Yes | Change behavior only | Context only |
| Risks / cleared / unproven | Yes | Yes | Test risks/gaps |
| Test inventory/gaps | Yes | If needed for proof | Yes |
| New tests and changed files | Yes, if applicable | No by default | No by default |
| Exact executed checks and results | Yes | Proof checks | Any diagnostic checks |
| Verdict | VERIFIED / FAILED / INCONCLUSIVE | Impact assessment with proof level | Coverage assessment, not a safety verdict |

## Planned file changes

```text
plugins/review/skills/
  verify-fix/
    SKILL.md                         # Router, full/focused flow, invariants, verdict gate
    references/
      impact-analysis.md            # Adapted complete blast-radius method and proof ladder
      test-assessment.md            # Mapping risks to tests, seam/coverage judgment
      verification-strategies.md    # Conditional test technique selection and execution
      verification-report.md        # Mode-specific report contracts/evidence rules
  blast-radius/SKILL.md              # REMOVE after migration verification
```

Keep references one level deep and loaded by the relevant mode; the router itself stays short. No scripts initially. Update only verified inbound links/skill mentions when retiring `blast-radius`. The plugin's `skills: ["./skills"]` auto-discovery likely needs no modification; verify rather than assume.

## Implementation sequence

1. Re-read source files and search all references on the target branch.
2. Draft self-contained `SKILL.md`, mode routing, and references. Preserve distinct source behavior, not irrelevant historical wording.
3. Test routing against six representative prompts: full verification, implicit blast radius, explicit `impact`, implicit test assessment, explicit `assess-tests`, and ambiguous scope requiring clarification.
4. Test full-mode evidence gate on a representative bug fix and ensure read-only modes do not edit tests or production files.
5. Compare migrated impact guidance against the original `blast-radius` point by point; only then remove `blast-radius/SKILL.md` and update references.
6. Validate skill metadata, links, markdown style, and repo-specific skill checks; report exact changed paths and test outcomes.

## Acceptance criteria

- One discoverable `verify-fix` under `plugins/review`, with **three independent modes** and no runtime reliance on another skill.
- Existing `blast-radius` capabilities retained in `impact` mode and original skill retired after migration.
- `assess-tests` works independently, with no test-writing side effect by default.
- `full` reviews correctness, adds missing meaningful tests where feasible, runs relevant existing and new tests, and returns evidence-backed verdicts.
- No production-code changes, PR posting, or unexpected repo mutations from the verification skill.
- A fresh implementer can follow this plan and the source paths without needing this conversation.

## Important non-goals

- Do not merge `diagnosing-bugs`, `code-review`, or their unrelated workflows into `verify-fix`.
- Do not build a new testing framework, test runner, agent scheduler, or generic CI orchestrator.
- Do not require mutation/property/contract/performance testing for every tiny change.
- Do not claim mathematical certainty that nothing else breaks.
