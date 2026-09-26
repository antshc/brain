# CodeGraphContext — multi-repo workspace support

Researched 2026-09-26 against `CodeGraphContext/CodeGraphContext@a864a9f` (main, 2026-09-24) and PyPI `codegraphcontext` 0.6.13 (2026-09-06). Line references point at that commit.

**Verdict**

- CGC has no multi-repo workspace concept. You index each path separately with `cgc index <path>`, and the resulting graphs go into one database. The context mode picks the database: `global` (one DB for everything), `named` (one DB per named context, can hold many repos), or `per-repo` (a `.codegraphcontext/` DB inside each repo).
- Cross-repo `CALLS`/`INHERITS` edges only resolve between files parsed in the same index run. The symbol map is rebuilt from the files of the current path on every run. Repos indexed separately share a DB but get no links between their symbols.
- If you index `<harness>` as a single path, you get cross-repo edges, but the whole harness becomes one `Repository` node. Only the harness `.gitignore` is applied. That file usually ignores `workspace/`, so you would need a `.cgcignore` with `!workspace/` to index the repos at all.
- Setup needs no service, Docker, or LLM (embedded FalkorDB Lite, KuzuDB, or LadybugDB). Re-indexing a repo from the CLI is a full delete-and-rebuild. Only the file watcher updates incrementally.

## 1. One graph vs one graph per repo

