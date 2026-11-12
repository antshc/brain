# CodeGraphContext — SCIP indexing for C#/.NET and TypeScript

Researched: 2026-11-12  
Scope: [CodeGraphContext (CGC)](https://github.com/CodeGraphContext/CodeGraphContext), [scip-dotnet](https://github.com/sourcegraph/scip-dotnet), and [scip-typescript](https://github.com/sourcegraph/scip-typescript).  
Related research: [CGC multi-repository workspaces](https://github.com/antshc/brain/blob/research/cgc-multirepo/docs/research/cgc-multirepo.md).

## Question

Can CGC use SCIP to semantically index both a .NET/C# backend and a TypeScript frontend, store them in one graph, and let CGC's CLI/MCP search both languages?

## Verdict

**Yes for shared search, provided the projects can be indexed as separate non-overlapping roots.** CGC supports both external SCIP indexers, and multiple index operations can populate one *named context* (one graph database). **No for a single mixed-language SCIP indexing run in the current implementation:** CGC chooses one dominant language per indexed path and uses Tree-sitter to supplement the other files.

A shared database does **not** imply semantic cross-language edges (for example, a TypeScript HTTP client invoking a C# controller). SCIP indexes symbols and references in each language's compilation model; CGC has no confirmed automatic API-boundary mapping.

| Requirement | Status | Explanation |
| --- | --- | --- |
| C# symbols and references via SCIP | Supported | External `scip-dotnet`; needs a buildable/restorable solution or project |
| TypeScript/TSX symbols and references via SCIP | Supported | External `scip-typescript`; requires working TypeScript project configuration and dependencies |
| Both languages searchable through the same CGC MCP server | Supported by design | Use one named context and sequentially index separate paths |
| Both SCIP indexers invoked for one `cgc index <mixed-root>` | **Not supported** | Only one detected language is dispatched |
| Other language files included when indexing a mixed root | Supported with lower semantic precision | Supplementary Tree-sitter pass |
| Cross-repo symbol relationships | **Not established** | Separate indexing runs do not re-resolve calls between repositories |
| TypeScript-to-C# HTTP/RPC/API call edges | **Not supported automatically / unverified** | Requires endpoint/client mapping beyond per-language SCIP symbols |
| Performance and result precision on the user's workspace | **Untested** | Requires an experiment |

These are **source-inspection findings**, not the result of running indexers on a real mixed-stack repository.

## 1. How the current CGC implementation works

### 1.1 Single-language SCIP selection

In [`graph_builder.py`](https://github.com/CodeGraphContext/CodeGraphContext/blob/main/src/codegraphcontext/tools/graph_builder.py), `build_graph_from_path_async`:

1. Checks `SCIP_INDEXER=true`.
2. Reads `SCIP_LANGUAGES` as the set of eligible languages.
3. Calls `detect_project_lang(path, scip_languages)`.
4. Dispatches **one** `_build_graph_from_scip(..., detected_lang, ...)`.
5. Falls back to the Tree-sitter path when the selected indexer is unavailable or fails.

In [`scip_indexer.py`](https://github.com/CodeGraphContext/CodeGraphContext/blob/main/src/codegraphcontext/tools/scip_indexer.py), `detect_project_lang` counts supported file extensions under the requested path and returns the most frequent eligible language. It does **not** iterate over every detected language. Setting `SCIP_LANGUAGES=csharp,typescript` is therefore an **allowlist**, not a request to run both.

The [`scip_pipeline.py`](https://github.com/CodeGraphContext/CodeGraphContext/blob/main/src/codegraphcontext/tools/indexing/scip_pipeline.py) workflow executes the selected indexer, parses its `index.scip`, persists the symbols, then discovers files absent from the SCIP output and adds them using Tree-sitter. It resolves Tree-sitter calls and writes available SCIP call edges. Both languages may appear in the graph for a mixed root, but only the selected language gets that run's SCIP data.

**Consequence:** `cgc index ./full-stack-root` alone is not proof that both C# and TypeScript are indexed semantically via SCIP.

### 1.2 Project discovery and prerequisites

| Language | External indexer | CGC invocation/discovery | Important constraint |
| --- | --- | --- | --- |
| C# | `scip-dotnet` | First `*.sln` at indexed root; else first recursive `*.csproj`. Invokes `scip-dotnet index <solution-or-project> --working-directory <project-dir> --output <temp>/index.scip`. | Many solutions/projects under one root are **not** all selected automatically; CGC's discovery does not check `*.slnx`, although upstream scip-dotnet accepts that format |
| TypeScript/TSX | `scip-typescript` | `scip-typescript index --output <temp>/index.scip` from selected root | TypeScript project configuration and installed dependencies must resolve |
| TS monorepo | `scip-typescript` | Adds `--pnpm-workspaces` for `pnpm-workspace.yaml`, or `--yarn-workspaces` for `package.json` with `workspaces` | Run at a configured workspace root |
| JavaScript | `scip-typescript` | Detects `javascript` as a distinct dominant language; adds `--infer-tsconfig` if `tsconfig.json` is absent | Mixed TS/JS detection can select only one label despite one underlying indexer |

CGC's current source contains the relevant command construction in `ScipIndexer._build_command`. Upstream [scip-dotnet](https://github.com/sourcegraph/scip-dotnet/blob/main/ScipDotnet/Program.cs) directly supports one or more solution/project arguments; **CGC's wrapper is the restriction**, not necessarily the underlying indexer.

### 1.3 Shared graph context

[CGC's contexts guide](https://github.com/CodeGraphContext/CodeGraphContext/blob/main/docs/docs/guides/contexts.md) supports multiple paths in a single **named context**:

```bash
cgc context create mixed-stack
cgc context mode named
cgc index /workspace/backend --context mixed-stack
cgc index /workspace/frontend --context mixed-stack
```

CGC writes a `Repository` node per indexed path and merges `File` nodes by absolute path. Avoid indexing both a parent and its descendants into the same database, because overlapping file ownership and subsequent delete/rebuild behavior need verification.

A named context is a shared *database*, not automatic cross-index semantic resolution. The [previous multi-repo investigation](https://github.com/antshc/brain/blob/research/cgc-multirepo/docs/research/cgc-multirepo.md) found that symbol maps are built per index run rather than from all previously persisted repositories.

## 2. Recommended setup: two SCIP passes into one graph

Use this for non-overlapping language-specific project roots:

```text
/workspace/product/
├── backend/
│   ├── Product.sln
│   └── src/
└── frontend/
    ├── package.json
    ├── tsconfig.json
    └── src/
```

The two roots can be separate Git repositories, or separate subdirectories of one repository. CGC treats each index root as its own logical repository node.

### 2.1 Prerequisites

- Python compatible with the installed CGC release; preferably Python 3.12+ on Linux if using FalkorDB Lite.
- .NET SDK/MSBuild compatible with the solution, including configured NuGet feeds, workloads, and restore credentials.
- Node.js and the frontend project's package manager, lockfile, TypeScript config, and dependencies.
- Compatible CGC graph database. An embedded backend is sufficient for a local proof of concept, but **avoid simultaneous writers** against one embedded database.

Install:

```bash
python -m pip install -U codegraphcontext
dotnet tool install --global scip-dotnet
npm install -g @sourcegraph/scip-typescript

# Ensure ~/.dotnet/tools is on PATH (may require a new shell).
scip-dotnet --version
scip-typescript --version
cgc setup-scip
```

Use a pinned CGC/indexer version for reproducible testing. In production/CI, prefer a virtual environment or `pipx` and version-pinned tool installations.

### 2.2 Restore and configure

```bash
dotnet restore /workspace/product/backend/Product.sln
cd /workspace/product/frontend
npm ci                 # or pnpm install --frozen-lockfile / yarn --immutable

cgc context create mixed-stack
cgc context mode named
cgc config set SCIP_INDEXER true
cgc config set SCIP_LANGUAGES csharp,typescript
cgc config set SCIP_LOCAL_INDEXER_TIMEOUT_SECONDS 900
```

`SCIP_LOCAL_INDEXER_TIMEOUT_SECONDS` is relevant for the local SCIP subprocess; `900` is a **suggested starting value**, not a benchmark-derived requirement. CGC defaults to 300 seconds.

For C# output, place a deterministic intended `*.sln` directly at the selected root. If that isn't possible, use a root with a single intended `*.csproj`, or adjust CGC discovery. If the solution uses `*.slnx` only, CGC currently needs modification or another supported project entrypoint.

### 2.3 Index sequentially

```bash
cgc index /workspace/product/backend  --context mixed-stack
cgc index /workspace/product/frontend --context mixed-stack

cgc list
cgc stats
```

Do **not** run both commands concurrently on an embedded single-process DB. For a reindex:

```bash
cgc index /workspace/product/backend --force --context mixed-stack
```

`--force` removes and rebuilds that indexed root. Verify it leaves the frontend untouched. Plain `cgc index` may skip an apparently completed previous index, so an existing graph is not proof that the SCIP configuration has just been applied.

Inspect command output to confirm **both** messages appeared, in their respective runs:

```text
SCIP_INDEXER=true — using SCIP for language: csharp
SCIP_INDEXER=true — using SCIP for language: typescript
```

Also check for warnings about missing indexers, failed restore, absent SCIP output, or fallback to Tree-sitter. The installed tools and their appearance in `cgc setup-scip` are **necessary but insufficient** to prove successful semantic indexing.

### 2.4 CGC search through MCP

Run `cgc mcp setup` and configure the MCP client to start `cgc mcp start` with access to the **same named context/database**. A single MCP server session queries the active database, so both indexed roots can be searched through CGC's `find_code`, `analyze_code_relationships`, and read-only Cypher tools. Use a context selection or saved default appropriate for the MCP server's working directory; its own context resolution may differ from the prior CLI's explicit `--context`.

For MCP indexing calls, ensure both root paths are permitted by the CGC path sandbox (`CGC_ALLOWED_ROOTS` or server working directory). Search the full shared graph without a `repo_path` filter, or filter to one indexed root for narrower results.

## 3. Verification experiment

**Goal:** distinguish *two languages present* from *two languages semantically indexed with SCIP*.

### 3.1 Verify counts and coverage

Run with the shared context:

```bash
cgc query "MATCH (f:File)
RETURN f.language AS language, count(f) AS files" --context mixed-stack

cgc query "MATCH (f:Function)
RETURN f.lang AS language, count(f) AS functions" --context mixed-stack
```

The function-language property may depend on parser/model version; if empty, inspect function properties and file relationships rather than interpreting `null` as no coverage.

Check representative symbols by name and path in both roots, e.g. one C# service method and one TS application function, using `find_code` or Cypher.

### 3.2 Verify SCIP-derived relations

```bash
cgc query "MATCH ()-[r:CALLS]->()
WHERE r.source = 'scip'
RETURN count(r) AS scip_calls" --context mixed-stack
```

The combined count does not establish correctness for *each* language. Check at least two known nontrivial C# calls and two TS calls, resolving caller file, callee file, and target definition. Inspect returned edge metadata and make sure these are genuine SCIP relationships instead of inferred or ambiguous Tree-sitter links.

Recommended acceptance checklist:

- [ ] C# indexer completed and its SCIP data was written.
- [ ] TS indexer completed and its SCIP data was written.
- [ ] File/function counts cover the expected source sets, excluding generated and vendor files.
- [ ] `find_code` retrieves distinct known symbols from each language via one MCP session.
- [ ] Representative intra-language `CALLS` and inheritance/reference relationships match actual code.
- [ ] `--force` rebuild of backend preserves frontend data, and vice versa.
- [ ] No duplicate files/symbols arise from overlapping root choices.
- [ ] Index wall-clock time, peak RSS, and DB size are recorded.
- [ ] Remaining cross-repo and cross-language links are explicitly classified as verified, absent, or unknown.

Record evidence as command/log, observed graph query, and selected symbol paths. Do not infer quality solely from node totals.

## 4. Alternative layouts and limits

### A. Separate Git repositories (best fit for current CGC)

Index each repo or suitable project subfolder into one named context. **Works for unified search**, but cross-repo `CALLS` edges are not guaranteed because CGC builds resolution state per run.

### B. One Git repo with distinct `backend/` and `frontend/`

Same approach. This creates separate logical CGC repository nodes for those two paths, even though they share a Git root. Avoid also indexing the parent as a third overlapping root.

### C. One mixed root with interleaved C# and TS

Unmodified CGC chooses **one** SCIP language and supplements the rest with Tree-sitter. If both languages must have SCIP precision, prefer refactoring indexing scopes to non-overlapping roots or **enhancing CGC** to dispatch both indexers and aggregate their outputs before graph write.

### D. Multiple .NET solutions

CGC's `_find_csharp_project` selects the first direct `*.sln`, then the first recursive `*.csproj`. Options: a valid aggregate solution at the indexing root, disjoint solution-specific scopes, or improving the wrapper to accept explicit project/solution lists. Verify no overlap and no missing projects.

### E. Cross-language frontend → backend links

SCIP alone does not turn HTTP paths, REST client generation, or RPC names into C# `CALLS` edges. For this feature, add a separate API-contract model (route + verb + schema/client binding) and verified mapping to controller/handler symbols. This is a distinct research and implementation task.

## 5. If CGC must support both SCIP languages in one run

Proposed **CGC change**, not an existing option:

1. Discover every eligible language, and the corresponding concrete project/indexer scope.
2. Run `scip-dotnet` and `scip-typescript` for those scopes with separate temporary `index.scip` outputs; avoid concurrently writing to the graph.
3. Parse each SCIP index, normalize all paths to a single indexing root, and merge by file + symbol identity (not by name alone).
4. Run one Tree-sitter supplement only for files absent from all SCIP outputs.
5. Persist one repository/file hierarchy and write all SCIP call edges and other verified relations.
6. Handle per-indexer errors explicitly: record which languages fell back, rather than silently labeling the entire run SCIP-successful.
7. Test collision handling, same file indexed twice, cross-root references, full rebuild/deletion, watcher behavior, and mixed TS/JS workspaces.

Potential integration points: `graph_builder.py` (dispatch), `scip_indexer.py` (project selection and external CLI), `scip_pipeline.py` (aggregating parsed outputs), `persistence/writer.py` (deduplication and edge writing).

## 6. Remaining risks and open questions

1. **Search correctness:** Are known symbols and `CALLS` edges retrieved with accurate file/line identities in both language graphs?
2. **Semantic coverage:** How many expected functions/calls are represented by SCIP rather than Tree-sitter? Are fallback warnings visible?
3. **Lifecycle:** What happens when just one of two indexed roots is force-reindexed, deleted, or watched?
4. **Project selection:** Does the existing .NET solution encompass all desired projects and project references? How are `*.slnx` and multi-solution workspaces handled?
5. **Monorepos:** Does the configured pnpm/yarn workspace indexing cover all intended TypeScript packages without unresolved imports?
6. **Cross-repository/cross-language edges:** Which relationships actually exist, and which require separate linkers?
7. **Scale:** What is indexing time, memory, DB footprint, and the cost of frequent full rebuilds?
8. **File ownership:** How does CGC handle shared files or package references when two index roots overlap?

**Recommended next action:** Run the two-root proof of concept against a real C# solution and TypeScript frontend. Only implement multi-language single-run dispatch if the project layout cannot be cleanly partitioned or the acceptance tests reveal a real accuracy gap.

## Sources

Primary code inspected from the CodeGraphContext default branch on 2026-11-12:

1. [CGC graph builder: SCIP language dispatch](https://github.com/CodeGraphContext/CodeGraphContext/blob/main/src/codegraphcontext/tools/graph_builder.py)
2. [CGC SCIP indexer: language detection, indexer command construction, C# project selection](https://github.com/CodeGraphContext/CodeGraphContext/blob/main/src/codegraphcontext/tools/scip_indexer.py)
3. [CGC SCIP indexing pipeline: supplement and relationship writing](https://github.com/CodeGraphContext/CodeGraphContext/blob/main/src/codegraphcontext/tools/indexing/scip_pipeline.py)
4. [CGC persistence writer: Repository/File merge and SCIP call edges](https://github.com/CodeGraphContext/CodeGraphContext/blob/main/src/codegraphcontext/tools/indexing/persistence/writer.py)
5. [CGC config: SCIP flags, language list, timeout](https://github.com/CodeGraphContext/CodeGraphContext/blob/main/src/codegraphcontext/cli/config_manager.py)
6. [CGC CLI: index, force, context and query](https://github.com/CodeGraphContext/CodeGraphContext/blob/main/src/codegraphcontext/cli/main.py)
7. [CGC contexts and named workspaces](https://github.com/CodeGraphContext/CodeGraphContext/blob/main/docs/docs/guides/contexts.md)
8. [Sourcegraph scip-dotnet README](https://github.com/sourcegraph/scip-dotnet/blob/main/readme.md)
9. [Sourcegraph scip-dotnet CLI implementation](https://github.com/sourcegraph/scip-dotnet/blob/main/ScipDotnet/Program.cs)
10. [Sourcegraph scip-typescript](https://github.com/sourcegraph/scip-typescript)
11. [Existing CGC multi-repo research](https://github.com/antshc/brain/blob/research/cgc-multirepo/docs/research/cgc-multirepo.md)
