# GitHub operations

- [Spec publication](#spec-publication)
- [Ticket operations](#ticket-operations)
- [Wayfinder operations](#wayfinder-operations)

## Spec publication

### Repository and labels

Resolve `{{trackerRepository}}` with `gh repo view --json nameWithOwner --jq .nameWithOwner` from the docs/harness root (or current repository for single-repo work). Keep it distinct from `{{repository}}`, the source repository selected by the skill. Use the tracker explicitly for every issue and label operation.

Missing baseline `spec` label → ask the user to follow the [WF installer](https://github.com/antshc/brain/blob/main/plugins/wf/install/install.md) in labels-only mode in the tracker repository, then retry.

### Publish spec

**Reads:** `{{initiativeId}}`, `{{specTitle}}`, `{{targetBranch}}`, `{{repository}}` (`owner/name`), `{{body}}`, and resolved `{{trackerRepository}}`.

1. Confirm `gh auth status`. List all specs, including closed ones, for the source repository:
   ```
   gh api --paginate repos/{{trackerRepository}}/issues --method GET -f state=all -f labels=spec,repo:target:{{repository}} -F per_page=100
   ```
   Ignore entries containing `pull_request`; inspect issue titles for the literal prefix `{{initiativeId}}:`. Any match → stop, report its URL, publish nothing. A lookup failure is not proof of absence.
2. Ensure routing labels exist:
   ```
   gh label create repo:target:{{repository}} --repo {{trackerRepository}} --color 0e8a16 --description "Source repository for this spec's tickets" --force
   gh label create repo:base:{{targetBranch}} --repo {{trackerRepository}} --color c5def5 --description "Base branch for this spec's feature branch" --force
   ```
3. Write the checked `{{body}}` verbatim to a temporary UTF-8 file. Create the issue:
   ```
   gh issue create --repo {{trackerRepository}} --label "spec,repo:target:{{repository}},repo:base:{{targetBranch}}" --title "{{initiativeId}}: {{specTitle}}" --body-file <file>
   ```
4. Read the returned issue with `gh issue view {{issueNumber}} --repo {{trackerRepository}} --json number,url,title,body,labels`; confirm title, body, and all three labels. Remove the temporary file.

**Returns:** verified spec issue number and URL. Tickets later become native sub-issues of this spec.

### Attach design artifacts

**Reads:** verified `{{issueNumber}}` created by this run, `{{trackerRepository}}`, and the bundle manifest.

1. `gh --version` below 2.103.2 → stop attaching; report that issue artifacts need gh ≥ 2.103.2 and leave the manifest in place for a retry. Never paste sketch files into the body or comments instead.
2. List existing artifacts once: `gh issue artifact list {{issueNumber}} -R {{trackerRepository}} --json number,name,type,url`.
3. For each manifest entry in order: name absent → create it; name present → replace its body. Never create a duplicate name.
   ```
   gh issue artifact create {{issueNumber}} --body-file <file> --name "<name>" --type <type> -R {{trackerRepository}}
   gh issue artifact edit {{issueNumber}} <artifactNumber> --body-file <file> -R {{trackerRepository}}
   ```
4. List again; every manifest name MUST be present with its type. Fill each `{{artifactUrl}}` in the **Design sketch** decision with its `url`, write the body to a temporary file, and `gh issue edit {{issueNumber}} --repo {{trackerRepository}} --body-file <file>`.
5. Read the issue back; confirm no `{{artifactUrl}}` remains. Remove temporary files and the bundle dir.

Partial failure → report attached and missing names, the bundle dir, and the published issue URL; the spec remains published. Rerunning this section resumes safely.

**Returns:** artifact count and names attached to the spec issue.

### Offline spec publishing

On explicit offline selection, skip GitHub operations. On missing tools, authentication, or API failure, report the failed operation and any known remote changes before saving locally. Save the rendered spec to `docs/specs/{{initiativeIdSlug}}.md`, retaining Initiative, source repository, base branch, and intended title in local metadata. Preserve an existing differing file rather than overwriting it without approval.

If creation may have reached GitHub before failing, reconcile with **Publish spec**'s lookup before retrying. If reconciliation is unavailable, mark the local copy's publication state unknown; never report it as unpublished with certainty or create another remote issue blindly. Return the local path and explicit offline/unknown status, not a GitHub success.

Architect run offline → copy each manifest file to `docs/specs/{{initiativeIdSlug}}/artifacts/` under its manifest file name, write the manifest there, and replace each `{{artifactUrl}}` with the relative artifact path. Attach them with **Attach design artifacts** once the spec is published.

### Spec publication gotchas

Use argument values, not shell interpolation, for user text. Quote values containing whitespace; multiline bodies use `--body-file`. A duplicate spec is a stop condition, not an outage triggering fallback. Do not substitute Jira or a local tracker backend. Artifact names come from the manifest verbatim; gh strips some characters, so match names after read-back, not before. Attach artifacts only to the issue this run created, never to a duplicate found by the lookup.

## Ticket operations

Use `{{trackerRepository}}` resolved by the skill for all commands. It holds the spec and its tickets; `repo:target:<owner>/<name>` identifies the source repository, not the tracker. Stop and report read/write failures; do not infer absent issues or edges from a failed lookup.

### Read spec

**Reads:** `{{specIssueNumber}}`.

```
gh issue view {{specIssueNumber}} --repo {{trackerRepository}} --json number,title,body,labels,comments
```

**Returns:** number, title, body, labels, comments. Require the `spec` label and exactly one `repo:target:` label before publication.

### Read design sketch

Optional. **Reads:** the spec's issue artifacts; run only online when the spec body has a **Design sketch** decision. No such decision → skip.

```
gh api -H "X-GitHub-Api-Version: 2026-03-10" "repos/{{trackerRepository}}/issues/{{specIssueNumber}}/artifacts?per_page=100&page={{page}}"
```

Loop pages until one returns fewer than 100 items. **Returns:** artifacts with `number`, `name`, `type`, `html_url`, `body`. Find **Sketch index**; read it and every artifact it lists (including `module-map.md` when listed). HTTP 404/410, a missing index, or an unreadable listed artifact → report the exact error and ask the user; never invent sketch content.

### Ticket labels

Missing baseline `hitl`, `spec`, or `bug` → ask the user to follow the [WF installer](https://github.com/antshc/brain/blob/main/plugins/wf/install/install.md) in labels-only mode in the tracker repository. Ensure the spec's routing label also exists:

```
gh label create {{repoLabel}} --repo {{trackerRepository}} --color 0e8a16 --description "Source repository for this spec's tickets" --force
```

### Reconcile reruns

List all children, including closed ones:

```
gh api --paginate repos/{{trackerRepository}}/issues/{{specIssueNumber}}/sub_issues?per_page=100
```

Map approved slices to existing child titles and bodies; labels do not encode HITL/AFK type. Reuse an unambiguous matching ticket; conflicting matches require user resolution. After interrupted creation, also inspect unlinked issues with the routing label and matching title/parent-spec content before creating replacements. A created issue remains recorded even if its parent-link request failed.

### Create sub-ticket

**Reads:** `{{title}}`, `{{body}}`, comma-separated `{{label}}`, `{{parentIssueNumber}}`.

1. Follow **Ticket labels**. Write the body verbatim to a temporary UTF-8 file:
   ```
   gh issue create --repo {{trackerRepository}} --label "{{label}}" --title "{{title}}" --body-file <file>
   ```
2. Record the returned URL/number immediately as `{{childIssueNumber}}`. Resolve its internal ID:
   ```
   gh api repos/{{trackerRepository}}/issues/{{childIssueNumber}} --jq .id
   ```
3. Unless already linked to this parent, link with the numeric ID, not the issue number:
   ```
   gh api repos/{{trackerRepository}}/issues/{{parentIssueNumber}}/sub_issues --method POST -F sub_issue_id={{childIssueId}}
   ```
4. Confirm the child appears in the parent's paginated sub-issues and its body/labels match the approved slice. Remove the temporary file.

**Returns:** verified child number and URL; on failure, report any created issue and unfinished link.

### Link blocking

**Reads:** `{{issueNumber}}`, `{{blockedBy}}` (blocker issue numbers).

List existing blockers first:

```
gh api --paginate repos/{{trackerRepository}}/issues/{{issueNumber}}/dependencies/blocked_by?per_page=100
```

For each missing blocker:

```
gh api repos/{{trackerRepository}}/issues/{{blockerNumber}} --jq .id
gh api repos/{{trackerRepository}}/issues/{{issueNumber}}/dependencies/blocked_by --method POST -F issue_id={{blockerId}}
```

**Returns:** confirmed blocker edges after rereading the dependency list. Ignore an already-linked response only after confirming that exact edge exists; surface other failures. Do not close or rewrite the parent spec.

### Offline ticket publishing

Explicit offline mode → use supplied local spec content and routing metadata; skip GitHub reads/writes. A missing spec or metadata requires user input, not invented content. An online failure → report the failed operation and preserve any known issue numbers/URLs and completed/pending links.

Save approved issue bodies under `docs/tickets/`, with distinct stable slice filenames. Include intended titles, labels, parent spec, symbolic blocker graph adjacency (including roots), and initial ready frontier in local metadata. Never invent GitHub issue numbers for unpublished slices. Preserve differing existing files unless replacement is approved.

Report local paths and unpublished/partially published status, not GitHub success. If a create response was lost, mark publication unknown and reconcile before retrying. Offline output does not satisfy the online native-link completion condition.

### Ticket operation gotchas

`gh issue edit --add-blocked-by` is unavailable; use the REST dependency endpoint. API internal `id` differs from issue `number`; `-F` sends numeric IDs. Preserve literal multiline text with `--body-file`. Do not replace native sub-issue/dependency edges with body links or substitute Jira.

## Wayfinder operations

### Repository and errors

Resolve `{{trackerRepository}}` using `gh repo view --json nameWithOwner --jq .nameWithOwner` from the docs/harness root or current single repository. An issue URL must belong to this tracker; resolve conflicting targets before acting. Use the explicit repository in every command.

Missing workflow labels → ask the user to follow the [WF installer](https://github.com/antshc/brain/blob/main/plugins/wf/install/install.md) in labels-only mode. Missing tools, authentication, permissions, or failed writes → stop and report the operation and known remote changes. Do not claim a map/claim/resolution exists until confirmed; no Jira/local tracker fallback.

Use `--body-file <file>` with a temporary UTF-8 file for literal multiline bodies, evidence, and comments. Remove temporary files after use. Placeholder values are arguments, not shell expressions.

### Create ticket

**Reads:** `{{title}}`, `{{body}}`, `{{label}}` (`wayfinder:map` for the map).

```
gh issue create --repo {{trackerRepository}} --label "{{label}}" --title "{{title}}" --body-file <file>
```

**Returns:** issue number and URL. Record both immediately. On an interrupted response, inspect matching issues before retrying; a failed response is not proof that no issue was created.

### Create Wayfinder sub-ticket

**Reads:** `{{title}}`, `{{body}}`, `{{label}}` (`wayfinder:<type>`), `{{parentIssueNumber}}` (map or narrower parent ticket).

1. List the parent's children with **List sub-tickets**; reuse an unambiguous existing match instead of duplicating a decision. On a partial earlier create, also reconcile unlinked issues by title and their **Part of** map link.
2. Follow **Create ticket**, retaining `{{childIssueNumber}}`.
3. Resolve the child's internal ID and attach it:
   ```
   gh api repos/{{trackerRepository}}/issues/{{childIssueNumber}} --jq .id
   gh api repos/{{trackerRepository}}/issues/{{parentIssueNumber}}/sub_issues --method POST -F sub_issue_id={{childIssueId}}
   ```
4. Confirm the child appears in the parent's sub-issue list. A link failure leaves a created issue: report it and retry only the missing link.

**Returns:** verified child number and URL.

### Read ticket

**Reads:** `{{issueNumber}}`.

```
gh issue view {{issueNumber}} --repo {{trackerRepository}} --json number,url,title,body,state,labels,comments,assignees
```

**Returns:** those fields. Fetch blockers by number to confirm they are closed; inaccessible blockers keep a ticket off the frontier.

### List sub-tickets

**Reads:** `{{issueNumber}}`.

```
gh api --paginate repos/{{trackerRepository}}/issues/{{issueNumber}}/sub_issues?per_page=100
```

**Returns:** every child's number, title, body, state, labels, assignees. Recurse through open children when finding the frontier. Use the body's **Blocked by** convention, not native dependency links, for Wayfinder decisions.

### Assign ticket

**Reads:** `{{issueNumber}}`. Refresh the ticket first; an assigned or closed ticket is not claimable.

```
gh issue edit {{issueNumber}} --repo {{trackerRepository}} --add-assignee "@me"
```

Read again to confirm the current user is the sole claimant before work. A conflicting claim requires choosing another ticket or resolving ownership; assignment is not atomic locking.

**Returns:** confirmed assignment.

### Unassign ticket

**Reads:** `{{issueNumber}}`.

```
gh issue edit {{issueNumber}} --repo {{trackerRepository}} --remove-assignee "@me"
```

**Returns:** confirmed no current-user assignee after **Read ticket**; the open ticket returns to the frontier.

### Comment on ticket

**Reads:** `{{issueNumber}}`, `{{body}}` (resolution/evidence).

```
gh issue comment {{issueNumber}} --repo {{trackerRepository}} --body-file <file>
```

**Returns:** resolution comment URL. Confirm it exists before closing.

### Close ticket

**Reads:** `{{issueNumber}}`, `{{comment}}` (short closing summary, after the detailed resolution comment).

```
gh issue close {{issueNumber}} --repo {{trackerRepository}} --comment "{{comment}}"
```

**Returns:** confirmed closed state after **Read ticket**. Out-of-scope closures go in the map's **Out of scope**, not **Decisions so far**.

### Update map or ticket

**Reads:** `{{issueNumber}}`, revised `{{body}}`.

Read the latest body first; preserve concurrent edits, existing decisions, fog, and scope boundaries. Apply the intended section change to a temporary UTF-8 file:

```
gh issue edit {{issueNumber}} --repo {{trackerRepository}} --body-file <file>
```

**Returns:** verified updated body. Reconcile partial comment/close/map-update failures before retrying so evidence and index entries are not duplicated.

### Prepare a result worktree

**Reads:** captured harness root, invocation worktree, branch, repository, and issue number. Verify `origin` points to the tracker repository. Pin the invocation branch tip. *Run `worktrees` skill to create an isolated worktree* from that SHA with a temporary branch and leaf named for the ticket and a unique run suffix. Save the ownership record outside all worktrees and pass the returned path to the runner. Wayfinder owns integration and cleanup.

### Publish a result

**Reads:** result worktree, verified artifact paths, issue number, and captured invocation branch/worktree.

1. Commit only verified artifact paths in the result worktree. Check the staged diff for unrelated files and temporary resources.
2. Serialize merges into the captured branch. Verify the original worktree is still on that branch and clean. If it has changed branches or has local changes, preserve the result and report the blocker. Fetch `origin` and compare the captured branch with its remote counterpart before merging. If pushing would publish unrelated local commits, stop and preserve the result unless the user authorized publishing them. Integrate any remote changes, then merge the result. Review the outgoing commits and diff before pushing.
3. Resolve safe artifact conflicts automatically. Reuse identical content. For independently added artifacts that collide, give the incoming artifact a ticket-number suffix and update links in the incoming artifacts. If both sides edited the same findings or the safe resolution is unclear, abort the in-progress merge, preserve the result branch and worktree, and report the conflict.
4. Push the captured branch to the same branch name on `origin` with a normal push. Use no pull requests or force pushes. If rejected because the remote advanced, fetch and integrate the new remote head, check for conflicts again, and retry. If access or branch protection blocks publication, preserve the work and report the blocker.
5. Fetch the remote branch and verify the publication commit is reachable and the artifact paths are present. Use commit-pinned links in the ticket. If the push or ticket write was interrupted, inspect remote history and existing comments before retrying. Resume at the first unconfirmed step. After successful publication and ticket linking, *run `worktrees` skill to remove the finished worktree* with the saved ownership record and verified result HEAD. After verified removal, delete the temporary branch only if its tip still matches the result integrated on the published branch. Preserve and report blocked cleanup.

### Wayfinder operation gotchas

Native sub-issues require the internal numeric `id`, not issue `number`; `-F` sends a number. Body links do not create parent/child relationships. Wayfinder's body-based blockers are intentionally distinct from implementation tickets' native blockers.
