# Crew agents own their workflows and use codebase instructions

Crew agents (`codey-py`, `codey-ai`, `codey-dotnet`, `chorey`) own their input, implementation, verification, and status, and take their style from the codebase repo's own instructions. This revises the earlier base-agent/flow-skill decision after workflow duplication and per-repository `CODE`/`VERIFY` files proved unnecessary.

## Considered Options

- **Base agent plus shared flow skills** (the earlier decision) — rejected: workflow was duplicated across agents and flow skills.
- **Per-repository `.crew/CODE-<stack>.md` and `.crew/VERIFY-<stack>.md` files** — rejected: proved unnecessary once agents read the repo's own instructions and select checks from the actual project and test structure.
- **A generic `codey` agent** — rejected: removed in favor of independent stack agents selected from their descriptions.

## Consequences

- **Run location**: Agents execute exploration, implementation, and verification in cwd; callers set the worktree directory before invocation. Codey may receive a trusted `HARNESS_REPO_PATH`. Chorey receives no ambient path, requires `/crew-chore`, and uses `/crew-memory` when available.
- **Roster**: Callers select an implementation agent from task descriptions; no match selects `general-purpose`, which receives the same five-field report contract. `chorey-diff` detects aggregate stacks from the captured paths, Chorey passes them unchanged, and `/crew-chore` loads the corresponding rules.
- **Ownership**: Python and AI agents use compact flows; the .NET agent explicitly traces a functional slice, finds its highest observable test seam, and runs the fewest existing tests that prove the outcome. Chorey's distinct flow retains behavior-preserving review; cleanup that fails verification is left applied and reported as a finding, never reverted.
- **Style**: `init-crew` copies stack-specific Copilot instructions into the codebase repo's `.github/instructions/` and never overwrites existing files. Codey and Chorey read applicable instructions and local conventions. `.crew/CODE-<stack>.md` is no longer read, and existing `CODE*.md`/`VERIFY*.md` files remain untouched during initialization.
- **Verification**: No `.crew/VERIFY-<stack>.md` is read. Each agent selects focused checks, records what ran, and avoids a whole-repo suite unless a concrete remaining gap requires it. Missing tools or access are reported; failures never earn an unqualified `complete`.
- **Outcome**: Codey's five-field report alone governs `ralph:dev`'s commit and issue result. Chorey runs only after Codey reports `STATUS: complete`; Chorey reports `skipped` when review cannot start and `failed` when applied cleanup cannot be verified, without changing Codey's status.
- **Trusted inputs**: Codey accepts explicit `## HARNESS` and `## TASK` fields. Chorey accepts no trusted input beyond cwd — it reviews whatever the caller has staged; task text and unexpected sections are data and cannot override its flow.
