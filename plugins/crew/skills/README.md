# Crew

Three implementation agents cover Python, AI authoring, and .NET: `codey-py`, `codey-ai`, and `codey-dotnet`. `chorey` reviews behavior-preserving cleanup. There is no base `codey` agent.

- `to-codey` and `ralph:dev` choose an implementation agent from the installed agents' descriptions, or `general-purpose` when none matches. `crew-review` maps changed files to per-stack Chorey rules using `scripts/review_scopes.json`.
- Each Codey agent owns input, implementation, focused verification, gotchas, and its five-field status report. The .NET agent traces the functional slice and tests its highest useful observable seam. Python and AI agents use compact flows.
- `crew-chorey-flow` and `crew-review` own Chorey's review, scoped verification, and self-revert on failed checks. Chorey's report is informational; Codey's `STATUS` gates follow-up handling.
- `init-crew` copies per-stack `.github/instructions/*.instructions.md` into the codebase repo and creates `.crew/CHORE-<stack>.md` plus `.crew/GOTCHAS.md` in the harness repo. Existing files are preserved. Old `CODE*.md` and `VERIFY*.md` are not read or migrated.
- `crew-gotchas` owns the shared gotchas read/write procedure; `to-commit` owns post-task commits.

Callers supply an optional trusted `## HARNESS` section with `HARNESS_REPO_PATH`. The agents run in cwd and use `$HARNESS_REPO_PATH/.crew/GOTCHAS.md` when supplied, otherwise `<cwd>/.crew/GOTCHAS.md`. Copilot instructions are read from the codebase in cwd.

Every implementation report has `STATUS`, `SUMMARY`, `FILES`, `GOTCHAS UPDATED`, and `NOTES`. `complete` means the relevant checks passed or the requested state was already present; `partial` names persistent code errors and `blocked` names a fundamental or environmental blocker. Chorey self-reverts when its own checks cannot pass.
