# graphify — multi-repo workspace support

Research for issue antshc/brain#129. Tool identified: PyPI package `graphifyy` (CLI `graphify`), official repo `Graphify-Labs/graphify`, branch `v8`, latest release 0.9.68 (2026-09-25) [1][2]. It matches the tool in the question: it writes `graphify-out/` with `graph.json`, `manifest.json`, and `GRAPH_REPORT.md`, and has `query` / `path` / `explain` [2].

**Verdict**

- graphify has no workspace mode or config file that lists repositories. One scan root produces one `graph.json` [2][5].
- The supported multi-repo pattern: build one graph per repo, then combine them with `graphify merge-graphs` (a one-shot file) or `graphify global add` (an incremental store in `~/.graphify`). Another option is one MCP server with a per-call `project_path` [2][7][9][10].
- In a merged graph, node ids get a `<repo>::` prefix. The only cross-repo edges are shared external-module nodes, `same_type_as` between types with the same namespace and name, and parked member `calls` for C#/Java/C++/Swift. HTTP/API edges between repos are not supported in any release; they exist only in open PR #2134 [7][8][11][12][16].
- Code is parsed locally with tree-sitter and needs no LLM or API key. Rebuilds are incremental through a content-hash cache and `manifest.json`. An LLM is needed only for docs, PDFs, and images, and optionally for community names [2][3].

## 1. One merged graph vs one graph per repo

- **Per scan root:** `graphify extract <path>`, `graphify update <path>`, and `/graphify <path>` each build one graph for one directory tree [2].
- **Per repo, then merged (supported):**
  - `graphify merge-graphs a.json b.json [...] --out merged.json` combines graphs into "one cross-repo graph" [2][9].
  - `graphify global add graphify-out/graph.json --as <tag>` registers a repo in `~/.graphify/global-graph.json`, with a manifest at `~/.graphify/global-manifest.json`. `global remove`, `global list`, and `global path` manage it, and `extract --global --as <tag>` does it in one step [2][10].
  - The skill form `/graphify <url1> <url2> ...` clones several repos, builds each, and merges them [13].
- **Id namespacing:** `prefix_graph_for_global` renames every non-external node to `<repo_tag>::<id>`, sets `repo` and `local_id` on each node, and rewrites edges and hyperedges to match [7].
  - `merge-graphs` takes the tag from the directory above `graphify-out/`. Tags that collide are widened with the parent directory name, then an index suffix [9].
  - `merge-graphs` also offsets community ids so repos don't fuse into one community (#3014) [9][15].
