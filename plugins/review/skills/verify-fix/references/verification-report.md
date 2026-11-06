# Verification report

Keep reports concise but auditable. State mode, repository, target/head, baseline, original symptom/evidence, and inspected scope. Cite real `file:line` for nontrivial claims; separate confirmed defects, cleared concerns, and unproven assumptions. Report only executed commands as executed. Include target revision, exact command, result, and signal-bearing redacted output; name missing/skipped checks and why.

## Full

- **Verdict:** VERIFIED, FAILED, or INCONCLUSIVE under Report's gate; state the decisive evidence or blocker.
- **Fix correctness:** root cause → fix mechanism → original-scenario result; distinguish introduced regressions from an unresolved original defect.
- **Impact:** critical safety facts, proof level and execution, confirmed risks, cleared risks, unproven risks. Give likelihood/impact only where evidence supports them.
- **Tests:** risk → existing test → gap mapping; added/updated tests and changed paths; baseline red/fixed green results or why comparison was unavailable.
- **Checks:** required/relevant test results; separate pre-existing failures, introduced failures, flakes, and environment blockers.
- **Limitations:** missing evidence/seams, unchecked scope, residual risk, and cleanup failures or preserved temporary paths. Track user-supplied artifacts and what each contributed.

No findings after a complete review means no confirmed defects found in the inspected scope. It does not waive execution or critical-risk evidence requirements. A missing original-defect signal or critical proof prevents VERIFIED. A confirmed relevant failure takes precedence over missing evidence; report both when returning FAILED.

## Impact

Use What to hand back from Change impact analysis. Add scope/baseline and exact proof commands/results. Mark unavailable proof unproven and state its confidence-ladder level. State any uninspected scope. Return an impact assessment, not VERIFIED; no broad test campaign or persisted tests by default.

## Assess-tests

Return the risk-to-test mapping, prioritized missing cases and levels, and seam/assertion limitations. Include any narrowly necessary diagnostic commands/results. State whether the inventory was complete for the requested scope. Return a coverage assessment, not a safety verdict; no test edits by default.

## Incomplete

Name the blocked operation, essential evidence missing, completed independent checks, and smallest next action that would resolve it. In full mode use INCONCLUSIVE unless a relevant confirmed failure already requires FAILED. In focused modes mark the assessment incomplete or the critical fact unproven. Never substitute skipped checks or an empty findings list for evidence.
