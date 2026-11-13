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
- Open or reuse a PR
- Link branches and PRs
- Publish the document
- Publish a result
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

*Load and follow the `github` skill to run GitHub platform mechanics for issues, tickets, and repositories* using Issues to unassign `@me` and verify read-back. The open ticket returns to the frontier.

### Comment on ticket

*Load and follow the `github` skill to run GitHub platform mechanics for issues, tickets, and repositories* using Issues **Evidence** to post and verify the verbatim resolution comment. Confirm the comment URL before closing.

### Close ticket

*Load and follow the `github` skill to run GitHub platform mechanics for issues, tickets, and repositories* using Issues to close as completed with the verified factual answer or recorded human decision after document synchronization and detailed evidence are verified. Put out-of-scope closures in the map's **Out of scope**.

### Update map or ticket

Read the latest body through *Load and follow the `github` skill to run GitHub platform mechanics for issues, tickets, and repositories* using Issues. Preserve concurrent edits, decisions, fog and scope boundaries. Apply the intended section edit and verify the new body. Reconcile partial comment/close/map-update failures before retrying.

### Prepare a document worktree

**Reads:** captured harness root, repository, session base branch/SHA, summary and Wayfinder-selected prefix. Verify origin belongs to the tracker repository. *Load and follow the `git` skill to run verified Git mechanics for branch naming and creation* using Branches with the explicit prefix, summary and pinned base; inspect local/remote availability and reconcile a known resume before creation. *Load and follow the `git` skill to run verified worktree lifecycle* using Worktrees with that branch/SHA. Save ownership outside all disposable worktrees. Done when the dedicated document worktree and base/branch identity are verified.

### Prepare a result worktree

**Reads:** captured harness root, repository, persisted session base branch, issue, question/revision/environment identity and prefix from Wayfinder. Reuse the ticket's existing verified branch/PR on resume; otherwise fetch and pin the session base tip, then use Prepare a document worktree's mechanics to create a separate ticket branch/worktree. Never base it on the document branch. Supply prerequisite evidence by exact commit/artifact refs; do not assume sibling PRs merged. Persist branch/base SHA/ownership on the ticket before dispatch. Wayfinder owns publication and cleanup. Done when the runner's scoped environment and evidence are accessible.

### Open or reuse a PR

*Load and follow the `github` skill to run GitHub platform mechanics for pull requests and issues* using Pull requests. Derive title/body using its conventions; supply exact repository, branch head and persisted session base. Search by head/base before creating; reconcile interrupted creation. A found merged/closed PR requires user-directed continuation, never automatic reopening/replacement. Open the document PR as draft; result PRs describe evidence and limitations. Verify URL, head, base and remote commit, then persist immediately. Done when one PR exists for this head/base and no duplicate was created.

### Link branches and PRs

*Load and follow the `github` skill to run GitHub platform mechanics for issues and pull requests* using Issues and Pull requests. Document branch/PR belongs to the map issue; research/experiment/contract result branch/PR belongs to its ticket. Put the canonical issue link in the PR body and branch/PR links in the issue, preserving native parent-child links and other edits. Use non-closing references, no automatic closing keywords. If the document PR precedes map creation, finish these links immediately after map creation. Done when both sides read back correctly.

### Publish the document

1. Verify the dedicated document worktree is on its recorded branch; read its latest remote head and preserve concurrent edits. Stage only the selected document and explicitly retained document artifacts. *Load and follow the `git` skill to run verified Git mechanics for commit messages and creation* using Commits. Review diff/outgoing commits for unrelated changes before committing. Done when the commit contains only intended document changes.
2. *Load and follow the `git` skill to run verified Git mechanics for branch fetch and push* using Branches with recorded previous remote SHA. Normal push only; on rejection fetch/reconcile the same document branch, preserving ambiguous conflicts as blockers. Never push or merge into the session base or merge result branches. Done when the document commit/artifact paths are verified on origin.
3. Open or reuse a PR immediately; Link branches and PRs when its map exists. Update the existing PR summary as decisions evolve. Record synchronized result identities on the map only after verification; keep failures pending. Done when the same PR shows the latest document, or the exact missing publication step is recorded.

### Publish a result

1. Commit only verified report/evidence paths in the result worktree. *Load and follow the `git` skill to run verified Git mechanics for commit messages and creation* using Commits; inspect staged diff and outgoing commits for unrelated files, proof code and resources. Include runnable prototype code only when explicitly retained. Preserve runnable state through reproduction and requested review. Done when evidence is committed with its target revision/environment.
2. *Load and follow the `git` skill to run verified Git mechanics for branch fetch and push* using Branches to push only this result branch with a verified previous remote SHA. Normal push only; preserve work on access/protection/conflict failure. For a rejected push fetch/reconcile this branch, not the session base. Verify publication commit/path on origin. Done when evidence has a durable commit-pinned URL.
3. Open or reuse a PR targeting the session base and Link branches and PRs to the owning ticket. Keep artifact links commit-pinned until merged. Return control to Wayfinder for **Synchronize the document**, then comment/resolve or release the ticket according to its evidence/human phase. Done when result publication and document synchronization are separately confirmed.
4. Resume interruptions at the first unconfirmed push/PR/document/comment/map step; inspect remote history and existing PRs/comments before retrying. Identical content reuses the published artifact. Conflicting edits preserve both versions and block synchronization rather than overwrite evidence. Done when no duplicate result or unrecorded pending work remains.
5. After verified publication/linking and all declared consumers finish, *Load and follow the `git` skill to run verified worktree lifecycle and removal* using Worktrees with ownership and expected HEAD. Preserve worktrees needed for synchronization or follow-up review; retain branches with open PRs. Delete branches only after separately authorized, verified integration/closure cleanup. Done when resources are removed or explicitly retained with an owner/reason.

### Wayfinder operation gotchas

Verify native parent/child links independently from body links. Wayfinder blocker decisions use body references. Implementation Tickets use native blocker edges. A ticket's resolution or empty frontier never authorizes PR merge/close or auto-merge; only the user decides. A failed read is not proof a branch/PR/issue is absent.
