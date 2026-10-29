# GitHub spec publication

## Repository and labels

Resolve `{{trackerRepository}}` with `gh repo view --json nameWithOwner --jq .nameWithOwner` from the docs/harness root (or current repository for single-repo work). Keep it distinct from `{{repository}}`, the source repository selected by the skill. Use the tracker explicitly for every issue and label operation.

Missing baseline `spec` label → *run `init-wf` skill for wf setup and GitHub issue labels, using labels-only mode* in the tracker repository, then retry.

## Publish spec

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

## Attach design artifacts

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

## Offline publishing

On explicit offline selection, skip GitHub operations. On missing tools, authentication, or API failure, report the failed operation and any known remote changes before saving locally. Save the rendered spec to `docs/specs/{{initiativeIdSlug}}.md`, retaining Initiative, source repository, base branch, and intended title in local metadata. Preserve an existing differing file rather than overwriting it without approval.

If creation may have reached GitHub before failing, reconcile with **Publish spec**'s lookup before retrying. If reconciliation is unavailable, mark the local copy's publication state unknown; never report it as unpublished with certainty or create another remote issue blindly. Return the local path and explicit offline/unknown status, not a GitHub success.

Architect run offline → copy each manifest file to `docs/specs/{{initiativeIdSlug}}/artifacts/` under its manifest file name, write the manifest there, and replace each `{{artifactUrl}}` with the relative artifact path. Attach them with **Attach design artifacts** once the spec is published.

## Gotchas

Use argument values, not shell interpolation, for user text. Quote values containing whitespace; multiline bodies use `--body-file`. A duplicate spec is a stop condition, not an outage triggering fallback. Do not substitute Jira or a local tracker backend. Artifact names come from the manifest verbatim; gh strips some characters, so match names after read-back, not before. Attach artifacts only to the issue this run created, never to a duplicate found by the lookup.
