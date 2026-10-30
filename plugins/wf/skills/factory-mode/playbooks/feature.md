### Feature

**You own the design. Sketch, spec, ship.** New or changed behavior goes from an accepted sketch to a spec to a reviewed draft PR.

Include **Design preferences** from Principles in every architecture design request, including each arena candidate's brief.

## Resolve open questions

For each question raised by the sketch, `architect`, or `interrogate`, preserve its original wording and resolve it before accepting the design:

- **How/why:** run the `research` skill against primary sources. Pass the original research request verbatim and a separate grounded question naming the repository/subsystem/symbol or external target, the unknown, and expected evidence. Apply cited findings to the sketch and rationale; do not silently change the research request.
- **Observable technical uncertainty:** run the `experiment` skill with one falsifiable question and a real CLI, test, or minimal throwaway app when reading cannot settle it. Apply observed results; use the `prototype` playbook only for comparing design alternatives, not for an already testable fact.
- **Product/preference:** apply the supported recommendation and log the rejected alternative.
- **Unanswerable with available access/evidence:** log `unanswerable` with its reason and proceed only on a safe reversible path.

Record evidence, conclusions, and changes to the sketch/rationale. Never treat a technical how/why question as a user preference.

## Workflow

**Goal: deliver the entire feature autonomously.** No open questions: every question gets an answer you recommend and then apply, with the reason and rejected alternative logged. Impossible to answer (needs access, data, or authority you lack) → log the question as `unanswerable` with the concrete reason why, then continue on the safest reversible path. Never ask the user after step 1 except for an explicitly requested checkpoint or required authority; a called skill's routine decision gets your evidence-backed recommendation. Decide calls the Principles cover by them; decide product, preference, and operator-only calls by the best recommendation from evidence. Never merge, force-push, or mark the PR ready.

Trail: *run `show-me-your-work` skill in Log mode to keep the decision trail* at `tmp/factory-mode-{{featureSlug}}/decisions.tsv` from step 1; log every fork, default, research finding, experiment result, review verdict, and fix with its evidence.

1. Ask once at the start, in one batch, for the inputs the request does not already give: Initiative ID, target branch, and repository (`owner/name`). Never invent them. Done when all three are set; later pauses only for an explicitly requested checkpoint or required authority.
2. Research the affected subsystem through Non-negotiables: how the flow works, what calls it, where config and tests live, and relevant architecture documentation and domain terminology. Done when every touched module has a file and line.
3. Arena. *Run `architect` skill with `arena-agents=3` for a design-only handoff* to synthesize competing multi-model candidates into one sketch. Request one overall `interrogate` and close questions through **Resolve open questions** before handoff; forward `checkpoint` only when the user explicitly asks for it, and resume after approval. Done when the synthesized sketch and rationale exist and every question has an answer or `unanswerable` reason.
4. *Run `to-spec` skill to synthesize the accepted sketch into a published spec issue* with the inputs from step 1. Done when the spec issue URL exists.
5. *Run `implement-spec` skill to implement the spec issue through a routed ticket graph in parallel mode into one draft PR.* Done when complete `ready` handoff exists; blocked/incomplete → report blockers, preserve work, skip post-implementation phases; proceed to Report.
6. Verify app. Run *Handoff and synchronization*, then *App verification*. Done when verdict or explicit skip and publication results are retained.
7. Review. Run *Code review* once. Done when every axis has an outcome for the pushed head and posting results are retained.
8. Address. *Run `address` skill to group the PR review comments into issues, investigate each against the code, fix what needs fixing, and reply to every thread.* Each issue gets a fix or a reply closing it with a concrete reason. Done when every thread carries a reply.
9. One remediation round only. Each finding left after Address gets a recommended resolution applied and logged; none stays open.
10. Run *Finalize*. Head changes require fresh verification/review per that section, without another Address cycle. Done when closure/cleanup state is read back or blockers and preserved paths reported.
11. Report last. *Run `show-me-your-work` skill in Report mode to audit the decision trail against the transcript, get a cross-model review, and print the report.* Done when the trail table and Attention section are printed.

**Reply:** the `show-me-your-work` report, then the accepted sketch, arena synthesis and what each candidate contributed, open questions and how each closed (interrogate, research, experiment, default), spec and draft PR URLs, app verdict/evidence or skip, final verified/reviewed heads, closure/cleanup status, review findings fixed vs closed with reason, deviations from the sketch, every recommendation applied with its rejected alternative, every `unanswerable` question with its reason. Tables for design alternatives.
