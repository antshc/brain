# Crew

Three implementation agents cover Python, AI authoring, and .NET: `codey-py`, `codey-ai`, and `codey-dotnet`. `chorey` reviews behavior-preserving cleanup. There is no base `codey` agent.

- `to-codey` and `ralph:dev` choose an implementation agent from the installed agents' descriptions, or `general-purpose` when none matches. Chorey uses the changed files and installed Chore rules skill descriptions to select applicable per-stack rules.
- Each Codey agent owns input, implementation, focused verification, gotchas, and its five-field status report. The .NET agent traces the functional slice and tests its highest useful observable seam. Python and AI agents use compact flows.
- Chorey's agent owns change discovery, rule selection, behavior-preserving review, scoped verification, and self-revert on failed checks. Chorey's report is informational; Codey's `STATUS` gates follow-up handling.
- `init-crew` copies per-stack `.github/instructions/*.instructions.md` into the codebase repo, offers `chore-<stack>-rules` skills, and creates `/gotchas-memory` in the harness repo's `.github/skills/`. Existing repository rules are preserved and merged. Legacy `.crew/` files are ignored.
- `/gotchas-memory` locates the repository's persistent gotchas file; `crew-gotchas` owns the shared read/write procedure; `to-commit` owns post-task commits.

Codey runs in cwd and uses `/gotchas-memory` directly; callers do not pass its storage location. Chorey receives only an optional trusted `## BASELINE_COMMIT`, runs in cwd, and likewise uses available Chore rules and `/gotchas-memory` skills directly. The gotchas skill encapsulates its storage path; an unavailable skill is a no-op. Applicable Copilot instructions are supplied automatically and need no explicit discovery step.

Every agent report has `STATUS`, `SUMMARY`, `FILES`, `GOTCHAS UPDATED`, and `NOTES`. For Codey, `complete` means the relevant checks passed or the requested state was already present, `partial` names persistent code errors, and `blocked` names a fundamental or environmental blocker. Chorey reports `complete` after a finished or self-reverted review and `skipped` when invalid input or unavailable Chore rules prevent review from starting.
