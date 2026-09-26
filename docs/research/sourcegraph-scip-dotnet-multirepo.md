# Sourcegraph + scip-dotnet — multi-repo workspace support

## Verdict

Sourcegraph's precise-code-nav model is **one SCIP index per repository per commit**, uploaded separately via `src code-intel upload`; cross-repo "go to definition"/"find references" is done by the backend correlating symbol monikers between separately-uploaded indexes, not by merging index files, and it only works across repos registered and indexed **on the same Sourcegraph instance**. For a harness folder containing several independent git repos as subfolders, there is no native "workspace" concept on either side: Sourcegraph registers/indexes repos one at a time (via code-host connections or a generic git-URL list), and `scip-dotnet` indexes one MSBuild solution/working-directory at a time with no repo-boundary awareness. Making cross-repo C# navigation actually work additionally requires generating each repo's index with `--allow-global-symbol-definitions` (default is off, i.e. symbols are index-local by default). None of the steps require an LLM or API key — indexing is Roslyn/MSBuild-based and upload only needs a Sourcegraph access token.

## 1. Merged vs per-repo index, and cross-repo reference representation

- Precise Code Navigation is described as using "compile-time information to provide users with accurate cross-repository navigation experience across the entire code base," distinct from search-based navigation ([Code Navigation](https://sourcegraph.com/docs/code-search/code-navigation)).
- The upload unit is per-repository, per-commit: `src code-intel upload` takes `-repo`, `-commit`, `-root`, and `-file` (path to one `.scip` file), and by default `-repo`/`-commit` are derived from the git metadata of the directory you run it in ([`src code-intel upload` reference](https://sourcegraph.com/docs/cli/references/code-intel/upload)). There is no "upload a graph covering N repos" mode — one index file is associated with one repo+commit.
- Cross-repo "Find references"/"Go to definition" is a backend feature of the precise-code-intel service: it lists "all references, definitions, and implementations found for both precise and search-based results," across repos, when precise data is available for the involved repos ([Code Navigation Features](https://sourcegraph.com/docs/code-search/code-navigation/features)).
- **Requirement to be on the same instance**: cross-repo resolution is a property of the Sourcegraph *instance's* codeintel database correlating uploads; nothing in the docs describes cross-instance correlation, so all repos needing to be linked must have their indexes uploaded to the same Sourcegraph deployment. (This inference is not stated as a single explicit sentence in the docs; treat the "same instance" requirement as strongly implied but **unverified as an explicit doc statement**.)
- For `scip-dotnet` specifically, cross-index symbol visibility is gated by an indexer flag, not automatic: `--allow-global-symbol-definitions` — "If enabled, allow public symbol definitions to be accessible from other SCIP indexes. If disabled, then public symbols will only be visible within the index" (default `false`) ([`Program.cs`](https://github.com/sourcegraph/scip-dotnet/blob/main/ScipDotnet/Program.cs)). So even with all repos on one instance, cross-repo C# nav requires re-generating each repo's index with this flag set.
- A single `scip-dotnet index` invocation *can* technically be pointed at multiple `.sln`/`.slnx`/`.csproj`/`.vbproj` paths in one call (the `projects` argument has `ArgumentArity.ZeroOrMore`) and writes one `index.scip` with one `ProjectRoot` from `--working-directory` ([`IndexCommandHandler.cs`](https://github.com/sourcegraph/scip-dotnet/blob/main/ScipDotnet/IndexCommandHandler.cs)). Nothing in the tool is aware of git repository boundaries — it only sees MSBuild projects. Whether a single merged index spanning `harness/workspace/repoA` + `repoB` uploads cleanly to Sourcegraph (which expects one `-repo`/one 40-char `-commit` per upload) is not documented — see Open questions.

## 2. Telling Sourcegraph where repos live, and telling scip-dotnet what to index

- Repositories are added to Sourcegraph either via **code host connections** (GitHub, GitLab, Bitbucket Cloud/Server/Data Center, Perforce) configured under Site admin, or, for hosts without a first-class connector, via the **generic "Other" Git host** connection, which lists explicit git clone URLs ([Add repositories](https://sourcegraph.com/docs/admin/repo/add), [Other Git repository hosts](https://sourcegraph.com/docs/admin/code-hosts/other)).
- The generic connector's schema takes a flat `repos` array of repo path strings plus a base `url` and a `repositoryPathPattern` template — e.g. `"repos": ["gorilla/mux", "sourcegraph/sourcegraph"]` — each entry becomes one Sourcegraph repository ([Other Git repository hosts config](https://sourcegraph.com/docs/admin/code-hosts/other)). This is registration by **individual repo**, not by folder/workspace; you could list `harness`, `repoA`, `repoB` as three separate entries in one connection's `repos` array, but each still becomes a distinct Sourcegraph repository with its own clone/index lifecycle.
- `src-cli` is not used to *register* repositories with Sourcegraph — repo registration is via the site-admin code-host/external-service configuration above; `src-cli`'s repo-scoped commands are for code-intel upload/querying against already-registered repos ([`src code-intel upload`](https://sourcegraph.com/docs/cli/references/code-intel/upload)).
- `scip-dotnet` has **no workspace-level configuration**. It is invoked per solution/project: `scip-dotnet index [projects...]`, where `projects` is zero or more paths to `.sln`/`.slnx`/`.csproj`/`.vbproj`; if omitted, it auto-discovers a single solution/project file in `--working-directory` (`FindSolutionOrProjectFile`, which errors if none/multiple ambiguous files are found) ([`IndexCommandHandler.cs`](https://github.com/sourcegraph/scip-dotnet/blob/main/ScipDotnet/IndexCommandHandler.cs), [`Program.cs`](https://github.com/sourcegraph/scip-dotnet/blob/main/ScipDotnet/Program.cs)). There is no `.sourcegraph.yaml`-equivalent or multi-repo manifest read by `scip-dotnet` itself.
- Sourcegraph does have a repo-content-driven config for *auto-indexing* (`sourcegraph.yaml` committed to a repo root, or per-repo UI config), but this is Sourcegraph's own auto-indexing/executors feature, is per single repository, and its language coverage for auto-indexing is currently "Go, TypeScript, JavaScript, Python, Ruby and JVM" — **C#/scip-dotnet is not in the auto-indexing inference list** as of this doc, so scip-dotnet must be run manually/in CI, not via Sourcegraph auto-indexing inference ([Auto-indexing](https://sourcegraph.com/docs/code-search/code-navigation/auto_indexing)).

## 3. Regeneration: full vs incremental, cost/time, and no LLM/API-key dependency

- No incremental/partial SCIP generation mode is documented or present in `scip-dotnet`'s CLI surface (`index`, `--include`/`--exclude` glob filters, `--skip-dotnet-restore`, `--nuget-config-path`, `--dotnet-restore-timeout`, `--allow-global-symbol-definitions` — no `--since`/`--changed-files` style flag) ([`Program.cs`](https://github.com/sourcegraph/scip-dotnet/blob/main/ScipDotnet/Program.cs)). Each run re-analyzes the whole solution via Roslyn/MSBuild; this is a **full reindex** model.
- Sourcegraph's own guidance for SCIP-based (non-auto-indexed) setups is to run indexing in CI "on every commit (including branches)," falling back to indexing only the default branch or a periodic (e.g. daily) job if CI/disk load is too high; unindexed commits within 100 commits of an indexed one still get precise nav for unchanged lines ([Adding precise code navigation to CI/CD workflows](https://sourcegraph.com/docs/code-search/code-navigation/how-to/adding_scip_to_workflows)).
- No cost/time benchmarks for `scip-dotnet` on any repo size are published in the README, releases, or docs pages fetched — **unverified**.
- Neither indexing (`scip-dotnet index`, Roslyn/MSBuild-based) nor upload (`src code-intel upload`) requires an LLM or LLM API key. Upload authenticates with a Sourcegraph **access token** (`SRC_ACCESS_TOKEN`) and optionally a GitHub/GitLab token used only to verify repo access permissions, not for any AI feature ([scip-dotnet README](https://github.com/sourcegraph/scip-dotnet), [`src code-intel upload`](https://sourcegraph.com/docs/cli/references/code-intel/upload)).

## 4. Query surface for an agent

- **GraphQL API**: exists but is explicitly documented as a "debug API... intended primarily for debugging use cases," with **no backwards-compatibility guarantee across releases**; Sourcegraph recommends the Stream Search API instead for code-search integrations ([Sourcegraph GraphQL debug API](https://sourcegraph.com/docs/api/graphql)). It supports token or OAuth auth, has a console at `/debug/console`, and configurable cost limits (`graphQLMaxDepth`, `graphQLMaxFieldCount`, etc.).
- **`src-cli`**: `src code-intel upload` (index upload) and generic `src api` (send arbitrary GraphQL queries, with a `-get-curl` flag to emit an equivalent curl command) ([Sourcegraph GraphQL debug API](https://sourcegraph.com/docs/api/graphql)).
- No official Sourcegraph **MCP server** page was found at the URLs checked (`/docs/cody/overview/mcp`, `/docs/cody/clients/model-context-protocol`, `/docs/mcp`, `/docs/amp` all 404'd) — **unverified / not found in the official docs surface searched**; do not assume one exists without further, targeted search.
- Output/query shapes: precise-code-intel results (hover, definitions, references, implementations) are exposed to users through the web UI and code-host/browser-extension integrations, and programmatically only through the debug GraphQL API noted above ([Code Navigation Features](https://sourcegraph.com/docs/code-search/code-navigation/features)).

## 5. Install and runtime prerequisites

**Sourcegraph server**, in order of recommendation ([Deployment Overview](https://sourcegraph.com/docs/self-hosted/deploy)):
1. Sourcegraph Cloud (managed, not self-hosted).
2. Kubernetes via Helm — "most robust, scalable, and vetted self-hosted solution," multi-node.
3. Docker Compose — "the preferred single-node deployment solution."

"Docker Compose is our only supported single-node self-hosted deployment type" ([Single-Node](https://sourcegraph.com/docs/self-hosted/deploy/single-node)) — the older single-container `sourcegraph/server` Docker image path returned a 404 on the docs URL checked, consistent with it no longer being a current documented option.

Docker Compose install ([Docker Compose](https://sourcegraph.com/docs/self-hosted/deploy/docker-compose)):
- Prerequisites: Docker Compose ≥ v20.10.0 engine / ≥ v1.29.0 compose, Docker Swarm not supported, a Sourcegraph license (required for >10 users), ARM/ARM64 and Windows not supported for production.
- Steps: fork/clone [`sourcegraph/deploy-sourcegraph-docker`](https://github.com/sourcegraph/deploy-sourcegraph-docker/), check out a `release` branch at the desired `$SOURCEGRAPH_VERSION` tag, customize via `docker-compose.override.yaml`, then:
  ```bash
  cd docker-compose
  docker compose up -d
  ```

**`scip-dotnet` install** ([scip-dotnet README](https://github.com/sourcegraph/scip-dotnet)):
- Docker: `docker run -v $(pwd):/app sourcegraph/scip-dotnet:latest scip-dotnet index`
- Local dotnet tool: install **.NET 8.0** ([dotnet.microsoft.com](https://dotnet.microsoft.com/en-us/download)), then:
  ```bash
  dotnet tool install --global scip-dotnet
  scip-dotnet --version
  cd PATH_TO_CSHARP_PROJECT
  scip-dotnet index
  ```
  (Update with `dotnet tool update --global scip-dotnet`.)
- Note: the repo's own build tooling (`global.json`, CI) was bumped to **.NET SDK 10** for *building scip-dotnet from source* per recent releases ("Updated .NET SDK to version 10 (#98)", [v0.2.14 release notes](https://github.com/sourcegraph/scip-dotnet/releases)) — this is the SDK used to compile the indexer itself, separate from the README's stated **.NET 8.0** runtime requirement for *installing/running* the published tool. Treat the exact minimum runtime as **worth re-verifying** at experiment time given this discrepancy.
- Upload tool: `npm install -g @sourcegraph/src`, then `SRC_ACCESS_TOKEN`/`SRC_ENDPOINT` env vars, then `src code-intel upload`.

## 6. Language support and known limits (C#/.NET, TypeScript/JavaScript) in multi-repo/multi-solution setups

**C#/VB via `scip-dotnet`:**
- Status: 🟢 Generally available for "C#, Visual Basic" ([Precise Code Navigation — supported languages](https://sourcegraph.com/docs/code-search/code-navigation/precise_code_navigation)).
- Built on Roslyn via `MSBuildWorkspace`/`MSBuildLocator`; supports `.sln`, `.slnx` (added recently, PR [#112](https://github.com/sourcegraph/scip-dotnet/pull/112)), `.csproj`, `.vbproj`.
- Runs `dotnet restore` before indexing by default (configurable timeout, or skippable with `--skip-dotnet-restore` if restore already ran, with `--nuget-config-path` override) — this means indexing a repo requires its NuGet dependencies to be resolvable, which matters if `repoA`/`repoB` in a workspace reference each other only as source (`ProjectReference`) vs. as built NuGet packages (`PackageReference`); no documentation addresses this multi-repo case directly.
- Cross-index/cross-repo symbol visibility requires `--allow-global-symbol-definitions` on each index (off by default) ([`Program.cs`](https://github.com/sourcegraph/scip-dotnet/blob/main/ScipDotnet/Program.cs)).
- Known open issues (small maintenance surface, 4 open / 8 closed at time of writing): "Symbol doesn't contain full namespace name" (open, [#85](https://github.com/sourcegraph/scip-dotnet/issues/85)); a maintenance-help request (open, [#118](https://github.com/sourcegraph/scip-dotnet/issues/118)); SLNX support request (closed via #112) ([Issues](https://github.com/sourcegraph/scip-dotnet/issues)). No documented monorepo-scale performance numbers.

**TypeScript/JavaScript via `scip-typescript`:**
- Status: 🟢 Generally available ([Precise Code Navigation — supported languages](https://sourcegraph.com/docs/code-search/code-navigation/precise_code_navigation)).
- Install: `npm install -g @sourcegraph/scip-typescript`; supports Node v22 and v24 currently.
- Has first-class flags for **package-manager workspaces within one repo**: `scip-typescript index --yarn-workspaces` and `--pnpm-workspaces`, and `--infer-tsconfig` for plain JS projects — but these address multi-package monorepos under one `package.json`/one git repo, **not** multiple independent git repositories checked out as siblings under one folder ([scip-typescript README](https://github.com/sourcegraph/scip-typescript)).
- Known limitation: out-of-memory errors on large codebases, with documented mitigations `--no-global-caches` (disables cross-project symbol cache, trades memory for speed) and increasing Node's heap via `--max-old-space-size` ([scip-typescript README](https://github.com/sourcegraph/scip-typescript)).
- Auto-indexing inference (Sourcegraph-managed, executor-based) exists for TypeScript/JavaScript (keyed off `tsconfig.json`, with dependency install steps per ancestor `package.json`), unlike C# ([Auto-indexing inference](https://sourcegraph.com/docs/code-search/code-navigation/auto_indexing)).
- Neither indexer documents a mode for indexing "a harness folder containing several independent git repos" as a single unit; each independent git repo is expected to be indexed and uploaded on its own.

## Open questions for the experiment

- Does uploading one merged `index.scip` (built by pointing `scip-dotnet` at project files spanning `harness/workspace/repoA` and `repoB` in a single invocation) even accept an upload, given `src code-intel upload` expects one `-repo`/one 40-char `-commit`, and `repoA`/`repoB` have independent commit histories?
- With `--allow-global-symbol-definitions` set on both repos' indexes and both uploaded to the same instance, does "Find references" in the web UI actually surface hits in the sibling repo for a plain `ProjectReference` (source-level) dependency, or only for symbols resolved through a built/published NuGet package?
- Does `dotnet restore` succeed unmodified when `repoB`'s projects are referenced by path from `repoA`'s solution but `repoB` is a sibling git checkout rather than a NuGet-restored dependency?
- What is the actual indexing wall-clock time and `index.scip` file size for a harness-sized multi-repo solution (no published benchmarks found)?
- Is there an unofficial/community MCP server wrapping Sourcegraph's GraphQL or Stream Search API that an agent could use, given no official one was found?
- Does the "same Sourcegraph instance" requirement for cross-repo nav hold as stated, or are there any explicit doc/source statements confirming or narrowing it (only inferred here from architecture, not from one explicit sentence)?
- What is the true minimum .NET runtime for the installed `scip-dotnet` tool given the README says .NET 8.0 but recent releases moved the repo's own build SDK to .NET 10?

## Sources

1. https://sourcegraph.com/docs/code-search/code-navigation/precise_code_navigation
2. https://sourcegraph.com/docs/code-search/code-navigation/features
3. https://sourcegraph.com/docs/code-search/code-navigation
4. https://sourcegraph.com/docs/code-search/code-navigation/auto_indexing
5. https://sourcegraph.com/docs/code-search/code-navigation/how-to/adding_scip_to_workflows
6. https://sourcegraph.com/docs/cli/references/code-intel/upload
7. https://github.com/sourcegraph/scip-dotnet
8. https://github.com/sourcegraph/scip-dotnet/blob/main/ScipDotnet/Program.cs
9. https://github.com/sourcegraph/scip-dotnet/blob/main/ScipDotnet/IndexCommandHandler.cs
10. https://github.com/sourcegraph/scip-dotnet/releases
11. https://github.com/sourcegraph/scip-dotnet/issues
12. https://github.com/sourcegraph/scip-typescript
13. https://sourcegraph.com/docs/admin/repo/add
14. https://sourcegraph.com/docs/admin/code-hosts/other
15. https://sourcegraph.com/docs/api/graphql
16. https://sourcegraph.com/docs/self-hosted/deploy
17. https://sourcegraph.com/docs/self-hosted/deploy/single-node
18. https://sourcegraph.com/docs/self-hosted/deploy/docker-compose
19. https://sourcegraph.com/docs/admin/executors
