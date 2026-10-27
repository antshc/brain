---
name: init-wf
description: One-time wf setup — confirms repository topology, seeds Copilot instructions, bootstraps ARCHITECTURE.md/GLOSSARY.md, and creates GitHub issue labels. Use before the workflow or in labels-only mode to repair missing labels.
disable-model-invocation: true
---

# Setup WF

Sets up the environment for wf's domain-modeling skills: **single repo** (docs + codebase together) or **wrapping/harness repo** (multi-root workspace; reporoot tracks docs/decisions, codebase in a separate git-ignored `workspace/` repo).

**Labels-only mode:** follow **4. Set up GitHub labels** in the tracker repository; skip topology, instructions, and docs setup.

## 1. Confirm topology

Ask the user:

- **Single repo** — docs and codebase together. No harness split.
- **Wrapping (harness) repo** — reporoot tracks docs/decisions only; codebase in a separate repo nested under `workspace/` (git-ignored).

Then:

- **Single repo** → copilot instructions in `.github/copilot-instructions.md`. No `workspace/` split.
- **Wrapping repo** → copilot instructions in the reporoot's `.github/copilot-instructions.md`. If `workspace/` isn't set up or git-ignored:
  ```bash
  echo "workspace/" >> .gitignore
  git status --short   # confirm the harness ignores the nested source
  ```
  Resolve `{{codeRepoName}}`/`{{codeRepoSlug}}` from the nested repo (e.g. `git -C workspace/{{codeRepoName}} remote get-url origin`).

  Run `/init-harness` skill from the reporoot so `.github/skills/harness/` exists (the `harness` skill, its settings file, and its pull command) — without it, ralph tooling falls back to treating the harness root as the codebase root.

## 2. Seed the copilot instructions

Seed content: [copilot-instructions.template.md](./copilot-instructions.template.md) — same section structure as a working harness example (topology, safety/targeting, authoritative sources, code navigation, external repos, build/validation, doc conventions, skills).

- Create `.github/copilot-instructions.md` if missing. If present, append only missing sections — no duplicate headings, no overwriting unrelated content.
- Resolve every `{{placeholder}}` (e.g. `{{boardRepoName}}`, `{{codeRepoName}}`, `{{codeRepoSlug}}`) before writing — never leave a raw `{{...}}`. Drop sections 4/5/8/9 rows if no matching tooling/dependencies/skills exist beyond `gh`. For a single repo, drop/adjust `workspace/`-specific wording (sections 1, 2, 6).

## 3. Bootstrap the docs

*Run `bootstrap-docs` skill for ARCHITECTURE.md and GLOSSARY.md existence-and-creation mechanics* at the docs root (reporoot for a wrapping repo).

## 4. Set up GitHub labels

Follow [github.md](./github.md) **Setup labels**. Done when all nine baseline labels exist in the tracker repository.

## Completion criteria

- Topology confirmed; `workspace/` split (if any) set up.
- For a wrapping repo, `.github/skills/harness/` exists (the `harness` skill, its settings file, and its pull command) at the harness root.
- Copilot instructions seeded in `.github/copilot-instructions.md`, placeholders resolved, no duplicate sections.
- `ARCHITECTURE.md` and `GLOSSARY.md` exist.
- All nine GitHub baseline labels exist; labels-only mode requires only this condition.
