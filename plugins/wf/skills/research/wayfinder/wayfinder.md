# Research Wayfinder

Chart a destination, gather evidence, and maintain one living research document. Research surfaces facts and tests claims; decisions and implementation belong to the caller. Refer to topics by linked title in user-facing text.

## Contents

- Shared procedures
- Session and document
- Small effort
- Chart and approve
- Frontier and dispatch
- Validate and integrate
- Synchronize and pause
- Resume and migration
- Completion

## Shared procedures

*Load and follow the `github` skill to run GitHub platform mechanics for issues, tickets, and repositories* using **Wayfinder operations**. Read its shared resource in full before tracker writes, worktree setup, commits or integration. Apply its Create ticket, Create Wayfinder sub-ticket, Read ticket, List sub-tickets, Assign/Unassign, Comment, Close and Update operations. Use its Prepare a document/result worktree, Commit the document and Integrate a result procedures with the research document in place of HLD. GitHub owns mechanics; this playbook owns scope, eligibility and synchronization.

*Load and follow the `design` skill to chart a Wayfinder map* only to read and reuse **Ticket approval** and **Prototype approval** from its Wayfinder playbook. Load the router and selected playbook in full. Do not start Design, seed an HLD, dispatch Design helpers or adopt architecture-decision work. Research uses the proposal review files, exact-revision approvals and retained-payload lifecycle from those procedures. Helpers return control here.

*Load and follow the `git` skill to run verified Git mechanics for branch naming, creation, commit and worktree lifecycle* using Branches, Worktrees, Commits and Integration as each operation needs them. Prefixes come from this playbook. Keep all shared mechanics with their existing owners; never copy commands into this route.

## Session and document

1. Capture original absolute harness root, repository, invocation checkout, session base branch/SHA and dirty state before interviews or worktree switches; leave the caller's working branch untouched. On resume use persisted identities. Keep interview state in session storage until ownership setup; create no branch, worktree, document seed or issue before the interview/small-effort decision.
2. Use [Questioning](questioning.md) for the destination interview: settle subject, constraints, exact versions and evidence outcome; the user confirms the destination. Then conduct a separate breadth-first frontier interview, one question at a time with an answer before the next. Facts use evidence routes, never user guesses. Preserve open downstream questions rather than resolving the whole investigation. Destination confirmation does not approve tickets.
3. Apply Small effort. For a mapped effort, resolve detached HEAD and prepare a dedicated owned document worktree from the captured session base on `wayfinder/<slug>`. Persist ownership and interview phase outside disposable worktrees. Done when the branch/worktree and original base are verified.
4. Seed `docs/ongoing/<slug>-research.md` using [Research document](research-document.template.md); create missing directories. Commit locally before approved topic evidence dispatch. This is synthesized research, not another map.

| Work | Branch | Output |
|---|---|---|
| Living research | `wayfinder/<slug>` | `docs/ongoing/<slug>-research.md` |
| Research topic | `research/<slug>` | `docs/research/<initiative-slug>/<topic-slug>.md` |
| Experiment/verification | `prove/<slug>` | `docs/prototype/<initiative-slug>/<experiment>/report.md` |

No automatic push, PR, merge into session base, production implementation or Confluence publication. Standalone evidence routes and Prove defaults remain unchanged.

## Small effort

After both interviews, if the route is clear, no coarse fog remains and the whole journey fits one session, stop before branch/worktree, document seed or issue creation. Present the bounded outcome and ask one continuation question: standalone evidence route/bounded research, or an explicitly tracked map. Wait for the choice; do not dispatch the offered handoff automatically. Many precise questions or substantial dependencies still warrant a map even with empty fog. Reuse existing deliverable authorization after the chosen continuation. Existing maps resume normally; retain their documents/worktrees.

## Chart and approve

