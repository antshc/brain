# Copilot Instructions

## 1. Scope and repository topology

This repo (the **reporoot**) is the **documentation/context repo** — the harness, not the codebase.

- **Docs & decisions at the reporoot:** `CONTEXT.md` (domain glossary), `ARCHITECTURE.md` (ADR/Concept indexes + high-level source structure), ADRs under `docs/adr/` (localized decisions), Crosscutting Concepts under `docs/concepts/` (architectural backbone).
- **Source code ({{codeRepoName}}) & git worktrees in `workspace/`** (git-ignored by the reporoot). Source hierarchy documented under **Codebase Structure** in `ARCHITECTURE.md`.

Conflict order: **safety/targeting → authoritative sources → code navigation → external repos → build/validation → doc conventions.** Scopes only this file — doesn't override `AGENTS.md`, path-scoped instructions, or user instructions. Don't author rules that conflict across instruction files.

## 2. Safety and repository targeting

MUST NOT introduce **code changes, build artifacts, or code PRs** into the `{{boardRepoName}}` reporoot. All *code* work happens inside `workspace/{{codeRepoName}}` — MUST NOT make code changes, run builds, or create worktrees anywhere else.

Authoring, committing, and opening PRs for docs (`CONTEXT.md`, `ARCHITECTURE.md`, ADRs, Crosscutting Concepts, other reporoot docs) is allowed in `{{boardRepoName}}`. MUST NOT commit code or build output there.

Verify the target repo before any **code/build** `git`/`gh pr` command by checking `origin` exactly. Workspace code repo's `origin`: `{{codeRepoSlug}}`. Reporoot's `origin`: `{{boardRepoSlug}}`.

```bash
test "$(git remote get-url origin | sed -E 's#(git@github.com:|https://github.com/)##; s#\.git$##')" = "{{codeRepoSlug}}"
```

Also confirm the repo root for filesystem operations:

```bash
git rev-parse --show-toplevel
```

If `origin` ≠ `{{codeRepoSlug}}` (e.g. `{{boardRepoSlug}}` or any unrelated repo) and the action is code/build — **stop**, `cd workspace/{{codeRepoName}}` first. Doc commits/PRs may proceed in `{{boardRepoName}}`.

MUST actually execute the check command above — not merely reference or reason about it — before the first `git`/`gh` code action per session (including `git worktree add`); this guard has been skipped when only stated in prose.

### Action → target repo

| Action | Target repo | How to target |
| --- | --- | --- |
| **Code** `git worktree add`, `git commit`, `git push`, code `gh pr create` | workspace (`{{codeRepoName}}`) | `cd workspace/{{codeRepoName}}` first |
| Code-modifying, build, test, package, and source-repository Git commands | workspace (`{{codeRepoName}}`) | run from inside `workspace/{{codeRepoName}}` |
| **Docs** `git commit`, `git push`, `gh pr create` (for `CONTEXT.md`, `ARCHITECTURE.md`, ADRs, Crosscutting Concepts, reporoot docs) | board (`{{boardRepoName}}`) | `--repo {{boardRepoSlug}}` or run from the reporoot |
| `gh issue`, `gh api` (milestones, spec/ticket updates) | board (`{{boardRepoName}}`) | `--repo {{boardRepoSlug}}` or run from the reporoot |
| `gh pr` (view, create, review, merge) for **code** | workspace (`{{codeRepoName}}`) | `--repo {{codeRepoSlug}}` or run from inside `workspace/{{codeRepoName}}` |

## 3. Authoritative sources

Consult before searching the code:

- **Domain glossary:** [`CONTEXT.md`](../CONTEXT.md) — domain terminology and concepts.
- **Architecture:** [`ARCHITECTURE.md`](../ARCHITECTURE.md) — ADR/Concept indexes, high-level source structure, Codebase Structure.
<!-- Add project-specific authoritative docs here (service overviews, API contracts, config references), one bullet each, linked relative to this file. -->

