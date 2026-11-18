# Shipping

## Code comments

Keep comments that explain a reason the code cannot show. Remove phase narration from code, scripts, and tests produced by the run before review. Use assertions and logs to show what happened.

## Prepare a direct branch

Before editing for Bug fix, *Load and follow the `github` skill to confirm the destination repository for the change, using Repository.* Then *Load and follow the `git` skill to name and prepare the branch, using Branches.*

Verify the pinned target and local and remote branch availability. Create from that target. If the checkout has unrelated changes, use a fresh worktree. When continuing an existing PR, reuse its recorded branch.

## Commit

For Codey work, *Load and follow the `crew-commit` skill to commit the current work with a report- or diff-derived message.* For an ordinary commit, use Git's Draft commit tactic and commit the verified paths with authorization. Keep commits small and ordered. Amend only when the fix belongs in the last commit and repository policy permits it.

## Opening a PR

Use these steps for direct code-shipping playbooks. Feature uses the draft returned by Implement and verifies its initiative, title, body, and coverage during Post-implementation.

1. *Load and follow the `github` skill to draft the PR title and description, using Pull requests and Draft PR.* Supply the initiative ID, verified head and base, rationale, changes, and observed checks. Resolve a missing initiative ID before publication.
2. *Load and follow the `github` skill to open the draft PR, using Pull requests.* Specify head and base explicitly. Read back the metadata and pushed head.
3. If review was requested, run [Review](review.md) from the source checkout through the proof summary. If human review was explicitly requested, follow the Human review handoff in [HITL](../playbooks/hitl.md) with the saved results. Reuse that automated pass.
4. Show the PR URL and continue. Monitor checks when requested by the caller.
