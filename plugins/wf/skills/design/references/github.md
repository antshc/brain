# GitHub operations

- [Spec publication](#spec-publication)
- [Ticket operations](#ticket-operations)
- [Wayfinder operations](#wayfinder-operations)

## Spec publication

### Repository and labels

Resolve `{{trackerRepository}}` through *the `git` skill for verified Git mechanics* using Repository from the docs/harness root (or current repository for single-repo work). Keep it distinct from `{{repository}}`, the source repository selected by the skill. Use the tracker explicitly for every issue and label operation.

Missing baseline `spec` label → ask the user to follow the [WF installer](https://github.com/antshc/brain/blob/main/plugins/wf/install/install.md) in labels-only mode in the tracker repository, then retry.

### Publish spec

*Use `github` skill for platform specs, tickets, and issues* using Specs and tickets, Design profile. Supply the tracker, source repository, target branch, initiative, title and approved verbatim body. Stop and report the URL on a duplicate. Return the verified issue number and URL. Tickets later become native sub-issues of this spec.

### Attach design artifacts

Use *the `github` skill for platform issues, specs, and tickets* using Issue artifacts with the verified issue created by this run and the bundle manifest. Attach or update each artifact by exact name. Fill the **Design sketch** decision's `{{artifactUrl}}` placeholders with the verified URLs. Use the Issues edit-body operation and read back the exact final body. After verification, remove this run's temporary files and bundle.

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

*Use `github` skill for platform issues, tickets, and repositories* using Issues to read the qualified spec with comments. Require the `spec` label and exactly one `repo:target:` label before publication.

### Read design sketch

Only online and with a **Design sketch** decision, use *the `github` skill for platform issues, specs, and tickets* using Issue artifacts to read the complete collection. Read **Sketch index** and every artifact it lists, including `module-map.md` when listed. Unavailable artifacts, missing index, or unreadable entries → report the exact gap and ask the user.

### Ticket labels

*Use `github` skill for platform issues, tickets, and repositories* using Issues to verify baseline `hitl`, `spec`, and `bug`. If missing, use the WF installer in labels-only mode. Ensure the spec's routing label with color `0e8a16` and description `Source repository for this spec's tickets`.

### Reconcile reruns

*Use `github` skill for platform issues, tickets, and repositories* using Issues to read all native children, including closed ones. Map approved slices to exact existing titles, bodies and routing labels. After interrupted creation, also inspect unlinked issues with the routing label and matching title/parent-spec content. Reuse only an unambiguous match. Retain the created issue even if linking failed.

### Create sub-ticket

Follow **Ticket labels**. *Use `github` skill for platform issues, tickets, and repositories* using Issues to create the approved title, verbatim body and labels. Record its qualified ref and URL immediately. Link to the qualified parent, verify the native edge and check the read-back body and labels. On failure report the created issue and unfinished link.

### Link blocking

*Use `github` skill for platform issues, tickets, and repositories* using Issues to read and link native blockers with qualified refs. Reread the dependency list to confirm each edge. Keep the parent spec open and preserve its body.

### Offline ticket publishing

Explicit offline mode → use supplied local spec content and routing metadata; skip GitHub reads/writes. A missing spec or metadata requires user input, not invented content. An online failure → report the failed operation and preserve any known issue numbers/URLs and completed/pending links.

Save approved issue bodies under `docs/tickets/`, with distinct stable slice filenames. Include intended titles, labels, parent spec, symbolic blocker graph adjacency (including roots), and initial ready frontier in local metadata. Never invent GitHub issue numbers for unpublished slices. Preserve differing existing files unless replacement is approved.

Report local paths and unpublished/partially published status, not GitHub success. If a create response was lost, mark publication unknown and reconcile before retrying. Offline output does not satisfy the online native-link completion condition.

### Ticket operation gotchas

Use native sub-issue and dependency edges for Tickets. GitHub issue bodies and Jira links do not satisfy this contract.

## Wayfinder operations

### Repository and errors

Resolve `{{trackerRepository}}` through *the `git` skill for verified Git mechanics* using Repository from the docs/harness root or current single repository. An issue URL must belong to this tracker; resolve conflicting targets before acting. Use the explicit repository in every command.

Missing workflow labels → ask the user to follow the [WF installer](https://github.com/antshc/brain/blob/main/plugins/wf/install/install.md) in labels-only mode. Missing tools, authentication, permissions, or failed writes → stop and report the operation and known remote changes. Do not claim a map/claim/resolution exists until confirmed; no Jira/local tracker fallback.

Use `--body-file <file>` with a temporary UTF-8 file for literal multiline bodies, evidence, and comments. Remove temporary files after use. Placeholder values are arguments, not shell expressions.

### Create ticket

*Use `github` skill for platform issues, tickets, and repositories* using Issues to create the supplied title, approved body and label. Record the verified issue number and URL. Reconcile an interrupted create before retrying.

### Create Wayfinder sub-ticket

List the parent's children first. Reuse an unambiguous match. For a prior partial create, reconcile unlinked issues by exact title and **Part of** map link. *Use `github` skill for platform issues, tickets, and repositories* using Issues to create or reuse, record the qualified ref, then link the native child and verify the edge. Retry only missing work.

### Read ticket

*Use `github` skill for platform issues, tickets, and repositories* using Issues to read the qualified ticket with comments and assignees. Fetch body-listed blockers to confirm closure. An inaccessible blocker keeps the ticket off the frontier.

### List sub-tickets

*Use `github` skill for platform issues, tickets, and repositories* using Issues to list native children. Recurse through open children to find the frontier. Use **Blocked by** in bodies for Wayfinder blocker decisions.

### Assign ticket

*Use `github` skill for platform issues, tickets, and repositories* using Issues to assign `@me` to an open unassigned ticket. Require confirmed sole ownership. A conflicting claim requires another ticket or ownership resolution.

### Unassign ticket

*Use `github` skill for platform issues, tickets, and repositories* using Issues to unassign `@me` and verify read-back. The open ticket returns to the frontier.

### Comment on ticket

*Use `github` skill for platform issues, tickets, and repositories* using Issues **Evidence** to post and verify the verbatim resolution comment. Confirm the comment URL before closing.

### Close ticket

*Use `github` skill for platform issues, tickets, and repositories* using Issues to close as completed with the approved summary after detailed evidence is verified. Put out-of-scope closures in the map's **Out of scope**.

### Update map or ticket

Read the latest body through *`github` skill for platform issues, tickets, and repositories* using Issues. Preserve concurrent edits, decisions, fog and scope boundaries. Apply the intended section edit and verify the new body. Reconcile partial comment/close/map-update failures before retrying.

### Prepare a result worktree

**Reads:** captured harness root, invocation worktree, branch, repository, and issue number. Verify `origin` points to the tracker repository. Pin the invocation branch tip. *Run `git` skill for worktree lifecycle and creation using Worktrees* from that SHA with a temporary branch and leaf named for the ticket and a unique run suffix. Save the ownership record outside all worktrees and pass the returned path to the runner. Wayfinder owns integration and cleanup.

### Publish a result

**Reads:** result worktree, verified artifact paths, issue number, and captured invocation branch/worktree.

1. Commit only verified artifact paths in the result worktree. Check the staged diff for unrelated files and temporary resources.
2. Serialize merges into the captured branch. Verify the original worktree is still on that branch and clean. If it has changed branches or has local changes, preserve the result and report the blocker. Fetch `origin` and compare the captured branch with its remote counterpart before merging. If pushing would publish unrelated local commits, stop and preserve the result unless the user authorized publishing them. Integrate any remote changes, then merge the result. Review the outgoing commits and diff before pushing.
3. Resolve safe artifact conflicts automatically. Reuse identical content. For independently added artifacts that collide, give the incoming artifact a ticket-number suffix and update links in the incoming artifacts. If both sides edited the same findings or the safe resolution is unclear, abort the in-progress merge, preserve the result branch and worktree, and report the conflict.
4. Push the captured branch to the same branch name on `origin` with a normal push. Use no pull requests or force pushes. If rejected because the remote advanced, fetch and integrate the new remote head, check for conflicts again, and retry. If access or branch protection blocks publication, preserve the work and report the blocker.
5. Fetch the remote branch and verify the publication commit is reachable and the artifact paths are present. Use commit-pinned links in the ticket. If the push or ticket write was interrupted, inspect remote history and existing comments before retrying. Resume at the first unconfirmed step. After successful publication and ticket linking, *run `git` skill for verified worktree lifecycle and removal using Worktrees* with the saved ownership record and verified result HEAD. After verified removal, delete the temporary branch only if its tip still matches the result integrated on the published branch. Preserve and report blocked cleanup.

### Wayfinder operation gotchas

Verify native parent/child links independently from body links. Wayfinder blocker decisions use body references. Implementation Tickets use native blocker edges.
