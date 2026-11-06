# Verify-fix implementation report

Source snapshot: `7446c2a71bc86755c016381cabb94ab8a7dc954a`. Implements [verify-fix plan](verify-fix-plan.md). Authoring follows the repository's write-skill procedure; the plan's verbatim-migration policy takes precedence over stylistic pruning.

## Files and integration

- Added `plugins/review/skills/verify-fix/SKILL.md`, five local references, and `LICENSE`.
- Replaced the retired skill's README entry with the three-mode interface.
- Retired `plugins/review/skills/blast-radius/SKILL.md` after migration comparison.
- `plugins/review/plugin.json` already discovers `./skills`; no manifest or marketplace change required.
- Repository search found the README entry, source skill, implementation plan, and an external upstream link in `docs/cookbook/index.md`. Preserve historical plan references and that upstream source link; they are not live invocations of the retired local skill. Excluded `_backup/`, `_in-progress/`, and `docs/kbs` per repository instructions.

## Blast-radius migration inventory

Destination prefix: `plugins/review/skills/verify-fix/`.

| Original section/instruction | Destination | Treatment and reason |
|---|---|---|
| Frontmatter name, description, manual-only switch | `SKILL.md` Inputs and routing | Replace identity with discoverable three-mode router; retain familiar blast-radius trigger |
| Title | `references/impact-analysis.md` title | Rename to Change impact analysis for mode identity |
| Opening use cases and grep limitation | Impact introduction | Unchanged |
| Companion paragraph naming how/why | Omitted | Cross-skill runtime relationship forbidden by self-contained plan |
| Don't trust your own writeup | Impact same heading | Unchanged, including one-or-two-facts requirement |
| How sure are you and five-level evidence ladder | Impact same heading | Unchanged, including real-library script example |
| Steps 1 | Impact Steps 1 | First sentence unchanged; replace why step 2 with local pinned PR/commit context established by Scope and baseline |
| Steps 2 | Impact Steps 2 | Unchanged, including already-dead cache example |
| Steps 3 | Impact Steps 3 | Unchanged: pinned version/local patch, timing, framework examples, formats, flags, downstream effects |
| Steps 4 | Impact Steps 4 | Retain risk/cost, confirmed/cleared, file:line and no fabricated caller/API instructions; remove why invocation; append absence-of-match is not safety proof |
| Steps 5 | Impact Steps 5 | Unchanged executable-proof requirement |
| Steps 6 | Impact Steps 6 | Replace arena skill invocation with inline independent-review task/input/output and side-effect boundaries; retain multi-model intent and explain unavailable-review limitation |
| What to hand back, all five bullets | Impact same heading | Unchanged |
| writing-style instruction | Impact closing paragraph | Replace invocation with concise plain-language instruction; preserve cite-code and privacy constraints |
| Reply instruction | Impact closing paragraph | Unchanged |
| Focused-mode limits | Impact before What to hand back | Added disposable proof/no broad campaign/no persisted tests limits and explicit unproven outcome |

## Diagnosing-bugs migration inventory

Source attribution remains in `SKILL.md` Attribution. `LICENSE` is a byte-for-byte copy of the source's MIT notice, including Copyright (c) 2026 Matt Pocock.

