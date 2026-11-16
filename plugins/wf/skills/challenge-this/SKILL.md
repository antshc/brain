---
name: challenge-this
description: >-
  Adversarially test a change or design and report reproducible counterexamples. Use for 'challenge this', 'break this design', 'find blind spots', or 'stress test this change'. Not for ordinary PR review → `review`.
---

# Challenge this

Adversaries hunt for ways to break a change or design and return candidate claims; Prove runs them in parallel. Only findings proven by a run survive. Report findings; do not apply fixes. No verified findings means no counterexample found within the reported coverage, not proof of correctness.

For example requests, read [Examples](README.md) in full.

## Inputs

- Scope/diff/PR/design and intent; default scope is branch merge-base through working tree, including scoped dirty inputs.
- Pinned target/baseline, safe runnable target, repository facts, prior evidence and runtime/safety limits.
- `adversaries=1|2|3`, default `1`; independent of design candidate counts.
- `@outputPath`, `@outputBase` for a saved report and the Prove report folder; no save requested → inline. Missing requested destination → return findings inline and report the blocker.
- Supplied verified worktrees, ownership records and retention/cleanup needs when present.

## Frame

Read relevant repository architecture, ADRs/Concepts and glossary. Derive intent from the user, commits and PR description. *Load and follow the `principles` skill to load indexed engineering principles by name*. Select `In your own words`. Ask when intent is unclear. Pin committed refs and record dirty inputs; for CLI-only evidence scope the claim, command and observation instead of requiring a diff. Done when intent, scope/revision, safe target and limits are explicit.

Reject an adversary count outside the documented values before dispatch. Resolve relative report paths only against the supplied absolute base; an absent/ambiguous base blocks saving, not independent investigation.

## Hunt

Read [Adversary prompt](references/adversary-prompt.md) in full; fill every placeholder. *Load and follow the `subagents` skill to select the model and effort for an ordered model panel* with the `challenge-this reviewers` pool and the resolved adversary count. Spawn one read-only skill-capable `general-purpose` hunter per seat, together in the background, with the completed prompt; hunters read the pinned source checkout and run nothing. No seat available → report blocked coverage. Done when every hunter returned candidate claims or a named blocker.

## Prove

Merge candidates sharing one failure mechanism; keep adversary provenance and distinct affected behaviors. Drop candidates without falsifiable criteria or an intent they violate, with reasons. *Load and follow the `prove` skill to confirm or refute technical claims by executing tests, runnable prototypes, GUI E2E checks, or cloud experiments* once with every remaining candidate as a Claim (ID, Question, Criteria = the observable failure that violates intent, Route hint, Baseline when attribution matters), Facts = Frame facts, suites, prior reproductions and cited locations, Limits = runtime/safety limits, Checkout = supplied verified checkouts or none, Framing = finding title, root cause/location, violated intent, Destination = the run's Prove report folder, and Retention when a follow-up needs runnable state. Read every returned report in full. Done when every candidate has a Prove report or blocker.

## Verify

Keep a finding only when its Prove report observed a reproduced failure that violates intent against the scoped target. Source-only conclusions cannot confirm or refute a candidate. An unrelated failure, missing assertion, zero tests, inconclusive report or modified behavior cannot establish the claimed defect. Drop unsupported candidates with reasons; merge common root causes while retaining distinct supported findings and adversary provenance. Reuse reproductions only for unchanged scope/revision/dependencies/environment. Done when every candidate is verified, dropped or explicitly blocked.

## Output

- **Intent** — restatement and expected behavior.
- **Scope** — target/baseline, dirty inputs, environment, tested/excluded areas and blockers, including missing workers.
- **Findings** — each verified failure: title, root cause/location, exact command/working directory, expected/actual output, violated intent, Prove report and patch paths and adversaries. Say `no verified findings` when empty; report incomplete coverage separately.
- **Dropped** — each adversary's dropped candidates and reasons, before and after Prove.
- **Handoff** — retained evidence, resource/worktree ownership and cleanup outcome. Contract findings return to their caller for proposed Deep Module options; Wayfinder retains its Contract design Choice/selected-only integration gate; Challenge this supplies no interface redesign or fixes.

Prove owns proof worktrees and removes them unless Retention was requested; retained worktrees are handed back to the caller with Prove's ownership records. Preserve reports and patches outside worktrees. Done when every resource is removed or explicitly handed back.

## Completion criteria

- Every assignment/candidate is accounted for; an unavailable worker/runtime is incomplete coverage, not a clean review.
- Every retained finding has reproduced evidence violating intent; every dropped finding has a reason.
- Requested reports and reusable patches survive cleanup at the caller-selected destinations, or missing artifacts are reported.