## 4. Code-navigation policy

<!-- Optional section — keep only if workspace/{{codeRepoName}} has LSP/semantic-search/remote-lookup tooling available. Drop it otherwise. -->

Governs navigation within `workspace/{{codeRepoName}}` — the repo checked out locally. For a dependency not checked out locally, route to [**External repository queries**](#5-external-repository-queries) first.

Before searching code, check **Authoritative sources** for the relevant doc/contract and state which doc (if any) you checked — don't jump straight to grep/LSP for rename or reference-lookup tasks without noting this first.

Choose the tool by what you already know:

- **Exact symbol name, need an exact/refactoring operation** — use the **LSP** directly; semantic search and remote-lookup skills can't do this. LSP operations: **go to definition**, **find references**, **rename**, **hover**, **list file symbols**, **search symbols workspace-wide**, **go to implementation**, **incoming calls**, **outgoing calls**.
- **Know the concept/behavior, not the symbol name** — use **semantic search** first, scoped to `workspace/{{codeRepoName}}` to avoid matching docs/ADRs in the reporoot.
- **Semantic search unavailable/insufficient, or need the upstream default branch** (e.g. code not yet pulled locally) — fall back to a remote-lookup skill for `{{codeRepoSlug}}`, if one exists.

Use text search only for literals, configuration, generated files, or when the LSP is unavailable or can't answer the query.

## 5. External repository queries

<!-- Optional section — list any dependency/upstream repos not checked out anywhere in this workspace, and the skill that queries each one remotely. Drop this section if there are none. -->

| Dependency | Not checked out because | Query via |
| --- | --- | --- |
| `{{dependencyRepoSlug}}` | not cloned in this workspace | `{{dependencyQuerySkill}}` skill |

`{{codeRepoName}}` **is** checked out locally under `workspace/{{codeRepoName}}` — route its queries per [**Code-navigation policy**](#4-code-navigation-policy) instead.

## 6. Build and validation policy

- Follow `workspace/{{codeRepoName}}/README.md` for the full build command; run builds only from inside `workspace/{{codeRepoName}}`.
- Source under `workspace/` is git-ignored, but a root `.ignore` re-includes `/workspace/` so ripgrep-based search still finds source files there. MUST NOT remove that entry.

## 7. Documentation conventions

- MUST author all docs (`CONTEXT.md`, `ARCHITECTURE.md`, ADRs, Crosscutting Concepts) at the reporoot; MUST NOT author docs inside `workspace/`.
- MUST keep `CONTEXT.md` and `ARCHITECTURE.md` high-level — no implementation details, specs, or scratch notes.
- SHOULD cross-reference plans against code under `workspace/{{codeRepoName}}`.
- These docs, their templates, and their lazy-creation rules are owned by the `wf` plugin's `/manage-docs` skill — don't hand-author them outside it. Capture each resolved term, rule, Concept, or ADR the moment it crystallises — never batch documentation updates.

## 8. Skills

<!-- List repo-specific skills available here, one bullet each: `skill-name` — when to use it. Include any remote-lookup or recovery skills referenced in sections 4-5 above. -->

## 9. Tools

<!-- List CLIs, MCP servers, and other external tooling this repo's skills depend on. One row per tool, with a command/step to verify it's installed and authenticated. -->

| Tool | Purpose | Verify |
| --- | --- | --- |
| `gh` CLI | Ticket tracker (`/manage-backlog`), PRs | `gh auth status` |
| `{{cliToolName}}` (e.g. `aws`, `az`) | {{cliToolPurpose}} | `{{cliToolVerifyCommand}}` (e.g. `aws sts get-caller-identity`) |
| `{{mcpServerName}}` MCP server | {{mcpServerPurpose}} | Configured in `{{mcpConfigLocation}}` |

Before first use of a tool in a session, run its **Verify** command. If it fails, tell the user which tool is missing/unauthenticated instead of silently falling back or failing.
