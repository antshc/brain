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

*Load and follow the `github` skill to run GitHub platform mechanics for issues, tickets, and repositories* using **Wayfinder operations**. Read that shared resource in full for tracker operations, document/result worktrees, commits and integration. Design owns Ticket approval, Prototype approval, Contract selection and HLD synchronization; the shared mechanics preserve these gates.
