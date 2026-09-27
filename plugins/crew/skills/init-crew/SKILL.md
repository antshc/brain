---
name: init-crew
description: "Initialize Crew conventions when the user explicitly requests setup in a repository. Copy selected stack Copilot instructions and review templates and create shared gotchas without overwriting existing files."
disable-model-invocation: true
---

# Initialize Crew

Run on explicit user invocation. Resolve `HARNESS_REPO_PATH` and `CODEBASE_REPO_PATH` via `/resolve-harness`; use cwd for `HARNESS_REPO_PATH` when unavailable or empty and use `HARNESS_REPO_PATH` for `CODEBASE_REPO_PATH` when absent. Stop on a resolver error. Validate both as existing directories. Copilot instructions belong to the codebase; review rules and gotchas belong to the harness. Never create or modify `.harness.env`.

## Select stacks

Read `codey-<stack>.agent.md` in this plugin's `agents/` directory to discover the installed roster. Present the available stack ids (`ai`, `dotnet`, `py`) and let the user choose one or more. No choice means create nothing. Do not infer or offer stacks outside that roster.

## Copy missing files

For every chosen stack, run `python3 <skill-directory>/scripts/copy_templates.py --harness-repo <HARNESS_REPO_PATH> --codebase-repo <CODEBASE_REPO_PATH> <chosen-stack>...`. It copies each missing template verbatim, creates parent directories, and skips existing targets without merging or overwriting. The templates' `applyTo` scope determines when Copilot loads each instruction.

| Stack | Target | Template |
|---|---|---|
| `ai` | `$CODEBASE_REPO_PATH/.github/instructions/ai-authoring.instructions.md` | `templates/ai-authoring.instructions.template.md` |
| `dotnet` | `$CODEBASE_REPO_PATH/.github/instructions/dotnet.instructions.md` | `templates/dotnet.instructions.template.md` |
| `py` | `$CODEBASE_REPO_PATH/.github/instructions/python.instructions.md` | `templates/python.instructions.template.md` |
| each chosen stack | `$HARNESS_REPO_PATH/.crew/CHORE-<stack>.md` | `templates/CHORE-<stack>.template.md` |

Also create `$HARNESS_REPO_PATH/.crew/GOTCHAS.md` from `templates/GOTCHAS.template.md` if missing. Do not touch any pre-existing `CODE*.md` or `VERIFY*.md` files; agents no longer read them. Do not read from or migrate `.droid/`.

For each newly created `CHORE-<stack>.md` only, inspect the target repository's review conventions and replace placeholders with observed rules. Preserve its shipped safety constraints; record a discovered conflict in `GOTCHAS.md`. Never rewrite copied Copilot instructions during init; the user can customize them after scaffolding.

**Emit**: `HARNESS_REPO_PATH=<path>. CODEBASE_REPO_PATH=<path>. Stacks: <list>. Created: <paths>. Skipped: <existing paths>. Review conflicts: <count or none>.`