1. Use the confirmed destination and separate breadth-first interview from Session and document. Persist precise questions/hypotheses, dependencies, coarse fog and exclusions. Later human scope/evidence-criteria choices stay in direct Questioning, with one answer before the next question; no grilling ticket type or Design interview.
2. Render the root and sub-issues using [Research map](research-map.template.md). The GitHub root with `wayfinder:map` is the authoritative workflow state. **Do not maintain another active Markdown research map.** Child issues track concrete work; the living document holds supported conclusions and evidence links.
3. Keep only in-scope concerns too vague to ticket in root **Not yet specified**. A precise question belongs in a research/experiment ticket even when blocked, partial or conflicting. Transfer stable IDs, provenance, consequence, criteria, risk/mitigation evidence and next action to its owner; remove graduated fog only after the approved issue/links are verified or its exact draft and pending-proposal state are durable. Keep genuinely coarse remainder with predecessor links. Pending approval is not fog; preserve uncreated precise proposals in retained drafts and Pending proposals, human choices in interview state, and exclusions in Out of scope.
4. Follow shared Ticket approval: save temporary clickable Markdown drafts for root and each exact child proposal, including parent, blockers, labels, full body and stable proposal revision. Present one linked bullet per proposal, map first. Require explicit approval of each exact proposal before creation or evidence dispatch for it. Destination approval, previous approval, silence and passing checks are not ticket approval. Changed proposals require fresh review; unchanged approved issues may resume.
5. Create only approved issues with `wayfinder:map`, `wayfinder:research`, or `wayfinder:experiment`. Record verified issue refs immediately; verify native parent/sub-issue edges. Resolve symbolic blockers in a second pass. Follow shared body-based Wayfinder blocked-by operations; reject cycles, missing parents and unknown blockers. Persist approved revision/content identity and pending publication steps. Use the WF installer labels-only repair procedure if labels are absent.

## Frontier and dispatch

1. Read the latest root and recursively list native children. Select open, approved, unclaimed work whose blockers are closed **and prerequisite evidence is integrated**. Inaccessible blockers remain blocked. Confirm sole claim ownership; a pending approval is not permission to rerun.
2. Create every result worktree from a pinned current integration HEAD through Prepare a result worktree. Independent topics may share that pinned HEAD; dependent topics wait for integration. Persist topic/question, source revision, environment, branch/worktree, ownership and exact output paths before dispatch.
3. Research uses the router's **Frame, Routing and Spawning agents** pipeline. Select Explore, How, Why, Cloud or Web per question, loading its playbook and triggered resources fully. Never recursively invoke Research or select Wayfinder for a topic; add no dedicated agent. Pass destination/Notes, question, scope, target/ref/version/lens, original harness root, pinned source checkout and absolute report destination under the result worktree. Workers are read-only and return cited evidence; only the Research router writes reports. Save Explore verdicts unabridged to the topic path as a Wayfinder-only exception. Explicit caller destinations override defaults; preserve their ownership and isolate writes in the assigned result worktree, resolving ambiguous external destinations before dispatch.
4. For experiments, *Load and follow the `prove` skill to confirm or refute one technical claim with reproducible evidence*. Supply `@question`, `@criteria`, `@repoFacts`, limits, supplied owned checkout, exact absolute `@outputPath` and `@outputBase`, with retention through reproduction and human review. Read its returned report in full. Prove uses its own default dispatch; never wrap a helper in another worker. Keep runnable state, patches and report in the result worktree; Wayfinder owns commit/integration/cleanup.
5. Batch independent research when safe; sequence dependent topics and each route's worker stages. Serialize integration and document writes. Approved ready factual work runs automatically without another dispatch question. While new proposals or proof approval await the user, continue only already-approved independent work.

## Validate and integrate

