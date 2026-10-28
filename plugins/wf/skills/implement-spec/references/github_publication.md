# Publication

Per-ticket publication: PR, evidence, ticket closure.

## Pull request lifecycle

Push with `git push --set-upstream REMOTE INTEGRATION_BRANCH`; subsequent pushes must succeed before reporting the PR current.

| Purpose | Command |
|---|---|
| Find existing PR | `gh pr list --repo SOURCE_REPOSITORY --head INTEGRATION_BRANCH --state open --json number,url,isDraft,baseRefName,headRefName` |
| Open draft | `gh pr create --repo SOURCE_REPOSITORY --base BASE_BRANCH --head INTEGRATION_BRANCH --draft --title "TITLE" --body-file PR_FILE` |
| Update coverage | `gh pr edit PR_NUMBER --repo SOURCE_REPOSITORY --body-file PR_FILE` |
| Read PR | `gh pr view PR_NUMBER --repo SOURCE_REPOSITORY --json url,title,body,headRefOid,isDraft,baseRefName,headRefName,state` |
| Inspect checks | `gh pr checks PR_NUMBER --repo SOURCE_REPOSITORY` |

Create the draft only after a verified ticket commit exists ahead of the base. Reuse a matching PR; preserve user-authored PR content when updating coverage. Add separate `Closes OWNER/REPO#NUMBER` lines only for implemented tickets, never skipped ones. Reference the spec without a closing keyword until closure gates pass; then add its closing reference.

Use title `{{initiative-id}}: <summary>` and a standalone `{{initiative-id}}` line as the body's first line, substituting the resolved `INITIATIVE_ID` literally (e.g. `PAY-12`). Code review takes the first ID in the body as the initiative, so no other ID (ticket reference, `#number`, Jira key) may precede it. **MUST NOT** add `Initiative source` or a separate initiative-source URL. On updates, keep other user text, ticket references and evidence below the ID line; replace legacy `[#ID]` markers and generated `Initiative:`/`Initiative source:` metadata with the ID line. Read title/body back and verify the first body ID matches before cleanup. Keep the tracker/spec identity in run context, not the PR description.

**PR description:** terse rationale bullets; each **MUST** answer “Why?” (why the work is needed, which problem/risk it addresses, why the outcome matters) from spec/ticket evidence. **MUST NOT** describe code changes, list files/symbols, narrate implementation, or reproduce a commit changelog. One bullet per distinct reason. Source gives no reason → report the missing rationale; never invent one. Keep initiative metadata, issue references and verification/blocker evidence separate from the bullets. Apply on creation and every coverage update; read the body back and check each bullet answers “Why?”.

Example rationale: `- Prevent duplicate charges when customers retry timed-out payments.` Avoid code summaries such as `- Add an idempotency check to PaymentService.`

Read back final body, target/head branches, draft state, and checks. Distinguish pending, failed, absent, and passed checks; required pending/failed checks block spec closure. Confirm `isDraft` is `true`. Never claim a nonexistent check passed.

## Ticket publication

After each verified integration:

1. Mark the ticket integrated in the run-local map.
2. Push `INTEGRATION_BRANCH`; after the first integrated commit, create or reuse the draft PR against `BASE_BRANCH` per *Pull request lifecycle*; sequential mode does so before starting the next ticket.
3. Post ticket evidence and PR pointer to the ticket's owning repository, then close it per *Closure and cleanup*.
4. Read back push, PR body, comment, and closure before reporting success.

## Closure and cleanup

Close each ticket with `gh issue close --reason completed` right after its commit and validation evidence are verified on the integration branch and the evidence comment is posted. Close the spec the same way only per *Closure gates*. Verify each closure with `gh issue view NUMBER --repo ISSUE_REPOSITORY --json state,stateReason`; on failure report it and never claim closure. Never close an issue whose commit or validation is missing, or that was skipped, cancelled, or deferred. PR closing keywords stay as a merge-time backstop.

Use temporary Markdown body files outside the repository; remove only those created by this run. Worktree cleanup follows worktrees *Actualize and cleanup*; retain dirty, unpushed, or incomplete work with an explicit report. Keep `RUN_DIR` and `EVIDENCE_DIR` after the run.
