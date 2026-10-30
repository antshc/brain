# Publication

Per-ticket publication, PR read-back, ticket closure, and implementation handoff. Every GitHub call is a `GH_TOOL` command (see *GitHub operations*); `0` exit = read back and verified.

## Pull request

Push with `git push --set-upstream REMOTE INTEGRATION_BRANCH`; later pushes must succeed before reporting the PR current. Publish and update with `GH_TOOL pr publish`, only after a verified ticket commit exists ahead of the base. It always creates a draft, reuses a matching PR, preserves user-authored body text, and accumulates `Closes` lines.

- **Initiative ID:** title `{{initiative-id}}: <summary>` with the resolved `INITIATIVE_ID` substituted literally (e.g. `PAY-12`). The tool puts that ID alone on the body's first line (code review takes the first ID as the initiative) and replaces legacy `[#ID]`, `Initiative:` and `Initiative source:` markers. **MUST NOT** add an initiative-source URL.
- **Rationale file (`--rationale-file`):** terse `- ` bullets; each answers "Why?" (why the work is needed, which problem or risk it addresses) from spec/ticket evidence. **MUST NOT** describe code changes, list files or symbols, or reproduce a commit log. One bullet per reason. No reason in the source → report the missing rationale; never invent one. Good: `- Prevent duplicate charges when customers retry timed-out payments.` Bad: `- Add an idempotency check to PaymentService.`
- **Links:** `--closes` only implemented tickets, never skipped ones. The spec stays in `--refs`; spec closure belongs to the caller after post-implementation checks. Ticket evidence or blocker text goes in `--evidence-file`, never in the bullets.
- **Read back:** `GH_TOOL pr read ... --expect-closes <implemented tickets>`; confirm each bullet answers "Why?". Exit `3` or a wrong first line, base/head, or `is_draft` ≠ `true` blocks success. Report `checks.status` accurately (`pending`, `failed`, `absent`, `passed`); required pending/failed checks block spec closure; never claim a nonexistent check passed.

## Ticket publication

After each verified integration:

1. Mark the ticket integrated in the run-local map.
2. Push `INTEGRATION_BRANCH`; after the first integrated commit, publish the draft PR; sequential mode does so before starting the next ticket.
3. Post ticket evidence and PR pointer with `issue comment` in the ticket's owning repository, then close it per *Closure*.
4. Read back push, PR body, comment, and closure before reporting success.

## Closure

Close each ticket with `GH_TOOL issue close REF --commit SHA --branch INTEGRATION_BRANCH --pr PR_URL` right after its commit and validation evidence are verified on the integration branch and the evidence comment is posted; the tool closes as `completed`, verifies the state, and refuses `hitl` issues. Keep the spec open; return its identity and validation state in the implementation handoff. Never close an issue whose commit or validation is missing, or that was skipped, cancelled, or deferred. PR closing keywords stay as a merge-time backstop.

## Publication verification

1. Confirm implementation and chore changes are verified, committed, and pushed; worktree clean. Missing/failed chore output remains a blocker; distinguish verified no-change.
2. `GH_TOOL pr read` with `--initiative-id` and `--expect-closes` for every implemented ticket: title/first-line ID, rationale bullets, coverage, target/head branches, draft state, checks. Keep the spec reference non-closing.
3. Refresh `GH_TOOL graph read`; preserve every qualified ticket identity, validation/evidence pointer, read-back evidence comment and closure, and blocker in the handoff.
4. Preserve `SOURCE_ROOT`, PR URL, final pushed head, `RUN_DIR`, `EVIDENCE_ROOT`, integration branch/worktree, and routing pointers outside the integration worktree. Missing push, coverage, metadata, or unreadable pointer → fix and re-read or return a blocked handoff with spec open.