| Original section/instruction | Destination | Treatment and reason |
|---|---|---|
| Identity and diagnosis/fix mode gates | `SKILL.md` routing; `references/bug-reproduction.md` introduction | Replace diagnosis workflow with already-implemented-fix verification; no fresh hypothesis workflow |
| Skip phases only when justified | Workflow and report missing-evidence handling | Replace with explicit scoped mode routing and named limitations; focused modes intentionally omit other phases |
| GLOSSARY/ADRs exploration paragraph | `SKILL.md` Scope and baseline | Unchanged |
| Redact, first paragraph | Bug reproduction Redact | Unchanged, including `<REDACTED>`, env vars, auth headers and signal-only output |
| Redact, insufficient-output sentence | Same | Change diagnose to verify; preserve ask-user handling |
| Phase 1 opening motivation | Same | Replace finding-cause/hypothesis language with verifying an existing fix; retain tight red signal and no code-staring substitute |
| Phase 1 effort instruction | Same | Unchanged |
| Feedback-loop options 1–9 | Same | Unchanged, including tooling examples and `git bisect run`; all probes remain constrained to safe isolated environments |
| Option 10 HITL script | Same | Replace external `scripts/hitl-loop.template.sh` with inline exact actions, expected symptom and repeatable outcome capture; no bundled scripts planned |
| 90%-fixed statement | Same | Replace with feedback-loop-before-verification requirement because fix already exists |
| Tighten the loop | Same | Unchanged, including speed, exact assertion, determinism and timing examples |
| Non-deterministic bugs | Same | Unchanged trigger/repetition/stress/timing guidance; applies to disposable harnesses, not production modifications |
| Cannot build a loop | Same | Preserve stop/list attempts/access/artifact requests; replace production instrumentation request with safe reproduction environment; retain INCONCLUSIVE and independent-check continuation |
| Completion criterion opening and red-capable/deterministic/fast bullets | Same | Unchanged |
| Agent-runnable bullet | Same | Replace external HITL script path with local structured actions/captured outcome |
| Hypothesis-before-command prohibition | Same | Replace with no claimed reproduction without red command; correctness review can continue independently for already-fixed code |
| Phase 2 opening | Same | Retain run/red instruction; add isolated pre-fix baseline and explicit unavailable-baseline limitation, preserving dirty checkout |
| Phase 2 confirmation checklist | Same | Unchanged exact-symptom/reproducibility/captured-signal checks |
| Minimise procedure and load-bearing completion | Same | Unchanged |
| Minimise rationale | Same | Remove Phase 3 hypothesis-space clause; retain regression-test purpose |
| Phase 2 stop gate | Same | Limit to claimed reproduction; independent checks continue with missing evidence recorded |
| Phase 3 hypothesis generation/log | Omitted | Diagnosis-only workflow explicitly excluded |
| Phase 4 instrumentation/debugger/logging/hypothesis log | Omitted | No production modifications or fresh diagnosis; cleanup retains run-owned harness diagnostics |
| Phase 4 performance baseline paragraph | `references/verification-strategies.md` Perf branch | Retain baseline tooling examples; replace bisect/measure-first-fix-second ending with isolated pre/post comparison and measure-first-judge-fix-second |
| Phase 5 heading and explicit-fix gate | Bug reproduction Phase 5 | Regression-test phase; permit tests only in full or explicit test-change request |
| Write test before fix | Same | Test against pre-fix baseline when practical; already-implemented fix remains unchanged |
| Correct-seam definition and shallow-test examples | Same | Unchanged |
| Missing-seam finding paragraph | Same | Unchanged |
| Phase 5 numbered steps 1, 4, 5 | Same | Unchanged failing-test, pass, original un-minimized loop requirements |
| Phase 5 step 2 mutation proof | Same | Keep diff-against-pristine verification for disposable fixtures; exclude production mutation and distinguish synthetic failure from original-defect evidence |
| Phase 5 step 3 apply fix | Same | Run same test against existing fixed code; do not apply/revert production fix |
| Phase 6 required-before-done | Same | Unchanged |
| Phase 6 diagnostic/prototype cleanup | Same | Restrict to run-owned disposable harness diagnostics/prototypes, preserve existing work, account for temporary worktrees and cleanup failures |
| Phase 6 original repro and test/seam checklist | Same | Unchanged |
| Phase 6 correct hypothesis in commit/PR | Same | Put evidenced root cause/fix mechanism in report; no commit/PR posting as verification side effect |
| Output root-cause-report/hypothesis-log links | `references/verification-report.md` | Replace diagnosis schema with local mode-specific report |
| Output artifacts and contributions, changed tests, missing seam, original scenario | Same | Retain required content; no hypothesis-log dependency |
| Attribution/LICENSE | `SKILL.md` Attribution, `LICENSE` | Preserve upstream attribution and complete MIT terms |

## Bug-review guidance migration

| Original | Destination | Treatment |
|---|---|---|
| Review entire diff; continue after first finding | `SKILL.md` Correctness review | Unchanged sentence; remove AXIS/shared contract |
| Five Inspection bullets | Correctness review Inspection | Unchanged |
| Evidence gate first paragraph | Correctness review Evidence gate | Unchanged |
| Exclude speculation/pre-existing/intentional/style/duplicates; unsupported candidates | Same | Unchanged sentences; distinguish unresolved original defect separately from new regressions |
| Missing context, no false execution, safe checks | Same, Constraints, Report | Local unchecked-scope/outcome contract replaces shared failure object; allow tests in full |
| Trigger/behavior/impact, all findings ordered by impact | Same | Local report replaces inline comment schema/anchors and axis contract |
| PR comment formatting, shared schema, empty array, other axes | Omitted | Verification does not post comments or return reviewer-axis JSON |

## New workflow obligations

