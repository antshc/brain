# Copilot Instructions

## 1. Scope and repository topology

The reporoot itself plays the role of the **harness** for coding agents: context (`CONTEXT.md`, `ARCHITECTURE.md`), decisions (`docs/adr/`, `docs/concepts/`), agent conventions (`.crew/`, `.harness.env`), and the tool/action layer (`.github/skills/`, `.github/prompts/`, and the MCP servers/CLIs in [Tools](#8-tools)) all live here, while `workspace/` holds the subject the harness operates on.

This repo (the **reporoot**) is the **documentation/context repo**, not the codebase.

- **Docs & decisions live at the reporoot:** `CONTEXT.md` (domain glossary) and `ARCHITECTURE.md` (ADR/Concept indexes and the high-level source structure), with ADRs under `docs/adr/` (localized decisions) and Crosscutting Concepts under `docs/concepts/` (architectural backbone).
- **Source code ({{project}}) & git worktrees live in `workspace/`** (git-ignored by the reporoot). The source hierarchy is documented under **Codebase Structure** in `ARCHITECTURE.md`.

Within this file, resolve conflicts in this order: **safety and repository targeting → authoritative sources → navigation → build and validation → documentation conventions.** This ordering scopes only the rules in this file; it does not override `AGENTS.md`, path-scoped instructions, or user instructions. Avoid authoring rules that conflict across instruction files.

## 2. Safety and repository targeting

You MUST NOT introduce **code changes, build artifacts, or code PRs** into the `{{project-board}}` reporoot; all *code* work happens inside `workspace/{{project}}`, and you MUST NOT make code changes, run builds, or create worktrees anywhere else.

Authoring, committing, and opening PRs for docs (`CONTEXT.md`, `ARCHITECTURE.md`, ADRs, Crosscutting Concepts, and other reporoot docs) is allowed in `{{project-board}}`. You MUST NOT commit code or build output there.

Verify the target repo before any **code/build** `git`/`gh pr` command by checking `origin` exactly. Workspace code repo's `origin`: `{{codeRepoSlug}}`. Reporoot's `origin`: `{{boardRepoSlug}}`.

Runs unmodified on Linux, macOS, and Windows (no bash- or PowerShell-only syntax):

```
python -c 'import re,subprocess,sys; url=subprocess.run(["git","remote","get-url","origin"],capture_output=True,text=True,check=True).stdout.strip(); slug=re.sub(r"\.git$","",re.sub(r"^(git@github\.com:|https://github\.com/)","",url)); sys.exit(0 if slug=="{{codeRepoSlug}}" else 1)'
```

Also confirm the repo root for filesystem operations:

```bash
git rev-parse --show-toplevel
```

If `origin` is not exactly `{{repository}}/{{project}}` (e.g. `{{project-board}}` or any unrelated repo) and the action is a **code/build** action — **stop** and `cd` into `workspace/{{project}}` first. Documentation commits/PRs may proceed in `{{project-board}}`.

You MUST actually execute the check command above — not merely reference or reason about it — before the first `git`/`gh` code action in a session (including `git worktree add`), since this guard has previously been skipped when only stated in prose.

### Action → target repo

| Action | Target repo | How to target |
| --- | --- | --- |
| **Code** `git worktree add`, `git commit`, `git push`, code `gh pr create` | workspace (`{{project}}`) | `cd workspace/{{project}}` first |
| Code-modifying, build, test, package, and source-repository Git commands | workspace (`{{project}}`) | run from inside `workspace/{{project}}` |
| **Docs** `git commit`, `git push`, `gh pr create` (for `CONTEXT.md`, `ARCHITECTURE.md`, ADRs, Crosscutting Concepts, reporoot docs) | board (`{{project-board}}`) | `--repo {{repository-board}}/{{project-board}}` or run from the reporoot |
| `gh issue`, `gh api` (milestones, PRD/SPECS/ISSUE updates) | board (`{{project-board}}`) | `--repo {{repository-board}}/{{project-board}}` or run from the reporoot |
| `gh pr` (view, create, review, merge) for **code** | workspace (`{{project}}`) | `--repo {{repository}}/{{project}}` or run from inside `workspace/{{project}}` |

## 3. Authoritative sources

Consult these before searching the code:

- **Domain glossary:** [`CONTEXT.md`](../CONTEXT.md) — domain terminology and concepts.
- **Architecture:** [`ARCHITECTURE.md`](../ARCHITECTURE.md) — ADR/Concept indexes, high-level source structure, and Codebase Structure.
- **{{proejctName}} service overview:** [`{{proejctName}}-service.md`](../docs/services/{{proejctName}}-service.md) — {{proejctName}} service description and `main/src/` application-layer module map.
- **REST API/contracts:** [`{{proejctName}}-service.swagger.json`](../docs/services/{{proejctName}}-service.swagger.json) — request/response shapes, endpoint paths, status codes, schema definitions.
- **Support REST API/contracts:** [`support-service.swagger.json`](../docs/services/support-service.swagger.json) — request/response shapes, endpoint paths, status codes, schema definitions for the Support Service.
- **Configurations/tweaks:** [`{{proejctName}}-service.configuration-tweaks.md`](../docs/services/{{proejctName}}-service.configuration-tweaks.md) — available configurations/tweaks.
- **Code and Tests Conventions:** follow [CODE.md](../.crew/CODE.md) when writing or reviewing code or tests.

## 4. Navigation policy

### Step 1 — Route by target

{{proejctName}} (`{{project}}`) is the only codebase checked out locally; everything else is reached through a skill.

| Target | Where to look |
| --- | --- |
| {{proejctName}} source, tests, config | local `workspace/{{project}}` — continue to Step 2 |
| {{proj}} codebase | `search-{{proj}}` skill |
| `{{proejctPrefix}}.Infrastructure.*` / `{{proejctPrefix}}.Infra.Utils` source | `search-infra-nuget` skill |
| `AWSSDK.*` / `AWS.Logger.*` packages | `search-aws-sdk-nuget` skill |
| AWS service behavior, limits, quotas, APIs | `search-aws-docs` skill |
| Live AWS resource state | `query-aws` skill |
| Jira / Confluence | `preflight-atl` skill |

Each skill's frontmatter carries its full trigger conditions; do not restate them here.

### Step 2 — Read before you search

Consult the relevant [authoritative source](#3-authoritative-sources) first, and state which doc you checked (or that none applies) before running any search — do not jump straight to grep/LSP for rename or reference-lookup tasks. Use `ARCHITECTURE.md`'s Codebase Structure to resolve the owning area (`main/`, `support/`, `aws/`, `core/`, `gui/`) and scope every search to it.

### Step 3 — Pick the search tool

| You know | Use | If it fails |
| --- | --- | --- |
| The exact symbol, and need definition, references, rename, hover, implementations, or call hierarchy | **LSP** — semantic search cannot perform these | `lsp-recover` skill, then text search |
| The concept or behavior but not the symbol (e.g. "where is failover progress tracked?") | **Semantic search**, which is served by the Graphify graph — see the gate below | text search on domain terms from `CONTEXT.md` |
| A literal, configuration value, or generated file | **Text search** with `includePattern: workspace/{{project}}/**` | manual directory browsing under `workspace/{{project}}` |

Semantic results span both workspace roots: discard reporoot hits when the question is about code, and code hits when the question is about board documentation. Exclude `.artifacts/`, `**/bin/`, `**/obj/`, `TestResults/`, `graphify-out/`, and `bin/review_diff/` from text search.

**Graphify gate (applies to the semantic-search row):** Graphify backs semantic search here, so it is a discovery index — never an authoritative source. Before trusting a graph, run the health preflight and apply the corpus, exclusion, and degraded-mode rules in the `graphify` skill's `references/{{proejctName}}-workspace.md`. A code-only graph MUST NOT answer board-level architecture questions. Do not rebuild the graph unless the user asked for a build or update.

### Step 4 — Verify, then stop

Docs, contracts, ADRs, and graph results are leads, not proof: confirm behavior-specific conclusions against current source or tests. Stop searching once you can name the file and symbol that control the behavior — repeating a search is not verification.

## 5. Build and validation policy

- Follow `README.md` for the full build command; run builds only from inside `workspace/{{project}}`.
- The C# source under `workspace/` is git-ignored, but a root `.ignore` re-includes `/workspace/` so ripgrep-based search still finds `.cs` files. You MUST NOT remove that entry.

## 6. Documentation conventions

- You MUST author all docs (`CONTEXT.md`, `ARCHITECTURE.md`, ADRs, Crosscutting Concepts) at the reporoot, and MUST NOT author docs inside `workspace/`.
- You MUST keep `CONTEXT.md` and `ARCHITECTURE.md` high-level — no implementation details, specs, or scratch notes.
- You SHOULD cross-reference plans against code under `workspace/{{project}}`.

## 7. Skills

- You MUST create every skill under `.github/skills/<skill-name>/` at the reporoot — never in the user skills directory (`~/.copilot/skills/`) or inside `workspace/`. Each skill is its own folder holding `SKILL.md` plus any `reference/` files it needs.
- You MUST NOT reference a skill's own files via bare relative markdown links (e.g. `[memory.md](reference/memory.md)`); such links resolve against the runtime CWD (which may be a worktree, not the skill folder) and silently fail to load. Load reference files via the skill's stated absolute base directory instead.
### Available skills:
`preflight-atl`, `search-{{proj}}`, `search-infra-nuget`, `search-aws-sdk-nuget`, `search-aws-docs`, `lsp-recover`, `query-aws`, `graphify` — see each skill's own frontmatter `description` for full trigger conditions; do not restate them here.

## 8. Tools

- **AWS CLI** — configured; see the `query-aws` skill for profiles, account IDs, and usage. Always pass `--profile` explicitly and confirm before running any mutating command.
- **Atlassian Rovo MCP** — Jira/Confluence access; config read from `.atlassian`. See the `preflight-atl` skill for setup, confidentiality, and query-limit rules.
- **AWS Documentation MCP Server** (`aws-knowledge-mcp-server`) — read-only official AWS docs lookup; see the `search-aws-docs` skill.
- **`mmdc` (`@mermaid-js/mermaid-cli`)** — renders Mermaid diagrams (e.g. from docs) to images/SVG/PDF; installed globally via `npm install -g @mermaid-js/mermaid-cli`. Verify with `mmdc --version`.
