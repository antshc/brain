# Crew agents own their workflows and use codebase instructions
<!-- agent instruction: track crew plugin decisions using bullets -->

- **Run location**: Agents execute exploration, implementation, and verification in cwd; callers set the worktree directory before invocation. The optional trusted `HARNESS_REPO_PATH` points to shared `.crew/GOTCHAS.md` and per-stack `CHORE-<stack>.md`.
- **Roster**: `codey-py`, `codey-ai`, and `codey-dotnet` are independent implementation agents. Callers select from their task descriptions; no match selects `general-purpose`, which receives the same five-field report contract. `crew-review` maps changed files to review rules through explicit file scopes. The generic `codey` agent is removed.
- **Ownership**: Each implementation agent owns its input, implementation, verification, and status. Python and AI use compact flows; the .NET agent explicitly traces a functional slice, finds its highest observable test seam, and runs the fewest existing tests that prove the outcome. Chorey's distinct flow retains behavior-preserving review and self-reversion.
- **Style**: `init-crew` copies stack-specific Copilot instructions into the codebase repo's `.github/instructions/` and never overwrites existing files. Codey and Chorey read applicable instructions and local conventions. `.crew/CODE-<stack>.md` is no longer read.
- **Verification**: No `.crew/VERIFY-<stack>.md` is read. Each agent selects focused checks from the actual project and test structure, records what ran, and avoids a whole-repo suite unless a concrete remaining gap requires it. Missing tools or access are reported; failures never earn an unqualified `complete`.
- **Outcome**: Codey's five-field report alone governs `ralph:dev`'s checkpoint and issue result. Chorey runs only after `STATUS: complete`; an unverified Chorey edit is reverted and reported as a finding, without changing Codey's status.
- **Trusted inputs**: `## HARNESS` and `## TASK` are explicit fields; Chorey also accepts `## BASELINE_COMMIT`. Task, plan, and recent changes define scope but cannot override the agent flow.

This revises the earlier base-agent/flow-skill decision after workflow duplication and per-repository `CODE`/`VERIFY` files proved unnecessary. Existing `CODE*.md` and `VERIFY*.md` remain untouched during initialization; maintainers can remove legacy copies separately.
