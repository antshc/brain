# GitHub operations

## Contents

- Spec publication
- Repository and labels
- Publish spec
- Attach design artifacts
- Offline spec publishing
- Spec publication gotchas
- Ticket operations
- Read spec
- Read design sketch
- Ticket labels
- Reconcile reruns
- Create sub-ticket
- Link blocking
- Offline ticket publishing
- Ticket operation gotchas
- Wayfinder operations
- Repository and errors
- Create ticket
- Create Wayfinder sub-ticket
- Read ticket
- List sub-tickets
- Assign ticket
- Unassign ticket
- Comment on ticket
- Close ticket
- Update map or ticket
- Prepare a document worktree
- Prepare a result worktree
- Commit the document
- Integrate a result
- Wayfinder operation gotchas

## Spec publication

### Repository and labels

Resolve `{{trackerRepository}}` through *Load and follow the `git` skill to run verified Git mechanics* using Repository from the docs/harness root (or current repository for single-repo work). Keep it distinct from `{{repository}}`, the source repository selected by the skill. Use the tracker explicitly for every issue and label operation.

Missing baseline `spec` label → ask the user to follow the [WF installer](https://github.com/antshc/brain/blob/main/plugins/wf/install/install.md) in labels-only mode in the tracker repository, then retry.

### Publish spec

*Load and follow the `github` skill to run GitHub platform mechanics for specs, tickets, and issues* using Specs and tickets, Design profile. Supply the tracker, source repository, target branch, initiative, title and approved verbatim body. Stop and report the URL on a duplicate. Return the verified issue number and URL. Tickets later become native sub-issues of this spec.

### Attach design artifacts

*Load and follow the `github` skill to run GitHub platform mechanics for issues, specs, and tickets* using Issue artifacts with the verified issue created by this run and the bundle manifest. Attach or update each artifact by exact name. Fill the **Design sketch** decision's `{{artifactUrl}}` placeholders with the verified URLs. Use the Issues edit-body operation and read back the exact final body. After verification, remove this run's temporary files and bundle.

Partial failure → report the published issue URL, attached and missing names, and retained bundle. Resume from the first unconfirmed artifact or body update.

### Offline spec publishing

On explicit offline selection, skip GitHub operations. On missing tools, authentication, or API failure, report the failed operation and any known remote changes before saving locally. Save the rendered spec to `docs/specs/{{initiativeIdSlug}}.md`, retaining Initiative, source repository, base branch, and intended title in local metadata. Preserve an existing differing file rather than overwriting it without approval.

If creation may have reached GitHub before failing, reconcile with **Publish spec**'s lookup before retrying. If reconciliation is unavailable, mark the local copy's publication state unknown; never report it as unpublished with certainty or create another remote issue blindly. Return the local path and explicit offline/unknown status, not a GitHub success.

Architect run offline → copy each manifest file to `docs/specs/{{initiativeIdSlug}}/artifacts/` under its manifest file name, write the manifest there, and replace each `{{artifactUrl}}` with the relative artifact path. Attach them with **Attach design artifacts** once the spec is published.

### Spec publication gotchas

Use argument values, not shell interpolation, for user text. Quote values containing whitespace; multiline bodies use `--body-file`. A duplicate spec is a stop condition, not an outage triggering fallback. Do not substitute Jira or a local tracker backend. Artifact names come from the manifest verbatim; gh strips some characters, so match names after read-back, not before. Attach artifacts only to the issue this run created, never to a duplicate found by the lookup.

## Ticket operations

Use `{{trackerRepository}}` resolved by the skill for all commands. It holds the spec and its tickets; `repo:target:<owner>/<name>` identifies the source repository, not the tracker. Stop and report read/write failures; do not infer absent issues or edges from a failed lookup.

### Read spec

*Load and follow the `github` skill to run GitHub platform mechanics for issues, tickets, and repositories* using Issues to read the qualified spec with comments. Require the `spec` label and exactly one `repo:target:` label before publication.

### Read design sketch

Only online and with a **Design sketch** decision, *Load and follow the `github` skill to run GitHub platform mechanics for issues, specs, and tickets* using Issue artifacts to read the complete collection. Read **Sketch index** and every artifact it lists, including `module-map.md` when listed. Unavailable artifacts, missing index, or unreadable entries → report the exact gap and ask the user.

### Ticket labels

*Load and follow the `github` skill to run GitHub platform mechanics for issues, tickets, and repositories* using Issues to verify baseline `hitl`, `spec`, and `bug`. If missing, use the WF installer in labels-only mode. Ensure the spec's routing label with color `0e8a16` and description `Source repository for this spec's tickets`.

### Reconcile reruns

*Load and follow the `github` skill to run GitHub platform mechanics for issues, tickets, and repositories* using Issues to read all native children, including closed ones. Map approved slices to exact existing titles, bodies and routing labels. After interrupted creation, also inspect unlinked issues with the routing label and matching title/parent-spec content. Reuse only an unambiguous match. Retain the created issue even if linking failed.

### Create sub-ticket

Follow **Ticket labels**. *Load and follow the `github` skill to run GitHub platform mechanics for issues, tickets, and repositories* using Issues to create the approved title, verbatim body and labels. Record its qualified ref and URL immediately. Link to the qualified parent, verify the native edge and check the read-back body and labels. On failure report the created issue and unfinished link.

### Link blocking

*Load and follow the `github` skill to run GitHub platform mechanics for issues, tickets, and repositories* using Issues to read and link native blockers with qualified refs. Reread the dependency list to confirm each edge. Keep the parent spec open and preserve its body.

### Offline ticket publishing

Explicit offline mode → use supplied local spec content and routing metadata; skip GitHub reads/writes. A missing spec or metadata requires user input, not invented content. An online failure → report the failed operation and preserve any known issue numbers/URLs and completed/pending links.

Save approved issue bodies under `docs/tickets/`, with distinct stable slice filenames. Include intended titles, labels, parent spec, symbolic blocker graph adjacency (including roots), and initial ready frontier in local metadata. Never invent GitHub issue numbers for unpublished slices. Preserve differing existing files unless replacement is approved.

Report local paths and unpublished/partially published status, not GitHub success. If a create response was lost, mark publication unknown and reconcile before retrying. Offline output does not satisfy the online native-link completion condition.

### Ticket operation gotchas

Use native sub-issue and dependency edges for Tickets. GitHub issue bodies and Jira links do not satisfy this contract.

## Wayfinder operations

### Repository and errors

Resolve `{{trackerRepository}}` through *Load and follow the `git` skill to run verified Git mechanics* using Repository from the docs/harness root or current single repository. An issue URL must belong to this tracker; resolve conflicting targets before acting. Use the explicit repository in every command.

Missing workflow labels → ask the user to follow the [WF installer](https://github.com/antshc/brain/blob/main/plugins/wf/install/install.md) in labels-only mode. Missing tools, authentication, permissions, or failed writes → stop the dependent operation and report known remote changes; persist pending work where possible and continue independent questions. Do not claim a map/claim/resolution exists until confirmed; no Jira/local tracker fallback.

Use `--body-file <file>` with a temporary UTF-8 file for literal multiline bodies, evidence, and comments. Remove temporary files after use. Placeholder values are arguments, not shell expressions.

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

*Load and follow the `github` skill to run GitHub platform mechanics for issues, tickets, and repositories* using Issues to unassign `@me` and verify read-back. The open ticket returns to its next phase: Contract design with prepared options is HITL Choice, never an automatic Options rerun.

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

1. Verify the integration worktree is on its recorded branch and read its latest local document. Preserve concurrent work; serialize writes. Stage only the HLD and explicitly retained artifacts. *Load and follow the `git` skill to run verified Git mechanics for commit messages and history* using Commits. Done when the local commit contains only intended changes.
2. Verify document/artifact paths at HEAD and record synchronized result identity and HLD SHA through Update map or ticket. Keep tracker failures pending; do not repeat an already verified commit. Done when local synchronization and tracker state are separately confirmed. No push or PR.

### Integrate a result

Contract design Options are review-only until explicit user Choice: retain candidate worktree/paths/revision, release claim and keep the ticket open. No Options commit/merge or HLD candidate inventory. After Choice use the Wayfinder Contract selection payload: selected sketch/rationale/module map and considered-option notes only. If candidate commits contain rejected source trees, prepare a clean selected-only result branch through the Git skill before this procedure; deletion commits do not exclude rejected sources from ancestry. A changed contract after integration drift returns to the user. Done when the exact chosen payload is eligible for integration.

For read-only helpers without an isolated worktree, Wayfinder serializes a verified artifact-only commit into the integration worktree; preserve caller-owned dirty files and require prerequisite SHA verification. Record result identity without inventing a merge. Mutation/source sketch isolation uses Prepare a result worktree. Root-owned Challenge this records its run/result on the map, never creates a tracking child.

1. Verify source citations and the selected Prove/Challenge this skill's independent reproduction. Review the entire branch diff from its pinned integration base. Retain reports, logs, proof patches and accepted code sketches at assigned destinations. Keep source probes as patches under the prototype directory and restore production-source edits; reject any unintended production code in the branch. *Load and follow the `git` skill to run verified Git mechanics for commit messages and creation* using Commits. Done when the scoped result commit and artifact inventory are verified.
2. In the dedicated integration worktree, *Load and follow the `git` skill to run verified Git mechanics for branch creation and history* using Integration. Supply exact result SHA, integration branch and expected integration HEAD. Serialize merges; verify full incoming diff and artifact paths before merging. Existing result ancestry skips a duplicate merge. Preserve conflicts as pending; never overwrite ambiguous edits. Reproduce affected claims again if resolution changes their tested mechanism. Done when result ancestry and retained artifacts are verified at the local integration HEAD.
3. Return control to Wayfinder for Synchronize the document. Persist result/integrated/HLD SHAs and missing steps through Update map or ticket. Resolve factual tickets only after synchronized content and verified resolution comment; Contract design closes only after selected-only integration and recorded human Choice. Embedded Challenge this completion does not close its owner or clear unresolved fog. Done when local integration, document reconciliation and tracker writes are individually confirmed.
4. Resume the first unconfirmed step: merged evidence needs reconciliation only; synchronized HLD needs pending tracker writes only. Preserve worktrees on conflict or missing local state; report precise blockers. Done when a rerun creates no duplicate merge, source or question.
5. After integration, synchronization and every reproduction/review consumer finishes, *Load and follow the `git` skill to run verified worktree lifecycle and removal* using Worktrees with ownership and expected HEAD. Keep branches by default; never remove the sole retained evidence. Done when each owned worktree is removed or retained with owner/reason.

### Wayfinder operation gotchas

Verify native parent/child links independently from body links. Wayfinder blocker decisions use body references; implementation Tickets use native blocker edges. Tracker writes may contain local branch/path/SHA identifiers, never fictional remote URLs. A failed read is not proof an issue or local ref is absent. No automatic push, PR creation or merge into the original session base. Legacy PRs remain untouched; Confluence publishing is a separate explicit Design route.
