# Wayfinder operations

Shared mechanics for Design and Research. The calling Wayfinder owns document format, scope, ticket approval, payload eligibility and reconciliation. Read HLD below as the caller-selected living document; do not change its format.

## Operations

### Repository and errors

Resolve `{{trackerRepository}}` through *Load and follow the `git` skill to run verified Git mechanics* using Repository from the docs/harness root or current single repository. An issue URL must belong to this tracker; resolve conflicting targets before acting. Use the explicit repository in every command.

Missing workflow labels → ask the user to follow the [WF installer](https://github.com/antshc/brain/blob/main/plugins/wf/install/install.md) in labels-only mode. Missing tools, authentication, permissions, or failed writes → stop the dependent operation and report known remote changes; persist pending work where possible and continue independent questions. Do not claim a map/claim/resolution exists until confirmed; no Jira/local tracker fallback.

Use `--body-file <file>` with a temporary UTF-8 file for literal multiline bodies, evidence, and comments. Remove disposable transport files after use. Wayfinder Ticket approval review drafts are retained separately: keep pending/approved revisions through approval pauses, publication failures and reconciliation; clean only this run’s owned drafts after verified issue/link publication or explicit discard. Preserve unrelated files and pending proposals. Create from the recorded approved revision; resolve symbolic parent/blocker keys only to verified issue links, preserving all other approved content. Placeholder values are arguments, not shell expressions.

### Create ticket

*Load and follow the `github` skill to run GitHub platform mechanics for issues, tickets, and repositories* using Issues to create the supplied title, approved body and label. Record the verified issue number and URL. Reconcile an interrupted create before retrying.

### Create Wayfinder sub-ticket

List the parent's children first. Reuse an unambiguous match. For a prior partial create, reconcile unlinked issues by exact title and **Part of** map link. *Load and follow the `github` skill to run GitHub platform mechanics for issues, tickets, and repositories* using Issues to create or reuse, record the qualified ref, then link the native child and verify the edge. Retry only missing work.

### Read ticket

*Load and follow the `github` skill to run GitHub platform mechanics for issues, tickets, and repositories* using Issues to read the qualified ticket with comments and assignees. Fetch body-listed blockers to confirm closure. An inaccessible blocker keeps the ticket off the frontier.

### List sub-tickets

*Load and follow the `github` skill to run GitHub platform mechanics for issues, tickets, and repositories* using Issues to list native children. Recurse through open children to find the frontier. Use **Blocked by** in bodies for Wayfinder blocker decisions.

### Assign ticket

*Load and follow the `github` skill to run GitHub platform mechanics for issues, tickets, and repositories* using Issues to assign `@me` to an open unassigned ticket. Require confirmed sole ownership. A conflicting claim requires another ticket or ownership resolution.

### Unassign ticket

*Load and follow the `github` skill to run GitHub platform mechanics for issues, tickets, and repositories* using Issues to unassign `@me` and verify read-back. The open ticket returns to its recorded phase: a verified prototype awaits approval, Contract Options await HITL Choice; neither triggers an automatic rerun.

### Comment on ticket

*Load and follow the `github` skill to run GitHub platform mechanics for issues, tickets, and repositories* using Issues **Evidence** to post and verify the verbatim resolution comment. Confirm the comment URL before closing.

### Close ticket

*Load and follow the `github` skill to run GitHub platform mechanics for issues, tickets, and repositories* using Issues to close as completed with the verified factual answer or recorded human decision after document synchronization and detailed evidence are verified. Put out-of-scope closures in the map's **Out of scope**.

### Update map or ticket

Read the latest body through *Load and follow the `github` skill to run GitHub platform mechanics for issues, tickets, and repositories* using Issues. Preserve concurrent edits, decisions, fog and scope boundaries. Apply the intended section edit and verify the new body. Reconcile partial comment/close/map-update failures before retrying.

### Prepare a document worktree

**Reads:** captured harness root, repository, session base branch/SHA, summary and Wayfinder-selected prefix. Verify origin belongs to the tracker repository. *Load and follow the `git` skill to run verified Git mechanics for branch naming and creation* using Branches with the explicit prefix, summary and pinned base; inspect local/remote availability and reconcile a known resume before creation. *Load and follow the `git` skill to run verified worktree lifecycle* using Worktrees with that branch/SHA. Save ownership outside all disposable worktrees. Done when the dedicated document worktree and base/branch identity are verified.

### Prepare a result worktree

Read the persisted integration branch/worktree and pin its current local HEAD. Require prerequisite artifacts already integrated. Reuse the ticket's verified local branch/worktree on resume; otherwise use Prepare a document worktree with this integration SHA and Wayfinder's prefix. Persist branch, base SHA, ownership and question/revision/environment before dispatch. Producers receive exact paths and cleanup handoff; Wayfinder owns commits and integration. Done when the scoped worktree contains required evidence.

### Commit the document

1. Verify the integration worktree is on its recorded branch and read its latest local document. Preserve concurrent work; serialize writes. Stage only the HLD and artifacts already eligible for integration; pending approval-gated prototypes stay in their result worktrees; temporary proposal review drafts remain untracked. Document synchronization cannot bypass Prototype approval. *Load and follow the `git` skill to run verified Git mechanics for commit messages and history* using Commits. Done when the local commit contains only intended changes.
2. Verify document/artifact paths at HEAD and record synchronized result identity and HLD SHA through Update map or ticket. Keep tracker failures pending; do not repeat an already verified commit. Done when local synchronization and tracker state are separately confirmed. No push or PR.

### Integrate a result

Apply Wayfinder Prototype approval before any approval-gated prototype commit/merge. Require explicit approval of the exact payload inventory/content identity, including custom destinations; otherwise retain the owned worktree and return to Prototype approval. Research and Challenge this evidence integrate automatically without approval, including Challenge this test/probe patches; verify findings, retain evidence and restore production-source edits before integration. Contract design Options are review-only until explicit user Choice: retain candidate worktree/paths/revision, release claim and keep the ticket open. No Options commit/merge or HLD candidate inventory. After Choice use the Wayfinder Contract selection payload: selected sketch/rationale/module map and considered-option notes only. If candidate commits contain rejected source trees, prepare a clean selected-only result branch through the Git skill before this procedure; deletion commits do not exclude rejected sources from ancestry. A changed contract after integration drift returns to the user. Done when the exact chosen payload is eligible for integration.

For Research or Challenge this read-only inspection without an isolated worktree, Wayfinder serializes a verified artifact-only commit into the integration worktree; preserve caller-owned dirty files and require prerequisite SHA verification. Record result identity without inventing a merge. Approval-gated prototypes and Challenge this code changes or test execution use Prepare a result worktree. Artifact-only integration cannot bypass approval for gated prototypes; Challenge this remains automatic. Root-owned Challenge this records its run/result on the map, never creates a tracking child.

1. For approval-gated prototypes, verify current payload identity against recorded user approval before committing. Verify source citations and the selected Prove/Challenge this skill's independent reproduction. Review the entire branch diff from its pinned integration base. Retain reports, logs, proof patches and accepted code sketches at assigned destinations. Keep source probes as patches under the prototype directory and restore production-source edits; reject any unintended production code in the branch. *Load and follow the `git` skill to run verified Git mechanics for commit messages and creation* using Commits. Done when the scoped result commit and artifact inventory are verified.
2. In the dedicated integration worktree, *Load and follow the `git` skill to run verified Git mechanics for branch creation and history* using Integration. Supply exact result SHA, integration branch and expected integration HEAD. Serialize merges; verify full incoming diff and artifact paths before merging. Existing result ancestry skips a duplicate merge. Preserve conflicts as pending; never overwrite ambiguous edits. Reproduce affected claims again if resolution changes their tested mechanism; material changes to the approved payload return to Prototype approval before merge. Done when result ancestry and retained artifacts are verified at the local integration HEAD.
3. Return control to Wayfinder for Synchronize the document. Persist result/integrated/HLD SHAs and missing steps through Update map or ticket. Resolve factual tickets only after synchronized content and verified resolution comment; approval-gated prototype results additionally require recorded approval and verified integration; Contract design closes only after selected-only integration and recorded human Choice. Embedded Challenge this completion does not close its owner or clear unresolved fog. Done when local integration, document reconciliation and tracker writes are individually confirmed.
4. Awaiting approval retains the worktree without commit/merge or cleanup. Changed/rejected prototypes remain pending; missing state blocks recovery. Approved prototypes and automatic Challenge this evidence resume integration. Resume the first unconfirmed step: merged evidence needs reconciliation only; synchronized HLD needs pending tracker writes only. Preserve worktrees on conflict or missing local state; report precise blockers. Done when a rerun creates no duplicate merge, source or question.
5. After integration, synchronization and every reproduction/review consumer finishes, *Load and follow the `git` skill to run verified worktree lifecycle and removal* using Worktrees with ownership and expected HEAD. Keep branches by default; never remove the sole retained evidence. Done when each owned worktree is removed or retained with owner/reason.

### Wayfinder operation gotchas

Verify native parent/child links independently from body links. Wayfinder blocker decisions use body references; implementation Tickets use native blocker edges. Tracker writes may contain local branch/path/SHA identifiers, never fictional remote URLs. A failed read is not proof an issue or local ref is absent. No automatic push, PR creation or merge into the original session base. Legacy PRs remain untouched; Confluence publishing is a separate explicit Design route.
