---
name: setup-wf
description: One-time wf-plugin setup — confirms single-repo vs. wrapping/harness-repo topology, seeds `.github/copilot-instructions.md` accordingly, bootstraps ARCHITECTURE.md/CONTEXT.md, and creates the ticket-tracker labels. Run once before first use of the other wf skills.
disable-model-invocation: true
---

# Setup WF

Sets up the environment for wf's domain-modeling skills: **single repo** (docs + codebase together) or **wrapping/harness repo** (multi-root workspace; reporoot tracks docs/decisions, codebase in a separate git-ignored `workspace/` repo).

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

## 2. Seed the copilot instructions

Seed content: [copilot-instructions.template.md](./copilot-instructions.template.md) — same section structure as a working harness example (topology, safety/targeting, authoritative sources, code navigation, external repos, build/validation, doc conventions, skills).

- Create `.github/copilot-instructions.md` if missing. If present, append only missing sections — no duplicate headings, no overwriting unrelated content.
- Resolve every `{{placeholder}}` (e.g. `{{boardRepoName}}`, `{{codeRepoName}}`, `{{codeRepoSlug}}`) before writing — never leave a raw `{{...}}`. Drop sections 4/5/8/9 rows if no matching tooling/dependencies/skills exist beyond `gh`. For a single repo, drop/adjust `workspace/`-specific wording (sections 1, 2, 6).

## 3. Bootstrap the docs

Run `/bootstrap-docs`' skill **Mandatory creation** at the docs root (reporoot for a wrapping repo) — the once-per-repo firing of that guarantee.

## 4. Set up the ticket tracker

Run `/manage-backlog` skill **Setup labels**.

## Done when

- Topology confirmed; `workspace/` split (if any) set up.
- Copilot instructions seeded in `.github/copilot-instructions.md`, placeholders resolved, no duplicate sections.
- `ARCHITECTURE.md` and `CONTEXT.md` exist.
- `/manage-backlog` **Setup labels** ran without error.
