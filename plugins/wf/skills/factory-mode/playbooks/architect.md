### Architect

**You own the design. Sketch, spec, ship.** New or changed behavior goes from an accepted sketch to a spec to a reviewed draft PR.

Select mode from the request:

| Mode | Trigger |
|---|---|
| **Interactive** | default |
| **Auto** | auto, autonomous, run until done, don't stop, going to bed |

## Interactive

1. Learn the affected subsystem. *Run `explore-codebase` skill in a subagent to find how the flow works, what calls it, and where config and tests live.* Read `ARCHITECTURE.md` and `GLOSSARY.md` rows that match. Done when every touched module has a file and line.
2. *Run `architect` skill to sketch types, signatures, and module structure before code, loop corrections into the sketch, and resolve open design questions.* Name the data shape and its organizing structure (**Model the domain**, **Foundational thinking**). Multiple valid shapes → competing candidates (**Exhaust the design space**). Done when the user accepts the sketch.
3. *Run `to-spec` skill to turn the conversation and accepted sketch into a spec issue* with the target branch and Initiative ID. Done when the spec issue URL exists.
4. *Run `implement-spec` skill to implement the spec through a routed ticket graph into one draft PR.* Done when complete `ready` handoff exists; blocked/incomplete → report blockers, preserve work, stop post-implementation phases.
5. Run *Handoff and synchronization*, then *App verification*. Done when verdict or explicit skip and publication results are retained.
6. Run *Code review*. Done when every axis has an outcome for the pushed head; retain blockers/findings.
7. Review the draft PR against the accepted sketch; surface every deviation and open decision. Done when each is reported.
8. Run *Finalize*, then report *Output*. Done when closure/cleanup states are read back or blockers and preserved paths reported.

## Auto

**Goal: deliver the entire feature autonomously.** No open questions: every question gets an answer you recommend and then apply, with the reason and rejected alternative logged. Impossible to answer (needs access, data, or authority you lack) → log the question as `unanswerable` with the concrete reason why, then continue on the safest reversible path. Never ask the user after step 1; a called skill that asks (e.g. `to-spec` base candidate, `architect` review reply) gets your recommended answer. Decide calls the Principles cover by them; decide product, preference, and operator-only calls by the best recommendation from evidence. Never merge, force-push, or mark the PR ready.

Trail: *run `show-me-your-work` skill in Log mode to keep the decision trail* at `tmp/factory-mode-{{featureSlug}}/decisions.tsv` from step 1; log every fork, default, prototype result, review verdict, and fix with its evidence.

1. Ask once at the start, in one batch, for the inputs the request does not already give: Initiative ID, target branch, and repository (`owner/name`). Never invent them. Done when all three are set; no further questions after this step.
2. Learn the affected subsystem with `explore-codebase` as in Interactive step 1.
3. Arena. *Run `architect` skill with `arena-agents=3` to synthesize competing multi-model design candidates into one sketch.* Done when the synthesized sketch and rationale exist.
4. Close open questions. Act as the reviewer in the `architect` Review loop; reply for the user:
   - `interrogate` once on the synthesized sketch; apply findings backed by evidence.
   - `prototype` per remaining open question that an observation can settle; apply the corrections the evidence supports, citing it in the rationale.
   - Every other question (product, preference, no experiment settles it) → answer with your recommendation, record it and the rejected alternative in the rationale.
   - Reply `accept`. Done when every rationale question carries a recommended answer or an `unanswerable` reason; none is open.
5. *Run `to-spec` skill to synthesize the accepted sketch into a published spec issue* with the inputs from step 1. Done when the spec issue URL exists.
6. *Run `implement-spec` skill to implement the spec issue through a routed ticket graph in sequential mode into one draft PR.* Done when complete `ready` handoff exists; blocked/incomplete → report blockers, preserve work, skip post-implementation phases; proceed to Report.
7. Verify app. Run *Handoff and synchronization*, then *App verification*. Done when verdict or explicit skip and publication results are retained.
8. Review. Run *Code review* once. Done when every axis has an outcome for the pushed head and posting results are retained.
9. Address. *Run `address` skill to group the PR review comments into issues, investigate each against the code, fix what needs fixing, and reply to every thread.* Each issue gets a fix or a reply closing it with a concrete reason. Done when every thread carries a reply.
10. Diagnose. Each bug discovered in verification, review, or Address that is not trivially fixed, or any code-caused failing build, test, or verification (environment failures retain App verification skip policy) → spawn one fresh subagent per bug on the PR branch: *run `diagnosing-bugs` skill to confirm the root cause, write a regression test at the correct seam, apply the fix, and verify.* Review each diff (Subagents), push, and reply on the related thread with root cause and fix. Done when each bug is fixed with a regression test; a bug that cannot be fixed gets a recommended resolution (follow-up ticket, revert, or accepted risk) applied and logged.
11. One remediation round only. Each finding left after Diagnose gets a recommended resolution applied and logged; none stays open.
12. Run *Finalize*. Head changes require fresh verification/review per that section, without another Address/Diagnose cycle. Done when closure/cleanup state is read back or blockers and preserved paths reported.
13. Report last. *Run `show-me-your-work` skill in Report mode to audit the decision trail against the transcript, get a cross-model review, and print the report.* Done when the trail table and Attention section are printed.

**Reply:** the `show-me-your-work` report, then the accepted sketch, arena synthesis and what each candidate contributed, open questions and how each closed (interrogate, prototype, default), spec and draft PR URLs, app verdict/evidence or skip, final verified/reviewed heads, closure/cleanup status, review findings fixed vs closed with reason, bugs diagnosed with root cause, deviations from the sketch, every recommendation applied with its rejected alternative, every `unanswerable` question with its reason. Tables for design alternatives.