1. Read the complete report and incoming diff. Check citations, source revision/provenance, question/criteria, environment, report identity, supported outcome and limits. Partial, blocked, conflicting, rejected or inconclusive results remain open; their dependents remain blocked. Do not repeat an unchanged inconclusive run without new evidence, prerequisites or method.
2. Verified research report-only payloads integrate automatically using shared Integrate a result. Restore unrelated production-source edits before constructing the payload; never ship worktree source changes as fixes. Commit only eligible artifacts. Record result SHA and artifact inventory.
3. Prove follows shared Prototype approval: present the exact payload, observation and limits for explicit user approval before any payload commit/merge. Retain runnable reproduction state and patches; keep pending observations out of confirmed integrated conclusions. Record approval against the actual payload content identity. Passing tests, ticket approval, silence or a recommendation does not approve the proof payload. Changes/rejection retain the worktree and next action; revised payloads require fresh approval.
4. Recheck current integration HEAD, drift, ancestry, allowed paths and proof approval identity. Merge only eligible results locally through Git Integration; existing result ancestry skips duplicate merges. Conflicts remain pending with worktrees retained. Reproduce claims if conflict resolution changes their mechanism; material proof payload changes require renewed approval.
5. Apply [Living document](living-document.md), then synchronize tracker results/fog. Close a child only after deciding evidence, verified integration, document reconciliation and verified resolution comment; proof additionally needs its recorded approval. Claim release preserves the pending phase.

## Synchronize and pause

Before mapped setup, persist interview state only. After setup, on each integrated result, session pause, human choice, approval and resume, reconcile the living document and root/child state. Persist result/source identity, pinned base, payload/approval identity, result/integrated/document SHAs, last reconciled evidence/HEAD and exact pending step outside disposable worktrees and on the owning issue where available. Read before writes and preserve concurrent contributions.

A tracker failure leaves local progress valid but synchronization pending. Retry the first unconfirmed operation after read-back; do not duplicate issues, comments, commits or merges. Report known remote changes and blocked writes. Local identifiers are not published artifact URLs.

Clean an owned worktree only after verified integration, document synchronization and all required reproduction/review consumers finish. Retain blocked, rejected or approval-pending worktrees and sole evidence copies. Use ownership and expected HEAD for cleanup; never remove unrelated resources.

## Resume and migration

1. Resume from the root issue number/URL and persisted branch/worktree/HEAD identities, without restarting the destination interview. Verify repository, refs, ownership, ancestry, report files, approvals/content identities and last sync. Missing refs or local evidence are blockers; never invent remote artifact links or silently replace worktrees.
2. Recover pending approved proof integration before new dependent work. An already merged result needs reconciliation only; a synchronized document needs remaining tracker writes only. Never regenerate an unchanged approval candidate.
3. A legacy `docs/ongoing/<slug>-research-map.md` is migration input only. Verify its identity, destination and evidence links; preserve files/history. Propose the GitHub root and children through Ticket approval, then explicitly record the root as authoritative and legacy map as inactive. Do not run two active maps or infer approval from old destination confirmation. Missing or unreadable map state blocks recovery.
4. On legacy resume, reconcile fog rows with existing owners first: transfer precise questions/risks and IDs, criteria, evidence/history to verified tickets or durable pending proposals before removing duplicate rows; retain coarse remainder only. Missing/ambiguous owners block affected migration, never lose evidence or recreate tickets. Reconcile fog and child results; reuse sufficient matching evidence and existing unchanged approved work. Preserve stable IDs, blockers, status and links. Resume approved ready work; present only required human decisions or exact blockers.

## Completion

Finish only when the destination has sufficient supported evidence or the user confirms remaining gaps cannot change its answer. Every unresolved claim stays explicit; check open tickets, pending proposals, human choices, coarse fog and synchronization, since empty fog alone is not completion; paused or incomplete work is resumable, never a fabricated answer.

A selected small-effort continuation returns its bounded outcome and chosen route without fabricating map/document refs. For mapped efforts return root GitHub issue, clickable document path, local integration branch/HEAD, integrated topic/proof links, open unknowns/risks, pending approvals and blockers. Conclusions belong to the living document; detailed reports remain independently readable and linked. The caller owns decisions and implementation.
