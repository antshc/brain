---
name: init-crew
description: "Initialize Crew conventions when the user explicitly requests setup in a repository. Copy selected stack Copilot instructions, offer repository-local Chore rules skills, and create shared gotchas memory without overwriting repository conventions."
disable-model-invocation: true
---

# Initialize Crew

Run on explicit user invocation. Resolve `HARNESS_REPO_PATH` and `CODEBASE_REPO_PATH` via `/resolve-harness`; use cwd for `HARNESS_REPO_PATH` when unavailable or empty and use `HARNESS_REPO_PATH` for `CODEBASE_REPO_PATH` when absent. Stop on a resolver error. Validate both as existing directories. Copilot instructions belong to the codebase; Chore rules skills and gotchas memory belong to the harness. Never create or modify `.harness.env`.

## Select stacks

Read `codey-<stack>.agent.md` in this plugin's `agents/` directory to discover the installed roster. Present the available stack rule files for the stack ids (`ai`, `dotnet`, `py`) and let the user choose one or more. No choice means create nothing. Do not infer or offer stacks outside that roster.

## Copy missing files

For every chosen stack, create each missing target below and its parent directories. Never overwrite an existing target; add it to `Skipped` instead. Copy Copilot instruction templates verbatim. Their `applyTo` scope determines when Copilot loads each instruction.

| Stack | Target | Template |
|---|---|---|
| `ai` | `$CODEBASE_REPO_PATH/.github/instructions/ai-authoring.instructions.md` | `templates/ai-authoring.instructions.template.md` |
| `dotnet` | `$CODEBASE_REPO_PATH/.github/instructions/dotnet.instructions.md` | `templates/dotnet.instructions.template.md` |
| `py` | `$CODEBASE_REPO_PATH/.github/instructions/python.instructions.md` | `templates/python.instructions.template.md` |
| all selections | `$HARNESS_REPO_PATH/.github/skills/crew-chore/SKILL.md` | `templates/chore.SKILL.template.md` with stack sections removed |
| each chosen stack | `$HARNESS_REPO_PATH/.github/skills/crew-chore/stacks/<stack>.md` | generated from that stack's section in `templates/chore.SKILL.template.md` |

To create `/crew-chore`, read `templates/chore.SKILL.template.md` and write its common content, omitting every stack section and section marker, to its `SKILL.md` target. For each chosen stack, preserve the contents within every matching `<!-- stack: <stack> -->` through `<!-- /stack: <stack> -->` pair, omit all section markers and all other stacks' sections, and write the result to `stacks/<stack>.md`. Each stack file is read by `/crew-chore`.

Also create `$HARNESS_REPO_PATH/.github/skills/crew-memory/SKILL.md` from `templates/crew-memory.SKILL.template.md` when missing. Do not read from, migrate, report on, or modify `.crew/`, `.droid/`, `CODE*.md`, or `VERIFY*.md` files.

For each selected stack file, inspect the target repository's review conventions. For a newly created file, replace its repository-rules placeholder with observed rules while preserving the shipped safety constraints. For an existing file, semantically merge the shipped seed: preserve all repository-authored wording and conflicting repository rules, add only non-conflicting shipped rules, and report every conflict. Never rewrite copied Copilot instructions during init; the user can customize them after scaffolding.

**Emit**: `HARNESS_REPO_PATH=<path>. CODEBASE_REPO_PATH=<path>. Rules skills: <list>. Created: <paths>. Merged: <paths or none>. Skipped: <existing paths>. Review conflicts: <count or none>.`