- **Three context modes** control where the graph DB lives: `global` (default; "all indexed repositories populate a single shared database"), `per-repo` (each repo gets its own `.codegraphcontext/` DB, "completely isolated"), and `named` (a logical workspace that several codebases are indexed into) [4 §Context Modes; 15 L840-L860].
- **Each index call writes one `Repository` node**, `MERGE (r:Repository {path: $path})`, for the path given. Its files hang off it via `CONTAINS` [10 L114-L116; 26 L278-L300; 7 §1].
- **Symbol resolution is limited to one run.** `imports_map = pre_scan_for_imports(files, …)` is built only from the files found under the current path [10 L118-L125]. When a call can't be resolved in that map, it falls back to the caller's own file (tier 9, labelled `AMBIGUOUS`) or is skipped. It never looks up symbols already in the DB from other repos [11 L1527-L1564; 11 L44-L50].
- **Cross-repo relationships:** the source has no cross-repo linking logic; grepping for `cross_repo`/`cross-repo` finds nothing. The docs claim global mode "enables cross-project relationship tracing" [4 §Global Mode]. The source shows only a shared DB, where you can write Cypher that joins across `Repository` nodes; it does not create call edges between repos. Treat the docs claim as unverified beyond that.
- **Shared packages:** `cgc add-package <name> <lang>` / MCP `add_package_to_graph` index an installed package as a `Repository` with `is_dependency=true` [5 §2; 8 §Indexing]. That is its own index run, so calls from your repos into it are not re-resolved (inferred from [10], [11]).
- **Named graphs (FalkorDB only):** MCP tools accept an optional `graph_name`. The FalkorDB backends honour it as a separate graph per repo. KuzuDB, LadybugDB, and Neo4j reject it with an error (fixed in #1558) [19 L4-L7; 20 L22-L45; 29; 28 L157-L176]. `list_graphs` lists FalkorDB graphs [19 L389-L396].
- **Bundles:** "Multi-repository bundles" is still an unchecked roadmap item [docs/docs/guides/bundles.md L459, in 1's repo].

## 2. How CGC is told where repositories live

- **No workspace manifest.** Nothing lists repos declaratively. Each repo is added imperatively:
  - CLI: `cgc index [PATH] [--force] [--context NAME]` [17 L1689-L1700].
  - MCP: `add_code_to_graph(repo_path, is_dependency)` and `watch_directory(path)` [8 §Indexing, §Monitoring].
- **Global config file:** `~/.codegraphcontext/config.yaml` (YAML). Keys [15 L840-L860, L948-L975; 15 L1331-L1407]:
  - `version`, `mode` (`global|per-repo|named`), `default_context`
  - `contexts.<name>.{database, db_path, repos[], cgcignore_path}`
  - `workspace_mappings.<cwd>` → `{context_path, database}`
- **Settings and credentials:** `~/.codegraphcontext/.env`. Set via `cgc config set KEY VALUE` [6; 1 §MCP Server Mode]. Relevant keys:
  - `DEFAULT_DATABASE`, `IGNORE_DIRS`, `MAX_FILE_SIZE_MB` (10), `PARALLEL_WORKERS` (4)
  - `SCIP_INDEXER`, `SKIP_EXTERNAL_RESOLUTION`, `ENABLE_AUTO_WATCH`
  - Defaults are listed at [15 L90-L140].
- **Per-repo config:** `<repo>/.codegraphcontext/config.yaml` with key `database`. It is auto-created on first index in `per-repo` mode, which also copies the global `.env` into it [15 L1054-L1081].
- **Which DB a command uses** is resolved in this order [15 L1019-L1158; 4 §Context Resolution Precedence]:
  1. `--context`/`-c` flag
  2. `.codegraphcontext/` in the **current directory only** (no upward walk) [15 L1000-L1016]
  3. `config.yaml` mode/default
  4. global fallback
- **Named contexts:**
  - `cgc context create NAME [--database kuzudb] [--db-path P]`
  - `cgc context mode named`, `cgc context default NAME`, `cgc context list|delete` [4 §Managing Named Contexts; 17 L233-L291]
  - Indexing with `--context NAME` records the repo path under `contexts.NAME.repos` [16 L344-L358].
- **Directory discovery (MCP only):** at startup, if the server cwd has no DB, it scans child dirs one level deep for `.codegraphcontext/` folders. It then adds a note to the next tool result telling the agent to call `switch_context` [18 L203-L225, L760-L775].
  - `discover_codegraph_contexts(path, max_depth=1)` does a deeper scan [15 L1277-L1324].
  - `switch_context(context_path, save=true)` points the session at one DB and saves the choice under `workspace_mappings` [8 §Context management; 18 L693].
  - One MCP session serves one DB at a time.
- **MCP path sandbox:** index, watch, bundle, and context tools only accept paths under the server cwd or `CGC_ALLOWED_ROOTS` (`:`-separated). `CGC_ALLOW_ALL_PATHS=true` or `CGC_ALLOWED_ROOTS=*` disables the check [8 §Path sandbox; 20 L50-L59].
- **Ignore mechanisms.** Patterns are layered defaults → `.gitignore` → `.cgcignore`, last match wins [13 L264-L313; 9 §Indexing]:
  - Built-in defaults include `node_modules/`, `dist/`, `build/`, `target/`, `out/`, `obj/`, `.git/` [14 L8-L23]. `bin/` is **not** ignored by default [9 §.NET].
  - `.gitignore`: only the **nearest one**, searched upward from the indexed path, stopping at the enclosing git worktree [13 L67-L90].
  - `.cgcignore`: the nearest one, same upward search bounded to the git root. If none is found, CGC **creates** `<indexed path>/.cgcignore` with defaults, i.e. it writes into your repo [13 L32-L65, L275-L278].
  - `IGNORE_DIRS`: comma-separated directory names pruned at any depth [12 L117-L122; 15 L109].
  - The docs describe context-level `.cgcignore` paths (`~/.codegraphcontext/global/.cgcignore`, `contexts/<name>/.cgcignore`) [4 §Ingest Ignore]. In code, these are passed as an extra "explicit" file merged on top of the repo-local one [13 L264-L290].
  - Consequence for `<harness>`: indexing the harness root reads only `<harness>/.gitignore`. The nested `workspace/<repo>/.gitignore` files are not read, and a harness `.gitignore` that ignores `/workspace` excludes all the repos (inferred from [13 L67-L90, L312]).

## 3. Graph database backends

| Backend | Type | Setup | Notes |
|---|---|---|---|
| FalkorDB Lite (`falkordblite`) | embedded, in-memory, Unix socket | none | Default on Linux/macOS with Python ≥ 3.12. RAM-bounded. Stored at `~/.codegraphcontext/global/db/falkordb/` [4 §Workspace Directory Structure; 6 §3; 3] |
| KuzuDB (`kuzu`) | embedded | none | Fallback where FalkorDB Lite can't load. Upstream archived 2025-10-10 [3; 9 §Which backend]. Single-process lock [9 §Databases] |
| LadybugDB (`ladybug`) | embedded (Kùzu fork) | none | Buffer pool defaults to 4 GiB (`CGC_EMBEDDED_BUFFER_POOL_MB`) [1 §Database Options; 9] |
| FalkorDB Remote (`falkordb`) | client | Docker/server | `FALKORDB_HOST`, `FALKORDB_PORT`. `docker compose --profile falkordb up -d` [6 §3; 1 §Docker] |
| Neo4j | client | Docker/Aura | `docker run … -e NEO4J_AUTH=neo4j/password neo4j:latest`, then `cgc config db neo4j` plus `NEO4J_URI`, `NEO4J_USERNAME`, `NEO4J_PASSWORD`, or run `cgc neo4j setup` [6 §4] |
| Nornic DB | Bolt client | server | `NORNIC_URI`, `NORNIC_USERNAME`, `NORNIC_PASSWORD` [6 §5] |

- Select a backend with `cgc config db <neo4j|falkordb|falkordb-remote|kuzudb|nornic|ladybugdb>` [15 L236; 17 L587]. Check which one is active with `cgc config show` [9].
- The embedded DBs are single-process. If an MCP server or watcher already has the DB open, a concurrent CLI command fails with "Could not set lock on file" [9 §Databases].

## 4. Regeneration

- **`cgc index PATH`** skips the repo if its `File` count in the graph is at least what discovery expects ("already indexed … Skipping") [16 L359-L384; 9 §Indexing].
- **`cgc index --force` and `cgc update`** both call `reindex_helper`: delete the repo from the graph, then run a full rebuild [16 L886-L946; 17 L1754-L1768].
  - The docs say CGC "tracks modification timestamps and file hashes to perform incremental scans" [5 L27-L28]. This was **not confirmed in source**: the CLI paths are skip, full, or delete+full.
- **Git hooks:** `cgc hook install` installs `post-commit` and `post-checkout` hooks that run `cgc update --quiet`, i.e. a full re-index of that repo on every commit or checkout [25 L12; 17 L1754-L1766].
- **File watching** (`watchdog`) is incremental per file [21 L37-L63, L199-L315; 5 §4; 8 §Monitoring]:
  - Commands: `cgc watch [PATH] [--sync-on-start]`, `cgc watching`, `cgc unwatch PATH`; MCP `watch_directory`, `list_watched_paths`, `unwatch_directory`.
  - 2 s debounce per path. It keeps an in-memory `imports_map`, re-parses the changed file, and re-links calls and inheritance for the affected subset.
  - The watcher runs inside the process that started it; the CLI `watch` blocks the terminal [16 L428-L437].
  - Changes made while no watcher was running are missed unless you pass `--sync-on-start` [5 §4; 17 L2031-L2049].
- **Cost/time:** no official benchmarks were found for indexing time or size. Documented cost figures for optional phases:
  - `ENABLE_INHERIT_RESOLVE`: "~1-5 min per 50K functions".
  - `ENABLE_VECTOR_RESOLVE`: "~15 min per 50K functions on CPU", Neo4j only, needs `fastembed` [15 L176-L195].
  - SCIP subprocess timeout defaults to 300 s (`SCIP_LOCAL_INDEXER_TIMEOUT_SECONDS`) [15 L114, L170].
- **LLM/API key:** not needed for indexing or queries. Only the optional embeddings phase can use OpenAI (`CGC_EMBEDDING_MODEL=openai` + `OPENAI_API_KEY`); the default is local fastembed or sentence-transformers [24 L15-L19; 15 L196-L201, L128]. `OPENAI_MODEL`/`ANTHROPIC_MODEL` are defined as config keys but not referenced anywhere else in the source (grep).

## 5. Query surface

- **MCP tools.** 30 are defined in code [19; 18 L733-L763]. `docs/MCP_TOOLS.md` still says 0.4.16 with 25 tools [8]:
  - Context: `discover_codegraph_contexts`, `switch_context`, `list_graphs`
  - Indexing: `add_code_to_graph`, `add_package_to_graph`, `list_indexed_repositories`, `delete_repository`, `get_repository_stats`
  - Search and analysis: `find_code`, `analyze_code_relationships` (callers, callees, imports, hierarchy, …), `find_dead_code`, `calculate_cyclomatic_complexity`, `find_most_complex_functions`
  - Watching: `watch_directory`, `list_watched_paths`, `unwatch_directory`
  - Jobs: `list_jobs`, `check_job_status`
  - Cypher: `execute_cypher_query` (read-only), `visualize_graph_query`
  - Bundles: `load_bundle`, `search_registry_bundles`
  - Other: `generate_report`, `find_java_spring_endpoints`, `find_java_spring_beans`, `find_datasource_nodes`, `simulate_metrics`, `simulate_architectural_change`, `analyze_architectural_evolution`
  - Most query tools accept an optional `repo_path` filter (`path STARTS WITH`) [8; 30]. Tools can be disabled per project via `<cwd>/mcp.json` `disabledTools` [18 L278-L317, L712-L713].
- **CLI** [17]:
  - Indexing and management: `index`, `update`, `list`, `stats`, `delete [--all]`, `clean`, `add-package`, `watch`, `watching`, `unwatch`
  - Search: `find name|pattern|type|variable|content|decorator|argument`
  - Analysis: `analyze calls|callers|chain|deps|tree|complexity|dead-code|overrides|variable`
  - Other: `query "<cypher>"` (read-only), `report`, `visualize`, `diagram`, `bundle …`, `context …`, `config …`, `mcp setup|start|tools`, `api start`, `doctor`, `setup-scip`
- **Cypher:** read-only, enforced by `is_read_only_cypher`. Neo4j and FalkorDB also open READ sessions [16 `cypher_helper`]. The same graph model is used on all backends [8 §Advanced querying].
- **Graph model** [7]:
  - Nodes: `Repository`, `File`, `Module`, `Class`, `Function`, plus framework and datasource nodes.
  - Edges: `CONTAINS`, `IMPORTS`, `CALLS`, `INHERITS`, `IMPLEMENTS`, `MAPS_TO`, `READS`, `WRITES`.
  - CALLS edges carry a confidence label: `EXTRACTED`, `INFERRED`, or `AMBIGUOUS` [11 L44-L50].
- **Output formats:**
  - MCP returns JSON with the workspace path prefix stripped [18 L79-L87, L857]. Opt-in GCF instead: `CGC_OUTPUT_FORMAT=gcf` plus `pip install gcf-python`; falls back to JSON otherwise [1 §GCF; 34].
  - CLI `query` prints JSON [16 `cypher_helper`]. `--viz` and `visualize` produce HTML or a local web UI [1].
  - Response size caps: `MAX_TOOL_RESPONSE_TOKENS`, `MAX_PROMPT_CHARS`, `TOOL_RESULT_LIMITS` [15 L116-L124].

## 6. Install and runtime prerequisites

- Package: `codegraphcontext` on PyPI. Latest is 0.6.13 (2026-09-06), MIT, `requires_python >=3.10`, classifiers 3.10–3.14 [2; 3].
  - The GitHub "Latest release" is v0.5.7 and README "Project Details" says 0.5.1, so the docs lag PyPI [1; 33].
- Install: `pip install codegraphcontext` [1 §Installation & Quick Start].
  - If the command isn't found afterwards, the README suggests `curl -sSL https://raw.githubusercontent.com/CodeGraphContext/CodeGraphContext/main/scripts/post_install_fix.sh | bash` (not recommended without reviewing the script).
  - pipx variant for MCP: `pipx run codegraphcontext mcp start` [1 §MCP Client Configuration].
  - Docker: `docker run --rm -v "$(pwd):/workspace" codegraphcontext/codegraphcontext cgc index .` [1 §Docker].
- CLI entry points: `cgc` and `codegraphcontext` [1].
- MCP setup: `cgc mcp setup`. The wizard writes `./mcp.json` and `~/.codegraphcontext/.env`, and edits your IDE's settings file. Then `cgc mcp start` [1 §MCP Server Mode].
- Core dependencies [3]:
  - `tree-sitter>=0.24,<0.26`, `tree-sitter-language-pack>=1.6,<2`, `tree-sitter-c-sharp>=0.21`
  - `neo4j>=5.15`, `falkordb>=1,<1.6`, `falkordblite>=0.7,<0.10` (non-Windows, Python ≥ 3.12), `redis>=5,<6`
  - `kuzu`, `ladybug>=0.19,<0.20`, `mcp>=1,<2`
  - `watchdog`, `typer`, `rich`, `fastapi`, `uvicorn`, `pathspec`, `protobuf>=3.20,<3.21`
  - Extras: `parsing`, `falkordb-embedded`, `falkordb-remote`, `kuzu`, `ladybug`, `neo4j`, `gcf`, `dev`, `datasources` [2].
- Optional SCIP indexers are external binaries. Enable with `SCIP_INDEXER=true`; `cgc setup-scip` audits which are installed [22 L20-L37, L74; 17 L1800-L1808]:
  - C#: `dotnet tool install --global scip-dotnet`
  - TS/JS: `npm install -g @sourcegraph/scip-typescript`

## 7. Language support and known limits (C#/.NET, TS/JS, scale)

- 23 languages are listed, including C#, TypeScript, JavaScript, and TSX. The parser is Tree-sitter by default, with optional SCIP [1 §Supported Programming Languages].
- **C#** (Tree-sitter):
  - Namespace is extracted by regex as the package name. `using` directives and aliases are parsed [src/codegraphcontext/tools/languages/csharp.py L130-L132, L378-L383].
  - Partial types are tracked (`is_partial`, `PARTIAL_OF` links) [same file L353; 10 L281].
  - `obj/` is ignored by default since 0.6.1; add `bin/` to `.cgcignore` yourself [9 §.NET].
  - `ENABLE_INHERIT_RESOLVE` is recommended for C# codebases that use interfaces or DI [15 L176-L183].
- **C# via SCIP (scip-dotnet)** needs a restorable `.sln`/`.csproj` [1 §SCIP]. `_find_csharp_project` takes the **first** `*.sln` directly in the indexed root, otherwise the first `*.csproj` found recursively [22 L384-L391]. Two consequences:
  - Indexing a multi-solution harness root would feed SCIP a single project.
  - SCIP runs for **one dominant language per indexed path**, chosen by file count [22 L118-L140; 23 L606-L640]. Other files get a Tree-sitter supplement [27 L205-L245]; whether their calls are resolved is unverified.
- **TS/JS:**
  - The Tree-sitter TS parser extracts type aliases. No `tsconfig.json` `paths`/`baseUrl` alias handling was found (grep of `languages/typescript.py`, `javascript.py`); unverified whether aliased imports resolve.
  - SCIP TS supports yarn/npm workspaces via `--yarn-workspaces`, and `--infer-tsconfig` for JS-only projects [22 L33-L37, L143-L155].
  - Name collisions: the docs advise path-qualified Cypher "in monorepos that also contain TypeScript mirrors" [32 L174].
- **Known issues relevant to large or multi-repo setups** [9; 30; 31; 29]:
  - Embedded DB single-process lock (#1683).
  - LadybugDB buffer-pool OOM.
  - `repo_path` filter used to resolve against the server cwd and silently return 0 results; fixed (#1633).
  - `ENABLE_VECTOR_RESOLVE` was a silent no-op on a 123k-function repo; fixed (#1597).
  - `graph_name` was silently ignored by `add_code_to_graph`; fixed (#1558).
  - Still open: intermittent missing `CONTAINS` edges on LadybugDB (#1730).
  - `SKIP_EXTERNAL_RESOLUTION=true` is recommended for large enterprise codebases [15 L115, L171].
  - The project is "Development Status :: 3 - Alpha" [3].

## Open questions for the experiment

1. With `<harness>` indexed as one path, a `.cgcignore` of `!workspace/`, and the harness `.gitignore` ignoring `/workspace`: does `workspace/<repo>` actually get indexed, and are nested `node_modules`, `bin`, and `obj` excluded without per-repo `.gitignore`s?
2. Do cross-repo `CALLS`/`INHERITS` edges appear between C# repos (e.g. a shared NuGet-style library repo) and between TS repos when indexed as one path? What share of them is labelled `AMBIGUOUS` vs `EXTRACTED`?
3. In global mode, if you index `<harness>` and also `workspace/<repoA>` separately, are `File`/`Function` nodes shared (MERGE on absolute path) or duplicated? Does `delete_repository` on one remove nodes the other still needs?
4. Wall-clock time, peak RAM, and DB size for a full index of the real workspace on FalkorDB Lite vs KuzuDB. How long does the `--force` full rebuild take (it is the only CLI refresh)?
5. Does one MCP server started at `<harness>` with a single global or named DB answer `analyze_code_relationships` across repos? Does `repo_path` filtering work per sub-repo when the `Repository` node is the harness?
6. With `SCIP_INDEXER=true` on the harness root: which language wins, which `.sln` is picked, and does the rest fall back cleanly to Tree-sitter?
7. Does the watcher on `<harness>` keep up with edits across several repos, and does it respect the `.cgcignore` negations?
8. Does the auto-created `.cgcignore` (and in per-repo mode, the copied `.env`) end up as unwanted untracked files in each repo?

## Sources

1. README — https://github.com/CodeGraphContext/CodeGraphContext/blob/a864a9f9097c0ff820c5fa8611f4056799dde8fe/README.md
2. PyPI — https://pypi.org/project/codegraphcontext/ (metadata: https://pypi.org/pypi/codegraphcontext/json)
3. pyproject.toml — https://github.com/CodeGraphContext/CodeGraphContext/blob/a864a9f9097c0ff820c5fa8611f4056799dde8fe/pyproject.toml
4. Contexts guide — https://github.com/CodeGraphContext/CodeGraphContext/blob/a864a9f9097c0ff820c5fa8611f4056799dde8fe/docs/docs/guides/contexts.md
5. Indexing guide — https://github.com/CodeGraphContext/CodeGraphContext/blob/a864a9f9097c0ff820c5fa8611f4056799dde8fe/docs/docs/guides/indexing.md
6. Backends — https://github.com/CodeGraphContext/CodeGraphContext/blob/a864a9f9097c0ff820c5fa8611f4056799dde8fe/docs/docs/concepts/backends.md
7. Graph model — https://github.com/CodeGraphContext/CodeGraphContext/blob/a864a9f9097c0ff820c5fa8611f4056799dde8fe/docs/docs/concepts/graph-model.md
8. MCP tools reference — https://github.com/CodeGraphContext/CodeGraphContext/blob/a864a9f9097c0ff820c5fa8611f4056799dde8fe/docs/MCP_TOOLS.md
9. Troubleshooting — https://github.com/CodeGraphContext/CodeGraphContext/blob/a864a9f9097c0ff820c5fa8611f4056799dde8fe/docs/TROUBLESHOOTING.md
10. Tree-sitter pipeline — https://github.com/CodeGraphContext/CodeGraphContext/blob/a864a9f9097c0ff820c5fa8611f4056799dde8fe/src/codegraphcontext/tools/indexing/pipeline.py
11. Call resolution — https://github.com/CodeGraphContext/CodeGraphContext/blob/a864a9f9097c0ff820c5fa8611f4056799dde8fe/src/codegraphcontext/tools/indexing/resolution/calls.py
12. File discovery — https://github.com/CodeGraphContext/CodeGraphContext/blob/a864a9f9097c0ff820c5fa8611f4056799dde8fe/src/codegraphcontext/tools/indexing/discovery.py
13. Ignore handling — https://github.com/CodeGraphContext/CodeGraphContext/blob/a864a9f9097c0ff820c5fa8611f4056799dde8fe/src/codegraphcontext/core/cgcignore.py
14. Default ignore patterns — https://github.com/CodeGraphContext/CodeGraphContext/blob/a864a9f9097c0ff820c5fa8611f4056799dde8fe/src/codegraphcontext/tools/indexing/constants.py
15. Config manager — https://github.com/CodeGraphContext/CodeGraphContext/blob/a864a9f9097c0ff820c5fa8611f4056799dde8fe/src/codegraphcontext/cli/config_manager.py
16. CLI helpers — https://github.com/CodeGraphContext/CodeGraphContext/blob/a864a9f9097c0ff820c5fa8611f4056799dde8fe/src/codegraphcontext/cli/cli_helpers.py
17. CLI commands — https://github.com/CodeGraphContext/CodeGraphContext/blob/a864a9f9097c0ff820c5fa8611f4056799dde8fe/src/codegraphcontext/cli/main.py
18. MCP server — https://github.com/CodeGraphContext/CodeGraphContext/blob/a864a9f9097c0ff820c5fa8611f4056799dde8fe/src/codegraphcontext/server.py
19. MCP tool definitions — https://github.com/CodeGraphContext/CodeGraphContext/blob/a864a9f9097c0ff820c5fa8611f4056799dde8fe/src/codegraphcontext/tool_definitions.py
20. Indexing handlers — https://github.com/CodeGraphContext/CodeGraphContext/blob/a864a9f9097c0ff820c5fa8611f4056799dde8fe/src/codegraphcontext/tools/handlers/indexing_handlers.py
21. Watcher — https://github.com/CodeGraphContext/CodeGraphContext/blob/a864a9f9097c0ff820c5fa8611f4056799dde8fe/src/codegraphcontext/core/watcher.py
22. SCIP indexer — https://github.com/CodeGraphContext/CodeGraphContext/blob/a864a9f9097c0ff820c5fa8611f4056799dde8fe/src/codegraphcontext/tools/scip_indexer.py
23. Graph builder — https://github.com/CodeGraphContext/CodeGraphContext/blob/a864a9f9097c0ff820c5fa8611f4056799dde8fe/src/codegraphcontext/tools/graph_builder.py
24. Embeddings — https://github.com/CodeGraphContext/CodeGraphContext/blob/a864a9f9097c0ff820c5fa8611f4056799dde8fe/src/codegraphcontext/tools/indexing/embeddings.py
25. Git hook manager — https://github.com/CodeGraphContext/CodeGraphContext/blob/a864a9f9097c0ff820c5fa8611f4056799dde8fe/src/codegraphcontext/cli/hook_manager.py
26. Graph writer — https://github.com/CodeGraphContext/CodeGraphContext/blob/a864a9f9097c0ff820c5fa8611f4056799dde8fe/src/codegraphcontext/tools/indexing/persistence/writer.py
27. SCIP pipeline — https://github.com/CodeGraphContext/CodeGraphContext/blob/a864a9f9097c0ff820c5fa8611f4056799dde8fe/src/codegraphcontext/tools/indexing/scip_pipeline.py
28. FalkorDB backend — https://github.com/CodeGraphContext/CodeGraphContext/blob/a864a9f9097c0ff820c5fa8611f4056799dde8fe/src/codegraphcontext/core/database_falkordb.py
29. Issue #1558 (graph_name ignored) — https://github.com/CodeGraphContext/CodeGraphContext/issues/1558
30. Issue #1633 (repo_path filter vs server cwd) — https://github.com/CodeGraphContext/CodeGraphContext/issues/1633
31. Issue #1597 (vector resolve silent no-op, 123k functions) — https://github.com/CodeGraphContext/CodeGraphContext/issues/1597
32. Contributing languages — https://github.com/CodeGraphContext/CodeGraphContext/blob/a864a9f9097c0ff820c5fa8611f4056799dde8fe/docs/docs/contributing_languages.md
33. Releases — https://github.com/CodeGraphContext/CodeGraphContext/releases
34. GCF encoder — https://github.com/CodeGraphContext/CodeGraphContext/blob/a864a9f9097c0ff820c5fa8611f4056799dde8fe/src/codegraphcontext/utils/gcf_encoder.py
