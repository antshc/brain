# Install WF

Follow this file only on explicit request in Copilot CLI. Resolve the target with `git rev-parse --show-toplevel` and assets from this file's absolute path. Stop if the target is outside a Git repository.

Sets up the environment for wf's domain-modeling skills: **single repo** (docs + codebase together) or **wrapping/harness repo** (multi-root workspace; reporoot tracks docs/decisions, codebase in a separate git-ignored `workspace/` repo).

**Labels-only mode:** follow **4. Set up GitHub labels** in the tracker repository; skip plugin installation and every other setup step, then report the label check results.

## 1. Confirm topology

Ask the user:

- **Single repo** — docs and codebase together. No harness split.
- **Wrapping (harness) repo** — reporoot tracks docs/decisions only; codebase in a separate repo nested under `workspace/` (git-ignored).

## Install the Copilot plugin

1. Check `copilot plugin marketplace list --json`. If `brain` is absent, run `copilot plugin marketplace add antshc/brain`. Use the existing Brain marketplace when it points to that repository or to this installer checkout for local testing. Stop on a source conflict.
2. Check `copilot plugin list --json`. Install a missing plugin with `copilot plugin install wf@brain`. Local marketplaces can show uninstalled entries as disabled with `source: live`. For these entries, check only the matching `enabledPlugins` key in Copilot settings. An absent key permits the initial install; an explicit `false` is disabled. Recheck that `wf` is enabled from `brain` and that its version matches [plugin.json](../plugin.json). Report policy blocks, disabled installs, version mismatches, and failed commands before writing target files. Leave upgrades and enablement of existing installs to the user.

Check that WF Doc architecture and GitHub are available before writing target files; load each owning skill at its action below. If it is missing after installation, ask the user to run `/restart` and say “Resume the WF installer for <target> in <topology> mode.”

## Configure the selected topology

- **Single repo** → copilot instructions in `.github/copilot-instructions.md`. No `workspace/` split.
- **Wrapping repo** → first follow [the Ralph installer](../../ralph/install/install.md) with the same explicit harness root. If the Brain `plugins/` source directory is unavailable to the session, ask the user to allow it with `/add-dir`. Stop on failed Ralph installation. Then put copilot instructions in the reporoot's `.github/copilot-instructions.md`. If `workspace/` isn't set up or git-ignored:
  ```bash
  echo "workspace/" >> .gitignore
  git status --short   # confirm the harness ignores the nested source
  ```
  Resolve `{{codeRepoName}}`/`{{codeRepoSlug}}` from the nested repo (e.g. `git -C workspace/{{codeRepoName}} remote get-url origin`).

- **Both** → git worktrees live in `.worktrees/<repo-name>/<name>` at the reporoot. `git check-ignore -q .worktrees/` fails → `echo "/.worktrees/" >> .gitignore`.

## 2. Seed the copilot instructions

Seed content: [copilot-instructions.template.md](./copilot-instructions.template.md) — same section structure as a working harness example (topology, safety/targeting, authoritative sources, code navigation, external repos, build/validation, doc conventions, skills).

- Create `.github/copilot-instructions.md` if missing. If present, append only missing sections — no duplicate headings, no overwriting unrelated content.
- Resolve every `{{placeholder}}` (e.g. `{{boardRepoName}}`, `{{codeRepoName}}`, `{{codeRepoSlug}}`) before writing — never leave a raw `{{...}}`. Drop sections 4/5/8/9 rows if no matching tooling/dependencies/skills exist beyond `gh`. For a single repo, drop/adjust `workspace/`-specific wording (sections 1, 2, 6).

## 3. Bootstrap the docs

*Load and follow the `record-architecture` skill to initialize missing docs* with route `initialize` at the docs root (reporoot for a wrapping repo).

## 4. Set up GitHub labels

Follow [github.md](./github.md) **Setup labels**. Done when all nine baseline labels exist in the tracker repository.

## 5. Install factory-mode

Ask the user whether to install the `factory-mode` skill at repo level; it holds the repo-level engineering instructions (principles, design preferences, playbooks). Yes → run from the reporoot:

```bash
gh skill install antshc/brain plugins/wf/install/assets/factory-mode/SKILL.md --agent github-copilot --scope project
```

Already installed → skip; never overwrite (no `-f`), the repo copy carries user edits. Then tell the user to edit the installed `SKILL.md` and playbooks to align with the repo's conventions (layering, patterns, build/verify commands), and to run `/sync-skill` to pull upstream improvements later.

## Completion criteria

- Topology confirmed; `workspace/` split (if any) set up.
- For a wrapping repo, `.github/skills/harness/` exists (the `harness` skill, its settings file, and its pull command) at the harness root.
- Copilot instructions seeded in `.github/copilot-instructions.md`, placeholders resolved, no duplicate sections.
- `ARCHITECTURE.md` and `GLOSSARY.md` exist.
- All nine GitHub baseline labels exist; labels-only mode requires only this condition.
- User asked about `factory-mode`; if accepted, it is installed at project scope.

Report plugin status, created, merged and skipped files, label check results, and missing prerequisites. Leave target changes uncommitted.
