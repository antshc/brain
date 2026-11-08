# Initialize Crew

Follow this file only on explicit request in Copilot CLI. Resolve templates from this file's directory. Resolve `REPO_PATH` from cwd with `git rev-parse --show-toplevel`; stop if cwd is not inside a Git repository. All generated Crew files belong to `REPO_PATH`.

## Install the Copilot plugin

1. Check `copilot plugin marketplace list --json`. If `brain` is absent, run `copilot plugin marketplace add antshc/brain`. Use the existing Brain marketplace when it points to that repository or to this installer checkout for local testing. Stop on a source conflict.
2. Check `copilot plugin list --json`. Install a missing plugin with `copilot plugin install crew@brain`. Local marketplaces can show uninstalled entries as disabled with `source: live`. For these entries, check only the matching `enabledPlugins` key in Copilot settings. An absent key permits the initial install; an explicit `false` is disabled. Recheck that `crew` is enabled from `brain` and that its version matches [plugin.json](../plugin.json). Report policy blocks, disabled installs, version mismatches, and failed commands before writing target files. Leave upgrades and enablement of existing installs to the user.

## Select stacks

Present the stack rule options from the template table below (`ai`, `dotnet`, `py`) and let the user choose one or more. No choice means create nothing.

## Copy missing files

For every chosen stack, create each missing target below and its parent directories. Never overwrite an existing target; add it to `Skipped` instead. Copy Copilot instruction templates verbatim. Their `applyTo` scope determines when Copilot loads each instruction.

| Stack | Target | Template |
|---|---|---|
| `ai` | `$REPO_PATH/.github/instructions/ai-authoring.instructions.md` | `templates/ai-authoring.instructions.template.md` |
| `dotnet` | `$REPO_PATH/.github/instructions/dotnet.instructions.md` | `templates/dotnet.instructions.template.md` |
| `py` | `$REPO_PATH/.github/instructions/python.instructions.md` | `templates/python.instructions.template.md` |
| all selections | `$REPO_PATH/.github/skills/crew-chore/SKILL.md` | `templates/chore.SKILL.template.md` with stack sections removed |
| each chosen stack | `$REPO_PATH/.github/skills/crew-chore/stacks/<stack>.md` | generated from that stack's section in `templates/chore.SKILL.template.md` |

To create `/crew-chore`, read `templates/chore.SKILL.template.md` and write its common content, omitting every stack section and section marker, to its `SKILL.md` target. For each chosen stack, preserve the contents within every matching `<!-- stack: <stack> -->` through `<!-- /stack: <stack> -->` pair, omit all section markers and all other stacks' sections, and write the result to `stacks/<stack>.md`. Each stack file is read by `/crew-chore`.

Do not read from, migrate, report on, or modify `.crew/`, `.droid/`, `CODE*.md`, or `VERIFY*.md` files.

For each selected stack file, inspect the target repository's review conventions. For a newly created file, replace its repository-rules placeholder with observed rules while preserving the shipped safety constraints. For an existing file, semantically merge the shipped seed: preserve all repository-authored wording and conflicting repository rules, add only non-conflicting shipped rules, and report every conflict. Never rewrite copied Copilot instructions during setup; the user can customize them after scaffolding.

**Emit**: Plugin installed or reused. `REPO_PATH=<path>. Rules skills: <list>. Created: <paths>. Merged: <paths or none>. Skipped: <existing paths>. Review conflicts: <count or none>.`

Leave target changes uncommitted.