- Independent full, impact and assess-tests routes; ambiguity stops target selection.
- Scope/baseline and dirty-work protection; read-only PR context acquisition and stale-evidence handling.
- Risk-to-test mapping with seam/assertion judgment and prioritized recommended test levels.
- Focused tests and proportionate execution; conditional contract, characterization, property, mutation, differential, concurrency and performance techniques.
- Mutation tooling requiring production source mutation is reported unavailable; disposable fixtures/harnesses remain allowed.
- Separate introduced/pre-existing/flaky/environment outcomes; FAILED precedes INCONCLUSIVE when both confirmed failure and missing evidence exist.
- No production edits, unsolicited PR comments, commits, pushes or deployments by the resulting skill.
- Final completeness sweep accounts for unchecked scope and limitations.

## Validation

### Migration and structure

- Compared seven exact source spans: impact proof ladder, critical-fact/downstream investigation, all output bullets, reproduction options 1–9, tightening/non-determinism, reproduction checklist, and correct-seam/missing-seam instructions. All retained byte-for-byte within their destination text. The inventories above account for remaining adaptations and exclusions.
- MIT notice byte-identical to the diagnosing-bugs source.
- YAML metadata, 193-character trigger description, folder/name match, 77-line main file, local Markdown reference resolution and retired path absence passed Python assertions. `git diff --check` passed.
- Independent shrink pass retained all six Markdown files unchanged; no uncertain behavior preservation reported. Plan's verbatim policy overrides stylistic shortening.
- `python3 -m pytest tools/tests/unit/repo_consistency -q`: 12 passed.

### Behavioral exercises

Fresh agents used only the completed skill and isolated fixture repositories. Fixture: `allowed(count, limit)` changed from `count <= limit` to `count < limit`; README specifies accepted-request count and maximum capacity. Existing tests cover below/above capacity but omit equality. No fixture files were added to Brain.

| Request | Observed route and behavior |
|---|---|
| Verify this fix | Full; inspected scope, ran tests, added correct-seam regressions, compared isolated baseline and fixed code |
| What is the blast radius; what else could break? | Impact; ran disposable real-code proof, reported evidence level 4, no persistent test edits |
| verify-fix impact | Impact; inspect status/instructions and pin target/baseline first |
| Assess tests; which regression tests are missing? | Assess-tests; identified equality and zero-capacity gaps, no tests executed or edited |
| verify-fix assess-tests | Assess-tests; inspect status/instructions and pin target/baseline first |
| Verify the change, without target/baseline | Default full, unresolved scope; requested repository/change and baseline rather than guessing |

Full exercise: `python -m pytest -q` initially passed 2 existing tests; after adding equality, zero-capacity and first-request cases, the isolated baseline failed 2 and passed 3; fixed code passed all 5. Repeated focused equality test failed on baseline and passed on fixed code. `python -c 'from window import allowed; assert allowed(3, 3) is False; print("Original scenario: fourth request rejected")'` passed. A disposable differential harness checked 10,201 nonnegative integer pairs and confirmed only equality changed. Agent returned VERIFIED for the fixture's documented contract, with integration limits stated. These are the exact exercise commands; the Brain suite uses `python3`.

Impact exercise: disposable importlib harness compared `(2,3)`, `(3,3)`, `(4,3)`, `(0,0)`, `(0,1)` against an isolated baseline; all fixed outputs matched the contract and non-equality outputs remained unchanged. Temporary worktree removed. Assessment exercise identified the direct unit seam and prioritized equality/zero-capacity cases without execution.

Checked final fixture state: full changed only tests beyond the original production diff; impact and assess-tests retained exactly their original production diffs. No commits, pushes, production edits or PR posts were performed by the verification agents. All temporary baseline worktrees were removed. This small fixture validates mode boundaries and red/green execution, not every supported testing technique.

### Repository test results

`python3 .github/scripts/run-python-tests.py` before and after implementation: **1,109 passed, 52 skipped, 3 failed**, identical outcomes. Installed the declared development/Atlassian dependencies after the initial environment lacked pytest. No production Python changed; no type-check command is configured for this Markdown-only change.

Pre-existing failures, reproduced before any implementation files changed:

- `tests/wf/architect/test_checkpoint_contracts.py::test_factory_uses_one_autonomous_feature_flow_and_optional_checkpoint`: expected interrogate wording absent from feature playbook.
- `tests/wf/implement-spec/test_contracts.py::test_template_parity_except_intentional_artifact_section`: existing Related Spec Artifacts template mismatch.
- `tests/wf/research/test_contracts.py::test_request_lists_required_fields`: expected Request delimiter absent.

These failures remain outside this migration. Skipped integration tests are not claimed as passed. Closing sweep accounted for all planned files, mode boundaries, source sections, attribution, retired inbound links and validation limitations.
