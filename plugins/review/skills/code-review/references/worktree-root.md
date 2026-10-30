# Worktree root

Every worktree lives at `@repoRoot/.worktrees/<REPO>/<NAME>`; never create one elsewhere.

## Resolve

1. Set `@repoRoot` to the output of `git rev-parse --show-toplevel`, run from the agent session's launch folder, not the current CWD. **MUST NOT** re-resolve `@repoRoot` from a git worktree or nested repo (e.g. code repo under `workspace/`) after a `cd`; those are code roots, not `@repoRoot`.
2. `<REPO>` = repository name from the PR's `OWNER/REPO`, not a folder name. `<NAME>` = one safe path component.
3. `WORKTREES_ROOT` = `@repoRoot/.worktrees/<REPO>`. Same root whether `@repoRoot` is the code repo itself or a harness holding it under `workspace/<REPO>`. `@repoRoot/.worktrees/` or its `<REPO>/` child already exists → reuse it; absent → create it (`mkdir -p`). Only the `<NAME>` leaf must be new. Confirm every resolved path stays under `WORKTREES_ROOT`.

## Ignore

Idempotent; before the first `git worktree add`. Add only missing entries; preserve other content and comments; never commit. Report every file changed.

1. **Git:** `git -C @repoRoot check-ignore -q .worktrees/`. Not ignored → append `/.worktrees/` to `git -C @repoRoot rev-parse --path-format=absolute --git-path info/exclude`; recheck. Still not ignored (tracked negation) → stop and report.
2. **VS Code:** `@repoRoot/.vscode/settings.json` (create if absent) holds `"search.exclude": {"**/.worktrees": true}` and `"files.watcherExclude": {"**/.worktrees/**": true}`; merge into existing objects.
3. **JetBrains:** only when `@repoRoot/.idea/` exists. Rider (`.idea/.idea.*/.idea/`) → `indexLayout.xml` `<explicitExcludes>` holds `<Path>` to `@repoRoot/.worktrees` relative to the solution directory. Other IDEs → each `.idea/*.iml` `<content>` whose url resolves to `@repoRoot` holds `<excludeFolder url="<content url>/.worktrees" />`.

Done when the git check passes and existing editor configs exclude `.worktrees`.
