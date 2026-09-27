# Crew

Three implementation agents cover Python, AI authoring, and .NET: `codey-py`, `codey-ai`, and `codey-dotnet`. `chorey` reviews behavior-preserving cleanup. There is no base `codey` agent.

- `to-codey` and `ralph:dev` choose an implementation agent from the installed agents' descriptions, or `general-purpose` when none matches. Chorey requires `/crew-chore`, which selects applicable repository-local stack rule files from the changed files.
- Each Codey agent owns input, implementation, focused verification, gotchas, and its five-field status report. The .NET agent traces the functional slice and tests its highest useful observable seam. Python and AI agents use compact flows.
- `chorey-diff` owns Chorey's commit/uncommitted change capture, manifest, exact standalone snapshots, restoration, and artifact cleanup. Chorey's agent owns rule selection, behavior-preserving review, scoped verification, and the decision to self-revert failed cleanup. Chorey's report is informational; Codey's `STATUS` gates follow-up handling.
- `init-crew` copies per-stack `.github/instructions/*.instructions.md` into the codebase repo, creates `/crew-chore` with per-stack rule files, and creates `/crew-memory` in the harness repo's `.github/skills/`. Existing repository rules are preserved and merged. Legacy `.crew/` files are ignored.
- `/crew-memory` owns the repository's persistent `GOTCHAS.md`; it passes the stored rules to `crew-gotchas`, which owns the shared rule-processing procedure. `chorey-diff` owns the temporary `bin/crew_diff/` review bundle; `to-commit` owns post-task commits.

Codey runs in cwd and uses `/crew-memory` directly; callers do not pass its storage location. Chorey receives only an optional trusted `## BASELINE_COMMIT`, runs in cwd, and requires `/crew-chore` plus `/crew-memory` when available. The Chore skill owns stack-rule selection; the memory skill owns storage and passes only loaded rules to `/crew-gotchas`; an unavailable memory skill is a no-op. Applicable Copilot instructions are supplied automatically and need no explicit discovery step.

Every agent report has `STATUS`, `SUMMARY`, `FILES`, `GOTCHAS UPDATED`, and `NOTES`. For Codey, `complete` means the relevant checks passed or the requested state was already present, `partial` names persistent code errors, and `blocked` names a fundamental or environmental blocker. Chorey reports `complete` after a finished or self-reverted review and `skipped` when invalid input or `/crew-chore` is unavailable.