- **How cross-repo edges are represented:**
  - **Shared packages (external imports):** an external-module stub (for example stdlib or a third-party dependency) keeps an unprefixed global id. Both repos' import edges land on the same node [7][17].
  - **Package manifests:** within one corpus, `pyproject.toml`, `go.mod`, `pom.xml`, and `apm.yml` produce one package node per package name plus `depends_on` edges [2].
    - Across merged repos this is unverified. Open PR #3262 says it is still fixing manifest nodes that fragment or cross-link between projects [18].
  - **Shared contract types:** `link_shared_type_declarations` adds a `same_type_as` edge (INFERRED, 0.9) between type declarations that have the same namespace and name in different repos [8].
  - **Cross-repo member calls:** a `calls` edge with `context="cross_repo"` (INFERRED, 0.8) is added only when the receiver's type resolves to exactly one declaration in another repo [11].
    - Languages covered: `cpp`, `csharp`, `java`, `swift` [11].
    - C# candidates must also pass namespace/`using` visibility checks [11].
    - Parking for TypeScript/JS, Kotlin, and Objective-C is in open, unmerged PRs (#3387, #3389, #3385) [18].
  - **HTTP calls between repos:** not represented in any release.
    - Open PR #2134 (`graphify cluster`) would add declared `api_call` / `shared_resource` / `mirrored_file` links through a `cluster.json` file; it is unmerged [16].
    - ASP.NET route-template nodes are also only in open PR #3248 [18].
- **Known gap in `global add`:**
  - Issue #3100 and open PR #3578: `global add` applies neither the community offset nor `same_type_as`, unlike `merge-graphs`. The `same_type_as` call is also absent from the `global_add` excerpt of `global_graph.py` [10][15][18].
  - Issue #3433: `global add` is O(K²) in the number of repos because it loads, runs a pass over, and saves the whole store on every add [18].
- **Single-corpus alternative (scan the harness root as one graph):**
  - It works mechanically, since the walk descends into subfolders [5].
  - Symbols are then *not* repo-namespaced, and name-based resolution can bind same-named symbols across projects. Issue #3237 found 20 of 25 cross-project edges were artifacts in a 5-project monorepo [18].

## 2. How graphify is told where repositories live

- **CLI argument only.**
  - The scan root is the positional path.
  - The output directory is `--out <dir>` or `GRAPHIFY_OUT`.
  - `update` remembers its root in `graphify-out/.graphify_root`.
  - No other configuration file points at repos [2][14].
  - The skill writes `graphify-out/` to the current directory, not the scan directory [13].
- **Config files:**
  - `.graphifyrc` holds only `viz_node_limit` in releases. The `language.<ext>=` key is in open PR #3789 [14][18].
  - `.graphify_build.json`, inside `graphify-out/`, persists `--exclude` patterns and the `--no-gitignore` setting across `update`, `watch`, and hook rebuilds [14].
  - `graphify-out/.graphify_root` records the scan root [14].
- **Ignore files:**
  - `.graphifyignore` uses gitignore syntax including `!` negation.
  - `.gitignore` is read in every directory and merged with `.graphifyignore`, which is evaluated last [2].
  - `.git/info/exclude` is honored at the lowest priority [5].
  - README wording conflicts:
    - It says `.graphifyignore` "only ever excludes more" and never re-includes a `.gitignore`-excluded file [2].
    - Its own docstring and a test say a `!` negation in `.graphifyignore` *can* re-include such a file [5].
- **Ignore-file discovery:** ancestor ignore files are loaded from the scan root up to the nearest VCS root, not beyond it [5].
  - Scanning `workspace/<repoA>`, which has its own `.git`, therefore does **not** pick up the harness root's `.graphifyignore`.
  - Subdirectory ignore files below the scan root are loaded during the walk [5].
- **Directory discovery:**
  - `detect()` walks with `os.walk` and prunes noise directories. `.git/` and `node_modules/` stay out even with `--no-gitignore` [5][14].
  - Other options: `--exclude <pattern>` (persisted), `--no-gitignore`, and `--follow-symlinks` (symlinks are auto-detected) [2][14].
- **Local observation (zic-board harness, read-only):**
  - `graphify-out/.graphify_root` = `D:\_work\sources\zic-board\workspace\zerto-zic`, while `graphify-out/` sits at the harness root.
  - `.graphify_build.json` = `{"gitignore": false}`, meaning `--no-gitignore` was used.
  - The harness `.gitignore` contains `/workspace`, so a harness-root scan without `--no-gitignore` would drop every repo.
  - Only `zerto-zic` is in the manifest (5,096 entries; paths such as `main/src/...`, `aws/src/...`). `zerto-zic-fe` is absent.
  - The harness `.graphifyignore` (mtime Aug 20) is newer than the build (Aug 14). `.artifacts/**/bin/**/*.deps.json` entries appear in the manifest, so its `**/bin/` rule was not in effect for that build.

## 3. Regeneration

- **Full build:**
  - `graphify extract <path>` runs detect → AST → semantic → build → cluster → analyze → export [2][4].
  - `--force` overwrites even when the graph shrinks.
  - `--allow-partial` accepts an incomplete run. Otherwise a shrink guard refuses to overwrite a larger graph [2].
- **Incremental:**
  - `graphify update <path>` is AST-only with "no API cost" [2].
  - `extract` auto-detects a prior `manifest.json` and re-extracts only changed files [15].
  - `/graphify <path> --update` re-extracts changed docs through the LLM [2].
  - `graphify hook install` adds post-commit and post-checkout rebuilds plus a merge driver for `graph.json`. After `git pull`, you run `graphify update .` yourself [2].
  - `graphify watch <path>` rebuilds on file changes [2].
- **Manifest and cache:**
  - The cache (`graphify-out/cache/`) fingerprints every file by content hash (SHA256), so unchanged files are skipped [4].
  - The AST cache is namespaced by version (`cache/ast/<version>/`). The semantic cache is namespaced by a prompt fingerprint [15].
  - `manifest.json` holds a relative path key → `mtime`, `ast_hash`, and `semantic_hash` per file. It is portable across clones [2].
  - Issue #1964 (still open) reported absolute keys. The local manifest has relative keys.
  - Local files: `cache/ast`, `cache/stat-index.json`, `.graphify_analysis.json`, `.graphify_build.json`, `.graphify_root`.
- **Multi-repo regeneration:**
  - There is no recursive or workspace update. Issue #1687 proposes `update --recursive`; today you loop over repos yourself [18].
  - `global add` skips a repo whose `graph.json` hash is unchanged [10].
  - `merge-graphs` has no incremental mode, no prune, and no hash-skip [18].
- **LLM / API key:**
  - Code-only corpora need none: "`graphify extract` runs fully offline" [2].
  - Docs, PDFs, and images need a backend when run headless:
    - Gemini (`GEMINI_API_KEY`/`GOOGLE_API_KEY`), Kimi (`MOONSHOT_API_KEY`), Claude (`ANTHROPIC_API_KEY`), OpenAI (`OPENAI_API_KEY`), DeepSeek, Azure OpenAI, Bedrock (IAM), Ollama (local), and `claude-cli` (Claude subscription) [2].
    - Auto-detect priority: Gemini → Kimi → Claude → OpenAI → DeepSeek → Azure → Bedrock → Ollama [2].
  - `--code-only` skips docs [2].
  - Inside an IDE skill run, the IDE session's model is used and no key is needed [2].
  - `cluster-only` names communities with the configured backend; `--no-label` avoids that [2].
- **Cost and time:**
  - Graph-build LLM credits are 0 for code [2].
  - Parallel AST extraction ran about 1.66× faster than sequential on 84 files [4].
  - No official wall-clock figure exists for large C# corpora (unverified).
  - The local 22,576-node / 61,942-edge graph reports "Token cost: 0 input · 0 output".

## 4. Query surface for an agent

- **CLI:**
  - `graphify query "<question>"` (flags `--dfs`, `--budget N`, `--graph <path>`) [2].
  - `graphify path "A" "B"` and `graphify explain "X"` [2].
  - `graphify affected <seed>` gives blast radius [15].
  - `graphify god-nodes` [15].
  - Output is plain text on stdout. A query names the graph it opened and shows a truncation notice at the top [15].
  - `explain` accepts `<repo>::<id>` ids from merged graphs [7].
- **MCP server:**
  - Start it with `python -m graphify.serve graphify-out/graph.json` or `graphify-mcp`. It needs the `graphifyy[mcp]` extra [2][15].
  - Transport is stdio by default. `--transport http` adds `--host`, `--port`, `--api-key`, `--path`, `--stateless`, and `--json-response` [2].
  - Tools: `query_graph`, `get_node`, `get_neighbors`, `get_community`, `god_nodes`, `graph_stats`, `shortest_path`, `list_prs`, `get_pr_impact`, `triage_prs` [2][13].
  - Resources: `graphify://report`, `stats`, `god-nodes`, `surprises`, `audit` [6].
  - **Multi-project:** every tool accepts an optional absolute `project_path`, which resolves to `<project_path>/<GRAPHIFY_OUT>/graph.json` [6].
    - One server can serve many repos: one pinned default graph plus an LRU of `GRAPHIFY_MAX_CONTEXTS` (default 8) others [6].
    - A server started without a default graph runs as a pure multi-project server [6].
  - Per-repo graphs stay separate under `project_path`; there is no cross-graph traversal.
- **Output formats:**
  - `graph.json`: NetworkX node-link data. Nodes have `id`, `label`, `file_type`, `source_file`, and `community`; edges have `relation`, `confidence` (EXTRACTED / INFERRED / AMBIGUOUS), and `confidence_score` [4].
  - `GRAPH_REPORT.md` and `graph.html` [2].
  - Exports: `--obsidian`, `--wiki`, `--svg`, `--graphml`, `--neo4j` / `--neo4j-push`, `--falkordb`, and `export callflow-html` [2].
- **Always-on agent guidance:**
  - `graphify copilot install` (Copilot CLI) and `graphify vscode install` (VS Code Copilot Chat) set up guidance [2].
  - `graphify install --project` installs the skill into the repo [2].

## 5. Install and runtime prerequisites

- **Package and runtime:**
  - Package: `graphifyy` (double y); the command is `graphify`. Other `graphify*` PyPI packages are not affiliated [2].
  - Python `>=3.10` [1]. CI runs 3.10, 3.12, 3.13, and 3.14 [2].
  - License: Apache-2.0 [1].
- **Official install commands [2]:**
  ```bash
  uv tool install graphifyy      # recommended
  pipx install graphifyy         # alternative
  pip install graphifyy          # may need PATH setup
  graphify install               # register skill with assistant (--project for repo-scoped)
  uvx --from graphifyy graphify install   # no-install form
  python3 -m venv .venv && .venv/bin/pip install "graphifyy[mcp]"   # WSL/Linux note
  ```
- **Core dependencies [1]:**
  - `networkx>=3.4`, `numpy`, `rapidfuzz`, and `tomli` (<3.11).
  - `tree-sitter<0.26,>=0.23` and bundled grammars, including `tree-sitter-c-sharp<0.25,>=0.23`, `tree-sitter-typescript<0.25,>=0.23`, and `tree-sitter-javascript<0.26,>=0.23`.
- **Extras [1][2]:**
  - `mcp` (mcp + starlette), `leiden` (graspologic / graspologic-native), `pdf`, `office`, `google`, `video`, `svg`, `neo4j`, `falkordb`, `postgres`.
  - Backends: `anthropic`, `openai`, `gemini`, `kimi`, `ollama`, `bedrock`.
  - Languages: `sql`, `terraform`, `pascal`, `dm`, `ocaml`, `commonlisp`, `robot`, `vbnet`, `r`, `erlang`, `solidity`.
  - Also `chinese` and `all`.

## 6. Language support and known limits (C#/.NET, TS/JS, large and multi-repo)

- **C#/.NET:**
  - Grammar: `.cs`. Structural parsing covers `.sln`, `.slnx`, `.csproj`, `.fsproj`, `.vbproj`, `.xaml`, `.razor`, and `.cshtml` [2][17].
  - Resolution is namespace/`using`-aware for type references [15].
  - Member calls on a receiver are typed through fields, parameters, locals, `this`, and `base` [15].
  - Other constructs handled: partial classes, keyed by assembly [15]; generic call arguments [15]; primary constructors [15]; single-implementer interface dispatch via `dispatches_to` [15]; `new Foo()` producing `calls` [15].
  - **Known limits:**
    - The bundled `tree-sitter-c-sharp` 0.23.5 cannot parse C# 14 `extension` blocks (#3510, open PR #3523) [18].
    - A verbatim interpolated string ending in `""` drops the members after it (open PR #3612) [18].
    - `DbSet` / member-access reads link no edge (open PR #3538) [18].
    - ASP.NET routes are not captured (open PR #3248) [18].
    - Constructors as nodes: PRs #3016 and #3247 are open, so this is unverified whether it has landed [18].
- **TypeScript/JavaScript:**
  - Extensions: `.ts`, `.tsx`, `.mts`, `.cts`, `.js`, `.jsx`, `.mjs`, `.cjs`, `.vue`, `.svelte`, `.astro` [2].
  - Resolves tsconfig `paths` / `baseUrl`, with wildcard and fallback targets [15].
  - Resolves package.json `exports` maps, `export *` barrels, CommonJS `require`, and dynamic `import()` [15].
  - Cross-file `calls` require import evidence (0.9.7) [15].
  - **Known limits:**
    - `${configDir}` in tsconfig `paths` is unresolved (#2340) [18].
    - pnpm-workspace package resolution is an open request (#462) [18].
    - TS cross-repo member-call parking is unmerged (#3387) [18].
- **Large or multi-repo corpora:**
  - `graph.json` has a 512 MiB cap, overridable with `GRAPHIFY_MAX_GRAPH_BYTES` [2].
  - HTML output is impractical above 5,000 nodes; use `--no-viz` [2].
  - The git merge driver aborts above 100k merged nodes or 50 MB input [9].
  - Cross-project name collisions happen in single-corpus scans (#3237) [18].
  - Hub-heavy query seeding happens on wide multi-root corpora (#569). The documented workarounds are a narrower scan root, `.graphifyignore`, and `merge-graphs` [18].
  - `global add` has the quadratic cost and missing type links described in section 1 (#3433, #3100) [18].
  - Issue #2702 asks for smaller projections of a large monorepo graph (~52 MB, 36k nodes) [18].
  - Local reference point: one C# repo (zerto-zic) → 22,576 nodes, 61,942 edges, 717 communities, 56 MB `graph.json`.

## Open questions for the experiment

1. Does `graphify extract .` at the harness root with `--no-gitignore` produce a usable single graph? Check node count, false cross-repo edges, and time.
2. How does that compare with per-repo `extract` followed by `merge-graphs`?
3. Does `merge-graphs` on a C# backend graph plus a TS frontend graph produce any `same_type_as` or `cross_repo` `calls` edges? The expectation is none across languages; confirm it.
4. How long do a cold `graphify extract --code-only` and a warm `graphify update` take on `zerto-zic` and `zerto-zic-fe`, and what is the peak memory?
5. Can one MCP server with `project_path` answer queries against both repos from VS Code Copilot? How do agents behave with it?
6. When scanning `workspace/<repo>`, is the harness `.graphifyignore` actually ignored? Code says yes (the VCS-root ceiling).
7. When scanning the harness root, which files are dropped because git-tracked exemptions are computed only for the scan root's VCS root and not for nested repos? This is inferred from code and unverified.
8. What happens to `graph.json` when the output lives in the harness while its scan root is inside `workspace/`? Check hook and `update` behavior.
9. With a merged graph served through MCP, do `explain` and `path` over `<repo>::` ids work end-to-end?
10. Does the `global add` path still lack `same_type_as` edges in the installed version (PR #3578)?

## Sources

1. PyPI JSON metadata, graphifyy 0.9.68 (requires_python, requires_dist, extras, project_urls) — https://pypi.org/pypi/graphifyy/json
2. README (v8): Install, Prerequisites, Ignoring files, Team setup / Recommended workflow, Using the graph directly, Environment variables, Privacy, Troubleshooting, Full command reference — https://github.com/Graphify-Labs/graphify/blob/v8/README.md
3. ARCHITECTURE.md (pipeline, module table, extraction schema) — https://github.com/Graphify-Labs/graphify/blob/v8/ARCHITECTURE.md
4. docs/how-it-works.md (three passes, SHA256 cache, parallel extraction, graph format) — https://github.com/Graphify-Labs/graphify/blob/v8/docs/how-it-works.md
5. detect.py `_load_graphifyignore` / `_load_dir_own_ignore` / `detect` / `_git_info_exclude` — https://github.com/Graphify-Labs/graphify/blob/v8/graphify/detect.py#L1252-L1321 ; tests `test_graphifyignore_stops_at_git_boundary`, `test_graphifyignore_discovered_from_parent_in_vcs` — https://github.com/Graphify-Labs/graphify/blob/v8/tests/test_detect.py#L343-L413
6. serve.py `_max_server_contexts`, `_GraphContextCache`, `project_path` injection, `_resolve_graph_path`, resources — https://github.com/Graphify-Labs/graphify/blob/v8/graphify/serve.py#L103-L180 , https://github.com/Graphify-Labs/graphify/blob/v8/graphify/serve.py#L1828-L1872 , https://github.com/Graphify-Labs/graphify/blob/v8/graphify/serve.py#L2004-L2033 , https://github.com/Graphify-Labs/graphify/blob/v8/graphify/serve.py#L2291-L2299
7. build.py `prefix_graph_for_global`, `distinct_repo_tags`, `_mint_external_stub` — https://github.com/Graphify-Labs/graphify/blob/v8/graphify/build.py#L2363-L2441 , https://github.com/Graphify-Labs/graphify/blob/v8/graphify/build.py#L80-L100 ; tests/test_serve.py `test_find_node_matches_merge_graphs_namespaced_node_id` — https://github.com/Graphify-Labs/graphify/blob/v8/tests/test_serve.py#L249-L266
8. cross_repo_types.py `link_shared_type_declarations` — https://github.com/Graphify-Labs/graphify/blob/v8/graphify/cross_repo_types.py
9. cli.py `merge-graphs` and `merge-driver` handlers — https://github.com/Graphify-Labs/graphify/blob/v8/graphify/cli.py#L2564-L2733
10. global_graph.py `global_add` / `global_remove` — https://github.com/Graphify-Labs/graphify/blob/v8/graphify/global_graph.py
11. cross_repo_calls.py `_LANG_SUFFIXES`, `link_cross_repo_member_calls` — https://github.com/Graphify-Labs/graphify/blob/v8/graphify/cross_repo_calls.py
12. tests/test_cross_repo_member_calls.py, tests/test_cross_repo_shared_types.py, tests/test_global_graph.py — https://github.com/Graphify-Labs/graphify/tree/v8/tests
13. Generated skill usage and MCP exports reference — https://github.com/Graphify-Labs/graphify/blob/v8/tools/skillgen/expected/graphify__skill-copilot.md , https://github.com/Graphify-Labs/graphify/blob/v8/graphify/skills/claude/references/exports.md
14. CHANGELOG 0.9.16 (`.graphify_build.json` persists `--exclude`), 0.9.19 (`--no-gitignore`), 0.9.44 (`.graphifyrc` `viz_node_limit`), 0.5.5 (`.graphify_root`) — https://github.com/Graphify-Labs/graphify/blob/v8/CHANGELOG.md
15. CHANGELOG entries 0.7.5 (incremental extract), 0.7.7 (global graph), 0.8.36 (`graphify-mcp`), 0.8.38 (versioned AST cache), 0.9.5 (multi-project MCP), 0.9.7 (JS/TS import-gated calls), 0.9.11 (distinct repo tags), 0.9.49 (`same_type_as`), 0.9.50 (community offset), 0.9.54 (cross-repo member calls), 0.9.62 (C# `using` scoping in merge) — https://github.com/Graphify-Labs/graphify/blob/v8/CHANGELOG.md
16. PR #2134 "cluster graphs — link multiple repos into one connected graph" (open) — https://github.com/Graphify-Labs/graphify/pull/2134
17. tests/test_dotnet.py (.sln/.csproj/.xaml/.razor), tests/test_external_stub_endpoints.py — https://github.com/Graphify-Labs/graphify/blob/v8/tests/test_dotnet.py , https://github.com/Graphify-Labs/graphify/blob/v8/tests/test_external_stub_endpoints.py#L79-L96
18. Issues/PRs: #1177 https://github.com/Graphify-Labs/graphify/issues/1177 ; #1687 https://github.com/Graphify-Labs/graphify/issues/1687 ; #1964 https://github.com/Graphify-Labs/graphify/issues/1964 ; #2340 https://github.com/Graphify-Labs/graphify/issues/2340 ; #2702 https://github.com/Graphify-Labs/graphify/issues/2702 ; #2703 https://github.com/Graphify-Labs/graphify/issues/2703 ; #3100 https://github.com/Graphify-Labs/graphify/issues/3100 ; #3237 https://github.com/Graphify-Labs/graphify/issues/3237 ; #3433 https://github.com/Graphify-Labs/graphify/issues/3433 ; #3510 https://github.com/Graphify-Labs/graphify/issues/3510 ; #462 https://github.com/Graphify-Labs/graphify/issues/462 ; #569 https://github.com/Graphify-Labs/graphify/issues/569 ; PRs #3248, #3262, #3385, #3387, #3389, #3523, #3538, #3578, #3612, #3789, #3016, #3247 — https://github.com/Graphify-Labs/graphify/pulls
